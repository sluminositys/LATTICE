from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from lattice.schemas.common import LatticeBaseModel, LifecycleState, Provenance

ObservationStatus = Literal["success", "failure", "partial", "cancelled"]


class ToolCallSpec(LatticeBaseModel):
    toolcall_spec_id: str
    name: str
    tool_name: str
    tool_version_policy: str
    task_tags: list[str] = Field(default_factory=list)
    method_tags: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    parameter_schema: dict[str, Any] = Field(default_factory=dict)
    preconditions: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    repair_hints: list[str] = Field(default_factory=list)
    runtime_backend: str
    permission_policy: dict[str, Any] = Field(default_factory=dict)
    parameter_source_policy: dict[str, Any] = Field(default_factory=dict)
    lifecycle_state: LifecycleState
    provenance: Provenance


class StructuredObservation(LatticeBaseModel):
    observation_id: str
    toolcall_event_id: str
    status: ObservationStatus
    outputs: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    error_class: str | None = None
    raw_artifact_refs: list[str] = Field(default_factory=list)
    parsed_summary: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance
