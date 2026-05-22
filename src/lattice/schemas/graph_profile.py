from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, model_validator
from typing_extensions import Self

from lattice.schemas.common import LatticeBaseModel, Provenance

GraphProfileMode = Literal["demo", "production"]
L0GraphSource = Literal["packaged", "database", "builder"]
L1GraphSource = Literal["packaged", "database", "memory_health_compiler"]
GraphHealthPolicy = Literal["prevalidated_all_healthy", "memory_health_compiler"]


class GraphProfile(LatticeBaseModel):
    profile_id: str
    mode: GraphProfileMode
    schema_version: str = "graph-profile/v1"
    description: str | None = None
    l0_source: L0GraphSource
    l1_source: L1GraphSource
    l0_asset_path: str | None = None
    l1_asset_path: str | None = None
    mutable: bool
    graph_patch_writes_enabled: bool
    builder_enabled: bool
    evolution_enabled: bool
    health_policy: GraphHealthPolicy
    provenance: list[Provenance] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_profile_policy(self) -> Self:
        if self.mode == "demo":
            self._validate_demo_profile()
        else:
            self._validate_production_profile()
        return self

    def _validate_demo_profile(self) -> None:
        blockers: list[str] = []
        if self.mutable:
            blockers.append("demo graph profiles must be immutable")
        if self.graph_patch_writes_enabled:
            blockers.append("demo graph profiles cannot allow GraphPatch writes")
        if self.builder_enabled:
            blockers.append("demo graph profiles cannot enable builder workflows")
        if self.evolution_enabled:
            blockers.append("demo graph profiles cannot enable evolution workflows")
        if self.l0_source != "packaged":
            blockers.append("demo L0 source must be packaged")
        if self.l1_source != "packaged":
            blockers.append("demo L1 source must be packaged")
        if self.health_policy != "prevalidated_all_healthy":
            blockers.append("demo graph profiles must use prevalidated_all_healthy")
        if self.l0_asset_path is None:
            blockers.append("demo graph profiles require l0_asset_path")
        if self.l1_asset_path is None:
            blockers.append("demo graph profiles require l1_asset_path")
        if blockers:
            raise ValueError("; ".join(blockers))

    def _validate_production_profile(self) -> None:
        if self.health_policy == "prevalidated_all_healthy":
            msg = "prevalidated_all_healthy is reserved for packaged demo graph profiles"
            raise ValueError(msg)


def create_packaged_demo_graph_profile(
    *,
    profile_id: str,
    l0_asset_path: str,
    l1_asset_path: str,
    description: str | None = None,
    provenance: list[Provenance] | None = None,
    metadata: dict[str, Any] | None = None,
) -> GraphProfile:
    return GraphProfile(
        profile_id=profile_id,
        mode="demo",
        description=description,
        l0_source="packaged",
        l1_source="packaged",
        l0_asset_path=l0_asset_path,
        l1_asset_path=l1_asset_path,
        mutable=False,
        graph_patch_writes_enabled=False,
        builder_enabled=False,
        evolution_enabled=False,
        health_policy="prevalidated_all_healthy",
        provenance=provenance or [],
        metadata=metadata or {},
    )
