from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import uuid4

from pydantic import Field

from lattice.runtime import AgentEvent, AgentEventLog
from lattice.runtime.agent_event_log import AgentEventType
from lattice.schemas import LatticeBaseModel, Provenance


class HookBusError(ValueError):
    pass


class HookEvent(LatticeBaseModel):
    event_type: AgentEventType
    session_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    provenance: list[Provenance] = Field(default_factory=list)


class HookOutput(LatticeBaseModel):
    warnings: list[str] = Field(default_factory=list)
    audit_records: list[dict[str, Any]] = Field(default_factory=list)
    graph_patch_candidate_ids: list[str] = Field(default_factory=list)
    requested_l1_write: bool = False
    high_risk: bool = False


HookHandler = Callable[[HookEvent], HookOutput]


class HookRegistration(LatticeBaseModel):
    event_type: AgentEventType
    handler_name: str


class HookBus:
    def __init__(self, event_log: AgentEventLog | None = None) -> None:
        self.event_log = event_log
        self._handlers: dict[AgentEventType, list[tuple[str, HookHandler]]] = {}

    def register(
        self,
        event_type: AgentEventType,
        handler: HookHandler,
        *,
        handler_name: str | None = None,
    ) -> HookRegistration:
        raw_name = handler_name if handler_name is not None else getattr(handler, "__name__", None)
        name = raw_name if isinstance(raw_name, str) and raw_name else "anonymous_hook"
        self._handlers.setdefault(event_type, []).append((name, handler))
        return HookRegistration(event_type=event_type, handler_name=name)

    def emit(self, event: HookEvent) -> list[HookOutput]:
        outputs: list[HookOutput] = []
        for handler_name, handler in self._handlers.get(event.event_type, []):
            output = handler(event)
            if output.requested_l1_write:
                msg = f"Hook attempted direct L1 write: {handler_name}"
                raise HookBusError(msg)
            outputs.append(output)

        if self.event_log is not None:
            self.event_log.append(
                AgentEvent(
                    event_id=f"event-{uuid4()}",
                    session_id=event.session_id,
                    event_type=event.event_type,
                    payload={
                        "hook_outputs": [output.model_dump(mode="json") for output in outputs],
                        **event.payload,
                    },
                    provenance=event.provenance
                    or [Provenance(source_type="hook_bus", source_id=event.event_type)],
                )
            )
        return outputs
