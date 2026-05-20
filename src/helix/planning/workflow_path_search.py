from __future__ import annotations

from pydantic import Field

from helix.schemas import HelixBaseModel, RuntimeGraphContext, TaskFingerprint


class WorkflowSearchResult(HelixBaseModel):
    candidate_path_ids: list[str] = Field(default_factory=list)
    selected_workflow_path_id: str | None = None
    rejected_path_ids: list[str] = Field(default_factory=list)
    path_rationale: list[str] = Field(default_factory=list)
    unresolved_requirements: list[str] = Field(default_factory=list)


class WorkflowPathSearch:
    def search(
        self,
        fingerprint: TaskFingerprint,
        runtime_context: RuntimeGraphContext,
    ) -> WorkflowSearchResult:
        report = runtime_context.sufficiency_report
        if report.status == "insufficient":
            return WorkflowSearchResult(
                unresolved_requirements=[
                    *report.missing_task_info,
                    *report.missing_workflow_info,
                    *report.missing_toolcall_info,
                    *report.missing_evidence_info,
                    *report.missing_experience_info,
                ],
                path_rationale=[
                    "RuntimeGraphContext is insufficient; workflow path search cannot run."
                ],
            )

        return WorkflowSearchResult(
            unresolved_requirements=[
                "workflow path search strategy is not implemented for sufficient contexts"
            ],
            path_rationale=["No workflow search backend is configured."],
        )
