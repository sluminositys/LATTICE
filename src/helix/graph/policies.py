from __future__ import annotations

from helix.schemas import GraphPatch, GraphProfile


class GraphTierPolicyError(ValueError):
    pass


class GraphTierPolicy:
    memory_health_compiler_module = "MemoryHealthCompiler"

    def assert_patch_targets_l0(self, patch: GraphPatch) -> None:
        if patch.target_graph_tier != "L0":
            msg = "GraphPatch can only target L0."
            raise GraphTierPolicyError(msg)

    def assert_l1_update_source(self, source_module: str) -> None:
        if source_module != self.memory_health_compiler_module:
            msg = "L1 can only be updated by MemoryHealthCompiler materialization."
            raise GraphTierPolicyError(msg)

    def assert_graph_patch_writes_allowed(self, profile: GraphProfile) -> None:
        if not profile.mutable or not profile.graph_patch_writes_enabled:
            msg = f"GraphPatch writes are disabled for graph profile: {profile.profile_id}"
            raise GraphTierPolicyError(msg)

    def assert_builder_allowed(self, profile: GraphProfile) -> None:
        if not profile.builder_enabled:
            msg = f"Builder workflows are disabled for graph profile: {profile.profile_id}"
            raise GraphTierPolicyError(msg)

    def assert_evolution_allowed(self, profile: GraphProfile) -> None:
        if not profile.evolution_enabled:
            msg = f"Evolution workflows are disabled for graph profile: {profile.profile_id}"
            raise GraphTierPolicyError(msg)
