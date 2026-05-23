from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator
from typing_extensions import Self

from lattice.schemas.common import LatticeBaseModel, Provenance


class PackagedGraphTierAsset(LatticeBaseModel):
    tier: Literal["G0", "G1"]
    nodes_path: str
    edges_path: str
    node_count: int | None = Field(default=None, ge=0)
    edge_count: int | None = Field(default=None, ge=0)
    content_hash: str | None = None


class PackagedDemoGraphManifest(LatticeBaseModel):
    manifest_id: str
    profile_id: str
    schema_version: str = "packaged-demo-graph/v1"
    l0: PackagedGraphTierAsset
    l1: PackagedGraphTierAsset
    all_l1_nodes_healthy: Literal[True] = True
    builder_artifacts_included: Literal[False] = False
    provenance: list[Provenance] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_tiers(self) -> Self:
        if self.l0.tier != "G0":
            msg = "Packaged demo manifest l0 asset must target G0."
            raise ValueError(msg)
        if self.l1.tier != "G1":
            msg = "Packaged demo manifest l1 asset must target G1."
            raise ValueError(msg)
        return self
