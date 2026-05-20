from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import Field

from helix.schemas.common import HelixBaseModel, LifecycleState, Provenance


class LifecycleTransition(HelixBaseModel):
    transition_id: str
    target_node_or_edge_id: str
    from_state: LifecycleState
    to_state: LifecycleState
    reason: str
    source_event_ids: list[str] = Field(default_factory=list)
    approved_by: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GraphPatch(HelixBaseModel):
    patch_id: str
    source_event_ids: list[str] = Field(default_factory=list)
    source_module: str
    target_graph_tier: Literal["L0"] = "L0"
    nodes_to_add: list[dict[str, Any]] = Field(default_factory=list)
    edges_to_add: list[dict[str, Any]] = Field(default_factory=list)
    nodes_to_update: list[dict[str, Any]] = Field(default_factory=list)
    edges_to_update: list[dict[str, Any]] = Field(default_factory=list)
    lifecycle_transitions: list[LifecycleTransition] = Field(default_factory=list)
    provenance: Provenance
    approval_status: Literal["proposed", "approved", "rejected", "applied"] = "proposed"
    risk_level: Literal["low", "medium", "high", "critical"] = "low"
