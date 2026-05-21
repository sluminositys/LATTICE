from __future__ import annotations

from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field

from helix.graph.packaged import load_graph_records
from helix.schemas import BioEvoKGGraphRecords, GraphProfile, HelixBaseModel


class GraphRecordStore(Protocol):
    def replace_records(self, records: BioEvoKGGraphRecords) -> str:
        """Replace one graph tier with externally validated graph records."""


class GraphAssetImportReport(HelixBaseModel):
    profile_id: str
    graph_tier: Literal["L0", "L1"]
    status: Literal["imported", "blocked"]
    node_count: int = 0
    edge_count: int = 0
    durable_write_id: str | None = None
    blockers: list[str] = Field(default_factory=list)


class GraphAssetImporter:
    def import_records(
        self,
        *,
        profile: GraphProfile,
        graph_tier: Literal["L0", "L1"],
        asset_path: str | Path,
        store: GraphRecordStore,
    ) -> GraphAssetImportReport:
        if graph_tier == "L1" and profile.mode == "production" and profile.l1_source not in {
            "database",
            "memory_health_compiler",
            "packaged",
        }:
            return GraphAssetImportReport(
                profile_id=profile.profile_id,
                graph_tier=graph_tier,
                status="blocked",
                blockers=[f"Unsupported L1 source for import: {profile.l1_source}"],
            )

        records = load_graph_records(asset_path, graph_tier=graph_tier)
        durable_write_id = store.replace_records(records)
        return GraphAssetImportReport(
            profile_id=profile.profile_id,
            graph_tier=graph_tier,
            status="imported",
            node_count=len(records.nodes),
            edge_count=len(records.edges),
            durable_write_id=durable_write_id,
        )
