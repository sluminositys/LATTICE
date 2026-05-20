from __future__ import annotations

from typing import Protocol

from helix.schemas import AgenticExecutionStep, StructuredObservation, ToolCallSpec


class RuntimeBackend(Protocol):
    backend_name: str

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        """Execute a validated ToolCall step and return a structured observation."""
