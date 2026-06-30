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
        ("skill", "ToolUsageSkill"),
        ("experience", "FailureRecord"),
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


def test_g0_records_allow_l2_to_l6_reports_experience_exception() -> None:
    evidence = BioEvoKGNode.model_validate(
        make_node(
            node_id="evidence:paper",
            layer="evidence",
            node_type="Paper",
            operational_profile=None,
        )
    )
    experience = BioEvoKGNode.model_validate(
        make_node(
            node_id="experience:risk",
            layer="experience",
            node_type="FailureRecord",
            operational_profile=None,
        )
    )
    edge = BioEvoKGEdge.model_validate(
        {
            "edge_id": "edge:evidence-experience",
            "edge_type": "REPORTS_EXPERIENCE",
            "source_node_id": evidence.node_id,
            "target_node_id": experience.node_id,
            "source_layer": evidence.layer,
            "target_layer": experience.layer,
            "source_type": evidence.node_type,
            "lifecycle_state": "candidate",
            "operational_profile": None,
            "provenance": [{"source_type": "test"}],
        }
    )

    records = BioEvoKGGraphRecords(graph_tier="G0", nodes=[evidence, experience], edges=[edge])

    assert records.edges[0].edge_type == "REPORTS_EXPERIENCE"


def test_g0_records_still_reject_l1_to_l6_experience_edges() -> None:
    task = BioEvoKGNode.model_validate(
        make_node(
            node_id="task:assembly",
            layer="task",
            node_type="Task",
            operational_profile=None,
        )
    )
    experience = BioEvoKGNode.model_validate(
        make_node(
            node_id="experience:risk",
            layer="experience",
            node_type="FailureRecord",
            operational_profile=None,
        )
    )
    edge = BioEvoKGEdge.model_validate(
        {
            "edge_id": "edge:task-experience",
            "edge_type": "REPORTS_EXPERIENCE",
            "source_node_id": task.node_id,
            "target_node_id": experience.node_id,
            "source_layer": task.layer,
            "target_layer": experience.layer,
            "source_type": task.node_type,
            "lifecycle_state": "candidate",
            "operational_profile": None,
            "provenance": [{"source_type": "test"}],
        }
    )

    with pytest.raises(ValidationError):
        BioEvoKGGraphRecords(graph_tier="G0", nodes=[task, experience], edges=[edge])


def test_g0_records_require_l4_l4_dataflow_context() -> None:
    aligner = BioEvoKGNode.model_validate(
        make_node(
            node_id="resource:bwa",
            layer="resource",
            node_type="Tool",
            operational_profile=None,
        )
    )
    processor = BioEvoKGNode.model_validate(
        make_node(
            node_id="resource:samtools",
            layer="resource",
            node_type="Tool",
            operational_profile=None,
        )
    )
    valid_edge = BioEvoKGEdge.model_validate(
        {
            "edge_id": "edge:bwa-samtools",
            "edge_type": "FEEDS_INTO",
            "source_node_id": aligner.node_id,
            "target_node_id": processor.node_id,
            "source_layer": aligner.layer,
            "target_layer": processor.layer,
            "source_type": aligner.node_type,
            "attributes": {"workflow_temp_id": "workflow:variant-calling"},
            "lifecycle_state": "candidate",
            "operational_profile": None,
            "provenance": [{"source_type": "test"}],
        }
    )

    records = BioEvoKGGraphRecords(graph_tier="G0", nodes=[aligner, processor], edges=[valid_edge])

    assert records.edges[0].edge_type == "FEEDS_INTO"

    generic_edge = valid_edge.model_copy(
        update={
            "edge_id": "edge:generic",
            "edge_type": "SUPPORTS_WORKFLOW",
            "attributes": {"workflow_temp_id": "workflow:variant-calling"},
        }
    )
    missing_context_edge = valid_edge.model_copy(
        update={
            "edge_id": "edge:missing-context",
            "attributes": {},
        }
    )

    for edge in (generic_edge, missing_context_edge):
        with pytest.raises(ValidationError):
            BioEvoKGGraphRecords(graph_tier="G0", nodes=[aligner, processor], edges=[edge])
