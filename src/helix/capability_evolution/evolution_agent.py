from __future__ import annotations

from uuid import uuid4

from pydantic import Field

from helix.graph_patch import GraphPatchBuilder
from helix.runtime import AgentEvent
from helix.schemas import CapabilityGap, GraphPatch, HelixBaseModel, Provenance


class EvolutionRequest(HelixBaseModel):
    request_id: str
    capability_gaps: list[CapabilityGap] = Field(default_factory=list)
    source_event_ids: list[str] = Field(default_factory=list)
    status: str = "candidate_patch_proposed"
    proposed_graph_patch_id: str | None = None


class EvolutionAgent:
    def propose_gap_patch(
        self,
        *,
        gaps: list[CapabilityGap],
        source_events: list[AgentEvent],
    ) -> tuple[EvolutionRequest, GraphPatch | None]:
        request = EvolutionRequest(
            request_id=f"evolution-request-{uuid4()}",
            capability_gaps=gaps,
            source_event_ids=[event.event_id for event in source_events],
        )
        if not gaps:
            return request.model_copy(update={"status": "no_gap"}), None

        patch = GraphPatchBuilder().build_candidate(
            source_events=source_events,
            source_module="EvolutionAgent",
            provenance=Provenance(source_type="evolution_agent"),
        )
        for gap in gaps:
            patch.nodes_to_add.append(
                {
                    "node_id": f"experience-quality-signal-{gap.gap_id}",
                    "layer": "experience",
                    "node_type": "QualitySignal",
                    "canonical_name": f"Capability gap: {gap.gap_type}",
                    "attributes": gap.model_dump(mode="json"),
                    "lifecycle_state": "candidate",
                    "provenance": [gap.provenance.model_dump(mode="json")],
                }
            )
        return (
            request.model_copy(update={"proposed_graph_patch_id": patch.patch_id}),
            patch,
        )
