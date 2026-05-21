from helix.planning import ExitPlanGate
from helix.schemas import WorkflowAuditReport


def test_exit_plan_gate_blocks_without_aep_or_permission() -> None:
    report = ExitPlanGate().check(
        workflow_report=WorkflowAuditReport(report_id="war-1", status="pass"),
        execution_plan=None,
        parameter_source_passed=True,
        permission_passed=False,
    )

    assert report.passed is False
    assert report.blockers == ["AEP was not generated.", "PermissionGate did not pass."]
