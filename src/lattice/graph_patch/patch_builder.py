from __future__ import annotations

from collections.abc import Iterable
from uuid import uuid4

from lattice.runtime import AgentEvent
from lattice.schemas import GraphPatch, Provenance


class GraphPatchBuilder:
    def build_candidate(
        self,
        *,
        source_events: Iterable[AgentEvent],
        source_module: str,
        provenance: Provenance,
    ) -> GraphPatch:
        event_ids = [event.event_id for event in source_events]
        return GraphPatch(
            patch_id=f"patch-{uuid4()}",
            source_event_ids=event_ids,
            source_module=source_module,
            provenance=provenance,
            approval_status="proposed",
        )
