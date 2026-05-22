from __future__ import annotations

from typing import Literal
from uuid import uuid4

from lattice.planning import WorkflowSearchResult
from lattice.schemas import CapabilityGap, Provenance, RuntimeGraphContext, TaskFingerprint


class CapabilityGapDetector:
    def detect(
        self,
        *,
        fingerprint: TaskFingerprint,
        runtime_context: RuntimeGraphContext,
        workflow_search_result: WorkflowSearchResult,
    ) -> list[CapabilityGap]:
        gaps: list[CapabilityGap] = []
        unresolved = workflow_search_result.unresolved_requirements
        if not unresolved:
            return gaps

        gap_type = _classify_gap(unresolved)
        gaps.append(
            CapabilityGap(
                gap_id=f"gap-{uuid4()}",
                task_fingerprint_id=fingerprint.fingerprint_id,
                runtime_graph_context_id=runtime_context.graph_context_id,
                gap_type=gap_type,
                missing_requirements=unresolved,
                trigger_condition={
                    "task": fingerprint.task,
                    "sufficiency_status": runtime_context.sufficiency_report.status,
                },
                suggested_discovery_queries=[fingerprint.task, *unresolved[:3]],
                provenance=Provenance(source_type="capability_gap_detector"),
            )
        )
        return gaps


def _classify_gap(
    unresolved: list[str],
) -> Literal["workflow", "tool", "toolcall_spec", "runtime_backend", "evidence", "data"]:
    joined = " ".join(unresolved).lower()
    if "toolcallspec" in joined or "toolcall" in joined:
        return "toolcall_spec"
    if "tool" in joined:
        return "tool"
    if "workflow" in joined or "path" in joined:
        return "workflow"
    if "evidence" in joined:
        return "evidence"
    return "data"
