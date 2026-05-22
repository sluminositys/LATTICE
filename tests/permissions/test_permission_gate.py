from lattice.permissions import PermissionGate
from lattice.schemas import Blocker, WorkflowAuditReport


def test_permission_gate_blocks_failed_workflow_verification() -> None:
    report = WorkflowAuditReport(
        report_id="war-1",
        status="blocked",
        blockers=[Blocker(code="NO_TOOLCALL_SPEC", message="missing")],
    )

    decision = PermissionGate().check_execution(report, mode="plan_only")

    assert decision.allowed is False
    assert decision.blocked_by == ["NO_TOOLCALL_SPEC"]


def test_permission_gate_blocks_execution_in_plan_only_mode() -> None:
    report = WorkflowAuditReport(report_id="war-1", status="pass")

    decision = PermissionGate().check_execution(report, mode="plan_only")

    assert decision.allowed is False
    assert decision.blocked_by == ["PLAN_ONLY_MODE"]
