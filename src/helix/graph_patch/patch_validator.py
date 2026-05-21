from __future__ import annotations

from pydantic import Field, ValidationError

from helix.graph_health import LifecycleStateError, LifecycleStateManager
from helix.schemas import BioEvoKGEdge, BioEvoKGNode, GraphPatch, HelixBaseModel


class GraphPatchValidationReport(HelixBaseModel):
    patch_id: str
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.blockers


class GraphPatchValidator:
    def __init__(self, lifecycle_manager: LifecycleStateManager | None = None) -> None:
        self.lifecycle_manager = lifecycle_manager or LifecycleStateManager()

    def validate(self, patch: GraphPatch) -> GraphPatchValidationReport:
        blockers: list[str] = []
        warnings: list[str] = []

        if not patch.provenance.source_type.strip():
            blockers.append("GraphPatch provenance.source_type is required.")

        mutation_count = (
            len(patch.nodes_to_add)
            + len(patch.edges_to_add)
            + len(patch.nodes_to_update)
            + len(patch.edges_to_update)
            + len(patch.lifecycle_transitions)
        )
        if mutation_count == 0:
            blockers.append(
                "GraphPatch must contain at least one mutation or lifecycle transition."
            )

        for node in [*patch.nodes_to_add, *patch.nodes_to_update]:
            if "node_id" not in node:
                blockers.append("GraphPatch node mutation is missing node_id.")

        for node in patch.nodes_to_add:
            if "node_id" in node:
                try:
                    BioEvoKGNode.model_validate(node)
                except ValidationError as error:
                    first_error = error.errors()[0]["msg"]
                    blockers.append(
                        "GraphPatch node mutation failed Bio-EvoKG schema validation: "
                        f"{first_error}"
                    )

        for edge in [*patch.edges_to_add, *patch.edges_to_update]:
            if "edge_id" not in edge:
                blockers.append("GraphPatch edge mutation is missing edge_id.")

        for edge in patch.edges_to_add:
            if "edge_id" in edge:
                try:
                    BioEvoKGEdge.model_validate(edge)
                except ValidationError as error:
                    first_error = error.errors()[0]["msg"]
                    blockers.append(
                        "GraphPatch edge mutation failed Bio-EvoKG schema validation: "
                        f"{first_error}"
                    )

        for transition in patch.lifecycle_transitions:
            try:
                self.lifecycle_manager.assert_transition_allowed(transition)
            except LifecycleStateError as error:
                blockers.append(str(error))

        if patch.risk_level in {"high", "critical"} and patch.approval_status != "approved":
            warnings.append("High-risk GraphPatch should be approved before application.")

        return GraphPatchValidationReport(
            patch_id=patch.patch_id,
            blockers=blockers,
            warnings=warnings,
        )
