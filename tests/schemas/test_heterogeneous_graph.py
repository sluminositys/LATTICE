import pytest
from pydantic import ValidationError

from lattice.schemas import BioEvoKGEdge, BioEvoKGGraphRecords, BioEvoKGNode, OperationalProfile


def make_node(
    *,
    node_id: str = "node-1",
    layer: str = "workflow",
    node_type: str = "Method",
    lifecycle_state: str = "active_hot",
    operational_profile: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "node_id": node_id,
        "layer": layer,
        "node_type": node_type,
        "canonical_name": f"{node_type} node",
        "lifecycle_state": lifecycle_state,
        "operational_profile": operational_profile,
        "provenance": [{"source_type": "test"}],
    }


def make_edge(
    *,
    lifecycle_state: str = "active_hot",
    operational_profile: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "edge_id": "edge-1",
        "edge_type": "IMPLEMENTS_METHOD",
        "source_node_id": "tool-1",
        "target_node_id": "method-1",
        "source_layer": "resource",
        "target_layer": "workflow",
        "source_type": "test",
        "lifecycle_state": lifecycle_state,
        "operational_profile": operational_profile,
        "provenance": [{"source_type": "test"}],
    }


def test_each_heterogeneous_layer_accepts_documented_node_types() -> None:
    examples = [
        ("task", "Task"),
        ("evidence", "Paper"),
        ("workflow", "WorkflowPath"),
        ("resource", "Tool"),
        ("implementation", "ToolImplementationProfile"),
        ("experience", "FailureCondition"),
    ]

    for layer, node_type in examples:
        node = BioEvoKGNode.model_validate(
            make_node(layer=layer, node_type=node_type, operational_profile=None)
        )
        assert node.layer == layer
        assert node.node_type == node_type


def test_node_type_must_belong_to_declared_layer() -> None:
    with pytest.raises(ValidationError):
        BioEvoKGNode.model_validate(
            make_node(layer="task", node_type="Tool", operational_profile=None)
        )


def test_nodes_and_edges_require_provenance() -> None:
    node = make_node(operational_profile=None)
    node["provenance"] = []
    edge = make_edge(operational_profile=None)
    edge["provenance"] = []

    with pytest.raises(ValidationError):
        BioEvoKGNode.model_validate(node)
    with pytest.raises(ValidationError):
        BioEvoKGEdge.model_validate(edge)


def test_l1_graph_records_require_operational_profiles_and_healthy_states() -> None:
    profile = OperationalProfile(lifecycle_state="active_hot")
    records = BioEvoKGGraphRecords(
        graph_tier="G1",
        nodes=[
            BioEvoKGNode.model_validate(
                make_node(
                    node_id="tool-1",
                    layer="resource",
                    node_type="Tool",
                    operational_profile=profile.model_dump(mode="json"),
                )
            ),
            BioEvoKGNode.model_validate(
                make_node(
                    node_id="method-1",
                    layer="workflow",
                    node_type="Method",
                    operational_profile=profile.model_dump(mode="json"),
                )
            ),
        ],
        edges=[
            BioEvoKGEdge.model_validate(
                make_edge(operational_profile=profile.model_dump(mode="json"))
            )
        ],
        require_l1_operational_profile=True,
        require_l1_healthy_states=True,
    )

    assert records.graph_tier == "G1"


def test_l1_graph_records_reject_missing_operational_profile() -> None:
    with pytest.raises(ValidationError):
        BioEvoKGGraphRecords(
            graph_tier="G1",
            nodes=[
                BioEvoKGNode.model_validate(
                    make_node(
                        node_id="tool-1",
                        layer="resource",
                        node_type="Tool",
                        operational_profile=None,
                    )
                )
            ],
            edges=[],
            require_l1_operational_profile=True,
        )
