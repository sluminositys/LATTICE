from typing import Any

from lattice.graph_construction import GraphConstructionBootstrapWorkflow
from lattice.schemas import GraphPatch, Provenance, create_packaged_demo_graph_profile


def make_valid_node() -> dict[str, object]:
    return {
        "node_id": "node-1",
        "layer": "workflow",
        "node_type": "Method",
        "canonical_name": "Method node",
        "lifecycle_state": "candidate",
        "provenance": [{"source_type": "test"}],
    }


class RecordingFullGraphStore:
    def __init__(self) -> None:
        self.applied_patches: list[GraphPatch] = []

    def apply_patch(self, patch: GraphPatch) -> str:
        self.applied_patches.append(patch)
        return f"l0-write-{patch.patch_id}"

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return None


def test_bootstrap_workflow_blocks_before_l0_write_when_audit_fails() -> None:
    store = RecordingFullGraphStore()
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=[],
        source_module="test",
        provenance=Provenance(source_type="test"),
    )

    result = GraphConstructionBootstrapWorkflow(full_graph_store=store).run(patch)

    assert result.status == "blocked"
    assert result.durable_write_id is None
    assert result.memory_health_report is None
    assert store.applied_patches == []


def test_bootstrap_workflow_applies_l0_patch_and_runs_health_compiler() -> None:
    store = RecordingFullGraphStore()
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        nodes_to_add=[make_valid_node()],
        provenance=Provenance(source_type="test"),
    )

    result = GraphConstructionBootstrapWorkflow(full_graph_store=store).run(patch)

    assert result.status == "applied_to_l0_and_compiled_l1"
    assert result.durable_write_id == "l0-write-patch-1"
    assert result.memory_health_report is not None
    assert result.memory_health_report.compiled_patch_ids == ["patch-1"]
    assert store.applied_patches == [patch]


def test_bootstrap_workflow_blocks_demo_profile_before_l0_write() -> None:
    store = RecordingFullGraphStore()
    profile = create_packaged_demo_graph_profile(
        profile_id="demo-profile",
        l0_asset_path="resources/demo/demo_l0",
        l1_asset_path="resources/demo/demo_l1",
    )
    patch = GraphPatch(
        patch_id="patch-1",
        source_event_ids=["event-1"],
        source_module="test",
        nodes_to_add=[make_valid_node()],
        provenance=Provenance(source_type="test"),
    )

    result = GraphConstructionBootstrapWorkflow(
        full_graph_store=store,
        graph_profile=profile,
    ).run(patch)

    assert result.status == "blocked"
    assert result.durable_write_id is None
    assert result.memory_health_report is None
    assert result.notes == ["Builder workflows are disabled for graph profile: demo-profile"]
    assert store.applied_patches == []
