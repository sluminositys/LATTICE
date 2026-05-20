from __future__ import annotations

from pydantic import Field

from helix.schemas import HelixBaseModel, PermissionMode, WorkflowAuditReport


class PermissionDecision(HelixBaseModel):
    allowed: bool
    mode: PermissionMode
    reason: str
    blocked_by: list[str] = Field(default_factory=list)


class PermissionGate:
    def check_execution(
        self,
        workflow_report: WorkflowAuditReport,
        *,
        mode: PermissionMode = "plan_only",
    ) -> PermissionDecision:
        if workflow_report.status == "blocked":
            return PermissionDecision(
                allowed=False,
                mode=mode,
                reason="workflow verification blocked execution",
                blocked_by=[blocker.code for blocker in workflow_report.blockers],
            )

        if mode == "plan_only":
            return PermissionDecision(
                allowed=False,
                mode=mode,
                reason="plan_only mode does not allow tool execution",
                blocked_by=["PLAN_ONLY_MODE"],
            )

        return PermissionDecision(
            allowed=True,
            mode=mode,
            reason="permission checks passed",
        )
