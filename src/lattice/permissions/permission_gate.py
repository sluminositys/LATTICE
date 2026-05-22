from __future__ import annotations

from pydantic import Field

from lattice.schemas import LatticeBaseModel, PermissionMode, WorkflowAuditReport


class PermissionDecision(LatticeBaseModel):
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

        if mode in {"plan_only", "read_only"}:
            return PermissionDecision(
                allowed=False,
                mode=mode,
                reason=f"{mode} mode does not allow tool execution",
                blocked_by=[f"{mode.upper()}_MODE"],
            )

        if mode == "ask_before_execute":
            return PermissionDecision(
                allowed=False,
                mode=mode,
                reason="ask_before_execute requires an explicit external approval decision",
                blocked_by=["EXTERNAL_APPROVAL_REQUIRED"],
            )

        return PermissionDecision(
            allowed=True,
            mode=mode,
            reason="permission checks passed",
        )
