from __future__ import annotations

import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from lattice.schemas import (
    AgenticExecutionPlan,
    ArtifactManifest,
    Provenance,
    RunRecord,
    RuntimeGraphContext,
    ScriptExecutionRawResult,
    ScriptProposal,
    ScriptReviewResult,
)

BLOCKED_SCRIPT_MARKERS = (
    "Remove-Item",
    "rm -rf",
    "git reset --hard",
    "git clean",
    "format ",
    "Invoke-WebRequest",
    "curl ",
    "wget ",
)


class ScriptGenerationAgent:
    def generate(
        self,
        *,
        request: str,
        plan: AgenticExecutionPlan,
        runtime_context: RuntimeGraphContext,
    ) -> ScriptProposal:
        skill_ids = sorted({skill_id for step in plan.steps for skill_id in step.skill_ids})
        tool_names = sorted({tool for step in plan.steps for tool in step.suggested_tool_names})
        step_lines = [
            f"{index}. {step.script_goal or step.workflow_step_id}"
            for index, step in enumerate(plan.steps, start=1)
        ]
        script_text = "\n".join(
            [
                "from __future__ import annotations",
                "",
                "def main() -> None:",
                f"    request = {request!r}",
                f"    plan_id = {plan.plan_id!r}",
                f"    referenced_skill_ids = {skill_ids!r}",
                f"    suggested_tool_names = {tool_names!r}",
                f"    planned_steps = {step_lines!r}",
                "    print('LATTICE script proposal executed')",
                "    print({'request': request, 'plan_id': plan_id, 'steps': planned_steps, "
                "'skills': referenced_skill_ids, 'tools': suggested_tool_names})",
                "",
                "if __name__ == '__main__':",
                "    main()",
                "",
            ]
        )
        return ScriptProposal(
            proposal_id=f"script-{uuid4()}",
            plan_id=plan.plan_id,
            script_text=script_text,
            intended_actions=[
                "compose executable script from L2 workflow reference and L5 skill context",
                "preserve missing capability room for runtime discovery",
            ],
            referenced_skill_ids=skill_ids,
            suggested_tool_names=tool_names,
            expected_artifacts=[
                artifact
                for step in plan.steps
                for artifact in step.artifact_expectations
            ],
            permission_requirements={
                "network": False,
                "shell": False,
                "write_workspace": False,
                "runtime_context_id": runtime_context.graph_context_id,
            },
            provenance=[Provenance(source_type="script_generation_agent")],
        )


class ScriptReviewAgent:
    def review(self, proposal: ScriptProposal) -> ScriptReviewResult:
        blockers = [
            f"blocked marker found in generated script: {marker}"
            for marker in BLOCKED_SCRIPT_MARKERS
            if marker.lower() in proposal.script_text.lower()
        ]
        warnings: list[str] = []
        if not proposal.referenced_skill_ids:
            warnings.append("generated script has no referenced L5 skill ids")
        if proposal.language != "python":
            blockers.append(f"unsupported script language: {proposal.language}")
        status = "blocked" if blockers else "approved"
        return ScriptReviewResult(
            review_id=f"script-review-{uuid4()}",
            proposal_id=proposal.proposal_id,
            status=status,
            blockers=blockers,
            warnings=warnings,
            required_revisions=blockers,
            static_findings={
                "line_count": len(proposal.script_text.splitlines()),
                "blocked_marker_count": len(blockers),
            },
            provenance=[Provenance(source_type="script_review_agent")],
        )


class ScriptRunner:
    def run(self, proposal: ScriptProposal, *, working_dir: str | Path | None = None) -> ScriptExecutionRawResult:
        started_at = datetime.now(timezone.utc)
        run_dir_context = (
            tempfile.TemporaryDirectory(prefix="lattice-script-")
            if working_dir is None
            else None
        )
        try:
            run_dir = Path(working_dir or run_dir_context.name)  # type: ignore[union-attr]
            run_dir.mkdir(parents=True, exist_ok=True)
            script_path = run_dir / f"{proposal.proposal_id}.py"
            script_path.write_text(proposal.script_text, encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(run_dir),
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            status = "success" if completed.returncode == 0 else "failure"
            return ScriptExecutionRawResult(
                execution_id=f"script-exec-{uuid4()}",
                proposal_id=proposal.proposal_id,
                status=status,
                exit_code=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                artifact_paths=[str(script_path)],
                runtime_metadata={"working_dir": str(run_dir)},
                provenance=[Provenance(source_type="script_runner")],
            )
        finally:
            if run_dir_context is not None:
                run_dir_context.cleanup()


class RunRecordBuilder:
    def build(
        self,
        *,
        session_id: str,
        request: str,
        plan: AgenticExecutionPlan | None,
        proposal: ScriptProposal | None,
        execution: ScriptExecutionRawResult | None,
    ) -> tuple[RunRecord, ArtifactManifest]:
        provenance = [Provenance(source_type="run_record_builder")]
        manifest = ArtifactManifest(
            manifest_id=f"artifact-manifest-{uuid4()}",
            execution_id=execution.execution_id if execution is not None else "not-executed",
            artifacts=[
                {"path": path, "kind": "runtime_file"}
                for path in (execution.artifact_paths if execution is not None else [])
            ],
            provenance=provenance,
        )
        record = RunRecord(
            run_id=f"run-{uuid4()}",
            session_id=session_id,
            request=request,
            plan_id=plan.plan_id if plan is not None else None,
            proposal_id=proposal.proposal_id if proposal is not None else None,
            execution_id=execution.execution_id if execution is not None else None,
            status=execution.status if execution is not None else "skipped",
            referenced_skill_ids=proposal.referenced_skill_ids if proposal is not None else [],
            suggested_tool_names=proposal.suggested_tool_names if proposal is not None else [],
            artifact_manifest_id=manifest.manifest_id,
            summary={
                "exit_code": execution.exit_code if execution is not None else None,
                "stdout_excerpt": (execution.stdout[:1000] if execution is not None else ""),
                "stderr_excerpt": (execution.stderr[:1000] if execution is not None else ""),
            },
            provenance=provenance,
        )
        return record, manifest
