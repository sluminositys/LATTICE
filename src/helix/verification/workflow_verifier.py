from __future__ import annotations

from uuid import uuid4

from helix.planning import WorkflowSearchResult
from helix.schemas import Blocker, WorkflowAuditReport


class WorkflowVerifier:
    def verify(self, search_result: WorkflowSearchResult) -> WorkflowAuditReport:
        blockers: list[Blocker] = []
        if search_result.selected_workflow_path_id is None:
            blockers.append(
                Blocker(
                    code="NO_WORKFLOW_PATH",
                    message="No verified workflow path is available in the runtime context.",
                )
            )

        if any("ToolCallSpec" in item for item in search_result.unresolved_requirements):
            blockers.append(
                Blocker(
                    code="NO_TOOLCALL_SPEC",
                    message="No active ToolCallSpec is registered for execution.",
                )
            )

        if blockers:
            return WorkflowAuditReport(
                report_id=f"war-{uuid4()}",
                status="blocked",
                blockers=blockers,
                unresolved_items=search_result.unresolved_requirements,
            )

        return WorkflowAuditReport(report_id=f"war-{uuid4()}", status="pass")
