from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from lattice.schemas.common import LatticeBaseModel, Provenance

PlanStatus = Literal["planned", "verified", "executing", "completed", "failed", "blocked"]


class AgenticExecutionStep(LatticeBaseModel):
    step_id: str
    workflow_step_id: str
    skill_ids: list[str] = Field(default_factory=list)
    suggested_tool_names: list[str] = Field(default_factory=list)
    script_goal: str | None = None
    input_bindings: dict[str, Any] = Field(default_factory=dict)
    parameter_bindings: dict[str, Any] = Field(default_factory=dict)
    parameter_sources: dict[str, Any] = Field(default_factory=dict)
    preconditions: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)
    permission_requirement: dict[str, Any] = Field(default_factory=dict)
    failure_policy: dict[str, Any] = Field(default_factory=dict)
    quality_checks: list[str] = Field(default_factory=list)
    artifact_expectations: list[str] = Field(default_factory=list)
    toolcall_spec_id: str | None = None
    observation_schema: dict[str, Any] = Field(default_factory=dict)


class AgenticExecutionPlan(LatticeBaseModel):
    plan_id: str
    task_fingerprint_id: str
    runtime_graph_context_id: str
    selected_workflow_path_id: str
    status: PlanStatus = "planned"
    steps: list[AgenticExecutionStep] = Field(default_factory=list)
    script_strategy: str | None = None
    verification_report_id: str | None = None
    provenance: list[Provenance] = Field(default_factory=list)
