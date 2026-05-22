import pytest
from pydantic import ValidationError

from lattice.schemas import GraphProfile, create_packaged_demo_graph_profile


def test_packaged_demo_graph_profile_disables_mutating_workflows() -> None:
    profile = create_packaged_demo_graph_profile(
        profile_id="demo-profile",
        l0_asset_path="resources/demo/demo_l0",
        l1_asset_path="resources/demo/demo_l1",
    )

    assert profile.mode == "demo"
    assert profile.l0_source == "packaged"
    assert profile.l1_source == "packaged"
    assert profile.mutable is False
    assert profile.graph_patch_writes_enabled is False
    assert profile.builder_enabled is False
    assert profile.evolution_enabled is False
    assert profile.health_policy == "prevalidated_all_healthy"


def test_demo_graph_profile_requires_packaged_l0_and_l1_assets() -> None:
    with pytest.raises(ValidationError):
        GraphProfile(
            profile_id="invalid-demo",
            mode="demo",
            l0_source="packaged",
            l1_source="packaged",
            mutable=False,
            graph_patch_writes_enabled=False,
            builder_enabled=False,
            evolution_enabled=False,
            health_policy="prevalidated_all_healthy",
        )


def test_production_graph_profile_cannot_mark_all_content_prevalidated() -> None:
    with pytest.raises(ValidationError):
        GraphProfile(
            profile_id="production-profile",
            mode="production",
            l0_source="builder",
            l1_source="memory_health_compiler",
            mutable=True,
            graph_patch_writes_enabled=True,
            builder_enabled=True,
            evolution_enabled=True,
            health_policy="prevalidated_all_healthy",
        )
