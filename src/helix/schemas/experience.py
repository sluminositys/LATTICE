from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from helix.schemas.common import HelixBaseModel, LifecycleState, Provenance


class ExperienceCandidate(HelixBaseModel):
    candidate_id: str
    candidate_type: Literal[
        "constraint",
        "repair_action",
        "preference",
        "workflow_pattern",
        "quality_signal",
    ]
    source_event_ids: list[str] = Field(default_factory=list)
    trigger_condition: dict[str, Any] = Field(default_factory=dict)
    proposed_graph_patch_id: str
    scope: Literal["user", "lab", "project", "global"]
    confidence_state: Literal["raw", "reviewed", "approved", "rejected"] = "raw"


class Constraint(HelixBaseModel):
    constraint_id: str
    type: str
    subject: str
    relation: str
    object: str
    trigger_condition: dict[str, Any] = Field(default_factory=dict)
    applies_to_layers: list[str] = Field(default_factory=list)
    severity: Literal["blocker", "warning", "info"]
    repair_hint: str
    provenance: Provenance
    lifecycle_state: LifecycleState = "candidate"


class CapabilityGap(HelixBaseModel):
    gap_id: str
    task_fingerprint_id: str
    runtime_graph_context_id: str | None = None
    gap_type: Literal["workflow", "tool", "toolcall_spec", "runtime_backend", "evidence", "data"]
    missing_requirements: list[str] = Field(default_factory=list)
    trigger_condition: dict[str, Any] = Field(default_factory=dict)
    suggested_discovery_queries: list[str] = Field(default_factory=list)
    provenance: Provenance
    lifecycle_state: LifecycleState = "candidate"
