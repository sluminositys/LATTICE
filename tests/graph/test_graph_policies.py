import pytest

from helix.graph import GraphTierPolicy, GraphTierPolicyError
from helix.schemas import GraphPatch, Provenance


def test_graph_patch_policy_allows_l0_patch() -> None:
    patch = GraphPatch(
        patch_id="patch-1",
        source_module="GraphPatchAuditor",
        provenance=Provenance(source_type="test"),
    )

    GraphTierPolicy().assert_patch_targets_l0(patch)


def test_l1_update_policy_only_allows_memory_health_compiler() -> None:
    policy = GraphTierPolicy()

    policy.assert_l1_update_source("MemoryHealthCompiler")

    with pytest.raises(GraphTierPolicyError):
        policy.assert_l1_update_source("GraphPatchApplier")
