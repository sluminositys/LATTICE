import pytest

from helix.graph import GraphProfileRegistry, GraphProfileRegistryError, GraphTierPolicy
from helix.schemas import GraphProfile, create_packaged_demo_graph_profile


def make_production_profile() -> GraphProfile:
    return GraphProfile(
        profile_id="production-profile",
        mode="production",
        l0_source="builder",
        l1_source="memory_health_compiler",
        mutable=True,
        graph_patch_writes_enabled=True,
        builder_enabled=True,
        evolution_enabled=True,
        health_policy="memory_health_compiler",
    )


def test_graph_profile_registry_returns_registered_profiles() -> None:
    demo_profile = create_packaged_demo_graph_profile(
        profile_id="demo-profile",
        l0_asset_path="resources/demo/demo_l0",
        l1_asset_path="resources/demo/demo_l1",
    )
    production_profile = make_production_profile()
    registry = GraphProfileRegistry([demo_profile, production_profile])

    assert registry.require("demo-profile") == demo_profile
    assert registry.list_demo_profiles() == [demo_profile]

    with pytest.raises(GraphProfileRegistryError):
        registry.require("missing")


def test_graph_profile_policy_blocks_demo_builder_evolution_and_patch_writes() -> None:
    policy = GraphTierPolicy()
    demo_profile = create_packaged_demo_graph_profile(
        profile_id="demo-profile",
        l0_asset_path="resources/demo/demo_l0",
        l1_asset_path="resources/demo/demo_l1",
    )

    with pytest.raises(ValueError):
        policy.assert_graph_patch_writes_allowed(demo_profile)
    with pytest.raises(ValueError):
        policy.assert_builder_allowed(demo_profile)
    with pytest.raises(ValueError):
        policy.assert_evolution_allowed(demo_profile)


def test_graph_profile_policy_allows_production_builder_evolution_and_patch_writes() -> None:
    policy = GraphTierPolicy()
    production_profile = make_production_profile()

    policy.assert_graph_patch_writes_allowed(production_profile)
    policy.assert_builder_allowed(production_profile)
    policy.assert_evolution_allowed(production_profile)
