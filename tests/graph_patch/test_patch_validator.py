from lattice.graph_patch import GraphPatchValidator
from lattice.schemas import GraphPatch, LifecycleTransition, Provenance


def make_valid_node() -> dict[str, object]:
    return {
        "node_id": "node-1",
        "layer": "workflow",
        "node_type": "Method",
        "canonical_name": "Method node",
        "lifecycle_state": "candidate",
        "provenance": [{"source_type": "test"}],
    }


def test_patch_validator_blocks_empty_patch() -> None:
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        provenance=Provenance(source_type="test"),
    )

    report = GraphPatchValidator().validate(patch)

    assert report.passed is False
    assert report.blockers == [
        "GraphPatch must contain at least one mutation or lifecycle transition."
    ]


def test_patch_validator_requires_node_ids_for_node_mutations() -> None:
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        nodes_to_add=[{"label": "Tool"}],
        provenance=Provenance(source_type="test"),
    )

    report = GraphPatchValidator().validate(patch)

    assert report.blockers == ["GraphPatch node mutation is missing node_id."]


def test_patch_validator_rejects_invalid_lifecycle_transition() -> None:
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        lifecycle_transitions=[
            LifecycleTransition(
                transition_id="lt-1",
                target_node_or_edge_id="tool-1",
                from_state="candidate",
                to_state="active_hot",
                reason="skip review",
            )
        ],
        provenance=Provenance(source_type="test"),
    )

    report = GraphPatchValidator().validate(patch)

    assert report.blockers == ["Invalid lifecycle transition: candidate -> active_hot"]


def test_patch_validator_warns_for_unapproved_high_risk_patch() -> None:
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        nodes_to_add=[make_valid_node()],
        risk_level="high",
        provenance=Provenance(source_type="test"),
    )

    report = GraphPatchValidator().validate(patch)

    assert report.passed is True
    assert report.warnings == ["High-risk GraphPatch should be approved before application."]


def test_patch_validator_blocks_node_with_wrong_layer_type() -> None:
    node = make_valid_node()
    node["layer"] = "task"
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        nodes_to_add=[node],
        provenance=Provenance(source_type="test"),
    )

    report = GraphPatchValidator().validate(patch)

    assert report.passed is False
    assert report.blockers == [
        "GraphPatch node mutation failed Bio-EvoKG schema validation: "
        "Value error, Node type Method is not allowed in task layer."
    ]
