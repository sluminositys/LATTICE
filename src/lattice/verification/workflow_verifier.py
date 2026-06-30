from __future__ import annotations

from uuid import uuid4

from lattice.planning import WorkflowSearchResult
from lattice.schemas import Blocker, WorkflowAuditReport


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

        if any("executable steps" in item for item in search_result.unresolved_requirements):
            blockers.append(
                Blocker(
                    code="NO_EXECUTABLE_WORKFLOW_STEPS",
                    message="The selected workflow path has no executable step sequence.",
                )
            )
        remaining_unresolved = [
            item
            for item in search_result.unresolved_requirements
            if "executable steps" not in item
        ]
        if remaining_unresolved and search_result.selected_workflow_path_id is not None:
            blockers.append(
                Blocker(
                    code="UNRESOLVED_WORKFLOW_REQUIREMENTS",
                    message="Workflow path search returned unresolved requirements.",
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
