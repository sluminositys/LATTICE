from __future__ import annotations

import json
from pathlib import Path

from lattice.graph import GraphAssetImporter
from lattice.schemas import BioEvoKGGraphRecords, GraphProfile


class RecordingGraphRecordStore:
    def __init__(self) -> None:
        self.records: BioEvoKGGraphRecords | None = None

    def replace_records(self, records: BioEvoKGGraphRecords) -> str:
        self.records = records
        return "write-1"


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )


def test_graph_asset_importer_validates_and_replaces_records(tmp_path: Path) -> None:
    asset_path = tmp_path / "l0"
    write_jsonl(
        asset_path / "nodes.jsonl",
        [
            {
                "node_id": "task-1",
                "layer": "task",
                "node_type": "Task",
                "canonical_name": "Task",
                "lifecycle_state": "candidate",
                "provenance": [{"source_type": "test"}],
            }
        ],
    )
    write_jsonl(asset_path / "edges.jsonl", [])
    store = RecordingGraphRecordStore()

    report = GraphAssetImporter().import_records(
        profile=GraphProfile(
            profile_id="prod",
            mode="production",
            l0_source="database",
            l1_source="database",
            mutable=True,
            graph_patch_writes_enabled=True,
            builder_enabled=False,
            evolution_enabled=True,
            health_policy="memory_health_compiler",
        ),
        graph_tier="G0",
        asset_path=asset_path,
        store=store,
    )

    assert report.status == "imported"
    assert report.durable_write_id == "write-1"
    assert store.records is not None
    assert store.records.nodes[0].node_id == "task-1"
