from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class HelixBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


GraphTier = Literal["L0", "L1", "L2", "L1_plus_controlled_L0_recall"]

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


class Provenance(HelixBaseModel):
    source_type: str
    source_id: str | None = None
    source_path: str | None = None
    source_version: str | None = None
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class IdRef(HelixBaseModel):
    id: str
    type: str


class Blocker(HelixBaseModel):
    code: str
    message: str
    provenance: list[Provenance] = Field(default_factory=list)


class WarningItem(HelixBaseModel):
    code: str
    message: str
    provenance: list[Provenance] = Field(default_factory=list)
