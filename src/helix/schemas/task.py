from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import Field

from helix.schemas.common import ExecutionIntent, HelixBaseModel


class TaskFingerprint(HelixBaseModel):
    fingerprint_id: str
    user_id: str
    task: str
    task_category: str
    data_types: list[str] = Field(default_factory=list)
    input_formats: list[str] = Field(default_factory=list)
    output_goals: list[str] = Field(default_factory=list)
    execution_intent: ExecutionIntent = "plan_only"
    environment_constraints: dict[str, Any] = Field(default_factory=dict)
    preference_scope: dict[str, Any] = Field(default_factory=dict)
    ambiguity_items: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
