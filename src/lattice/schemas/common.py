from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LatticeBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


GraphTier = Literal["G0", "G1", "G2", "G1_plus_controlled_G0_recall"]

LifecycleState = Literal[
    "candidate",
    "probationary",
    "active_hot",
    "active_warm",
    "cold_reference",
    "deprecated_reference",
    "quarantined",
    "retired",
    "tombstoned",
]

ExecutionIntent = Literal["plan_only", "execute", "verify", "update"]

PermissionMode = Literal[
    "plan_only",
    "read_only",
    "safe_execute",
    "ask_before_execute",
    "admin_approved_execute",
    "graph_write_review",
    "headless_fail_closed",
]


class Provenance(LatticeBaseModel):
    source_type: str
    source_id: str | None = None
    source_path: str | None = None
    source_version: str | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class IdRef(LatticeBaseModel):
    id: str
    type: str


class Blocker(LatticeBaseModel):
    code: str
    message: str
    provenance: list[Provenance] = Field(default_factory=list)


class WarningItem(LatticeBaseModel):
    code: str
    message: str
    provenance: list[Provenance] = Field(default_factory=list)
