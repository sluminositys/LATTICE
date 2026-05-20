from helix.graph_patch import GraphPatchAuditor, GraphPatchBuilder
from helix.runtime import AgentEvent
from helix.schemas import Provenance


def test_graph_patch_builder_uses_source_events() -> None:
    event = AgentEvent(
        event_id="event-1",
        session_id="session-1",
        event_type="GraphPatchProposed",
        provenance=[Provenance(source_type="test")],
    )

    patch = GraphPatchBuilder().build_candidate(
        source_events=[event],
        source_module="test",
        provenance=Provenance(source_type="test"),
    )

    assert patch.source_event_ids == ["event-1"]
    assert patch.target_graph_tier == "L0"
    assert patch.approval_status == "proposed"


def test_graph_patch_auditor_blocks_patch_without_source_events() -> None:
    patch = GraphPatchBuilder().build_candidate(
        source_events=[],
        source_module="test",
        provenance=Provenance(source_type="test"),
    )

    report = GraphPatchAuditor().audit(patch)

    assert report.status == "blocked"
    assert "GraphPatch must reference at least one source event." in report.blockers
    assert (
        "GraphPatch must contain at least one mutation or lifecycle transition."
        in report.blockers
    )


def test_graph_patch_auditor_passes_valid_patch() -> None:
    patch = GraphPatchBuilder().build_candidate(
        source_events=[
            AgentEvent(
                event_id="event-1",
                session_id="session-1",
                event_type="GraphPatchProposed",
                provenance=[Provenance(source_type="test")],
            )
        ],
        source_module="test",
        provenance=Provenance(source_type="test"),
    )
    patch.nodes_to_add.append({"node_id": "node-1"})

    report = GraphPatchAuditor().audit(patch)

    assert report.status == "pass"
    assert report.blockers == []
