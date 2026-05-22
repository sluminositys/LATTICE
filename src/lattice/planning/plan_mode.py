from __future__ import annotations

from pydantic import Field

from lattice.schemas import AgenticExecutionPlan, LatticeBaseModel, WorkflowAuditReport


class ExitPlanGateReport(LatticeBaseModel):
    passed: bool
    blockers: list[str] = Field(default_factory=list)


class ExitPlanGate:
    def check(
        self,
        *,
        workflow_report: WorkflowAuditReport,
        execution_plan: AgenticExecutionPlan | None,
        parameter_source_passed: bool,
        permission_passed: bool,
    ) -> ExitPlanGateReport:
        blockers: list[str] = []
        if workflow_report.status == "blocked":
            blockers.append("WorkflowVerifier did not pass.")
        if execution_plan is None:
            blockers.append("AEP was not generated.")
        if not parameter_source_passed:
            blockers.append("ParameterSourceChecker did not pass.")
        if not permission_passed:
            blockers.append("PermissionGate did not pass.")
        return ExitPlanGateReport(passed=not blockers, blockers=blockers)
