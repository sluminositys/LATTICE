from __future__ import annotations

from typing import Literal
from uuid import uuid4

from helix.runtime import AgentEvent
from helix.schemas import Constraint, Provenance


class FailureToConstraintExtractor:
    def extract(
        self,
        event: AgentEvent,
        *,
        scope: Literal["user", "lab", "project", "global"] = "user",
        severity: Literal["blocker", "warning", "info"] = "warning",
    ) -> Constraint:
        if event.event_type not in {"ToolCallFailed", "PostToolCallFailure"}:
            msg = f"Cannot extract failure constraint from event type: {event.event_type}"
            raise ValueError(msg)

        if scope == "global" and severity == "blocker":
            msg = "Single failure events cannot become global blocker constraints."
            raise ValueError(msg)

        tool_name = str(event.payload.get("tool_name", "unknown_tool"))
        error_class = str(event.payload.get("error_class", "unknown_error"))
        trigger_condition = {
            "scope": scope,
            "event_id": event.event_id,
            "tool_name": tool_name,
            "error_class": error_class,
        }
        provenance = (
            event.provenance[0] if event.provenance else Provenance(source_type="event_log")
        )
        repair_hint = str(
            event.payload.get("repair_hint", "review failed ToolCall before reuse")
        )
        return Constraint(
            constraint_id=f"constraint-{uuid4()}",
            type="failure_condition",
            subject=tool_name,
            relation="failed_with",
            object=error_class,
            trigger_condition=trigger_condition,
            applies_to_layers=["Implementation", "Workflow", "Experience"],
            severity=severity,
            repair_hint=repair_hint,
            provenance=provenance,
            lifecycle_state="candidate",
        )
