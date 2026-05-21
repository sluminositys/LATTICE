from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from helix.schemas import (
    BioEvoKGEdge,
    BioEvoKGGraphRecords,
    BioEvoKGNode,
    GraphContextSufficiencyReport,
    GraphPatch,
    GraphProfile,
    PackagedDemoGraphManifest,
    Provenance,
    RuntimeGraphContext,
    TaskFingerprint,
)


class PackagedGraphStoreError(ValueError):
    pass


class PackagedFullGraphStore:
    def __init__(
        self,
        *,
        profile: GraphProfile,
        nodes: list[BioEvoKGNode],
        edges: list[BioEvoKGEdge],
    ) -> None:
        self.profile = profile
        self.nodes = [node.model_dump(mode="json") for node in nodes]
        self.edges = [edge.model_dump(mode="json") for edge in edges]
        self._nodes_by_id = _index_nodes(nodes)

    def apply_patch(self, patch: GraphPatch) -> str:
        msg = f"Packaged graph profile is read-only: {self.profile.profile_id}"
        raise PackagedGraphStoreError(msg)

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self._nodes_by_id.get(node_id)


class PackagedHealthyGraphStore:
    def __init__(
        self,
        *,
        profile: GraphProfile,
        nodes: list[BioEvoKGNode],
        edges: list[BioEvoKGEdge],
    ) -> None:
        self.profile = profile
        self.nodes = [node.model_dump(mode="json") for node in nodes]
        self.edges = [edge.model_dump(mode="json") for edge in edges]
        self._nodes_by_id = _index_nodes(nodes)

    def project_runtime_context(self, fingerprint: TaskFingerprint) -> RuntimeGraphContext:
        report = GraphContextSufficiencyReport(
            report_id=f"gcsr-{uuid4()}",
            status="sufficient" if self.nodes else "insufficient",
            missing_workflow_info=[] if self.nodes else ["packaged demo L1 has no nodes"],
            controlled_recall_required=False,
        )
        return RuntimeGraphContext(
            graph_context_id=f"rgc-{uuid4()}",
            task_fingerprint_id=fingerprint.fingerprint_id,
            source_graph_tier="L1",
            G_task={
                "profile_id": self.profile.profile_id,
                "mode": self.profile.mode,
                "task": fingerprint.task,
            },
            G_workflow={
                "nodes": self.nodes,
                "edges": self.edges,
            },
            sufficiency_report=report,
            provenance=[
                Provenance(
                    source_type="packaged_demo_l1",
                    source_id=self.profile.profile_id,
                    source_path=self.profile.l1_asset_path,
                )
            ],
        )

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self._nodes_by_id.get(node_id)


class JsonlPackagedDemoGraphStoreLoader:
    def load_l0_store(self, profile: GraphProfile) -> PackagedFullGraphStore:
        _assert_packaged_demo_profile(profile)
        if profile.l0_asset_path is None:
            msg = f"Demo profile has no L0 asset path: {profile.profile_id}"
            raise PackagedGraphStoreError(msg)
        records = _load_graph_records(Path(profile.l0_asset_path), graph_tier="L0")
        return PackagedFullGraphStore(
            profile=profile,
            nodes=records.nodes,
            edges=records.edges,
        )

    def load_l1_store(self, profile: GraphProfile) -> PackagedHealthyGraphStore:
        _assert_packaged_demo_profile(profile)
        if profile.l1_asset_path is None:
            msg = f"Demo profile has no L1 asset path: {profile.profile_id}"
            raise PackagedGraphStoreError(msg)
        records = _load_graph_records(Path(profile.l1_asset_path), graph_tier="L1")
        return PackagedHealthyGraphStore(
            profile=profile,
            nodes=records.nodes,
            edges=records.edges,
        )


def load_packaged_demo_graph_manifest(path: str | Path) -> PackagedDemoGraphManifest:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return PackagedDemoGraphManifest.model_validate(payload)


def _assert_packaged_demo_profile(profile: GraphProfile) -> None:
    if profile.mode != "demo":
        msg = f"Packaged demo loader only accepts demo profiles: {profile.profile_id}"
        raise PackagedGraphStoreError(msg)
    if profile.l0_source != "packaged" or profile.l1_source != "packaged":
        msg = f"Packaged demo loader requires packaged L0 and L1: {profile.profile_id}"
        raise PackagedGraphStoreError(msg)


def _load_graph_records(path: Path, *, graph_tier: Literal["L0", "L1"]) -> BioEvoKGGraphRecords:
    nodes = [BioEvoKGNode.model_validate(record) for record in _load_jsonl(path / "nodes.jsonl")]
    edges = [BioEvoKGEdge.model_validate(record) for record in _load_jsonl(path / "edges.jsonl")]
    return BioEvoKGGraphRecords(
        graph_tier=graph_tier,
        nodes=nodes,
        edges=edges,
        require_l1_operational_profile=graph_tier == "L1",
        require_l1_healthy_states=graph_tier == "L1",
    )


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        msg = f"Packaged graph asset file does not exist: {path}"
        raise PackagedGraphStoreError(msg)

    records: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            msg = f"Packaged graph asset line must be a JSON object: {path}:{line_number}"
            raise PackagedGraphStoreError(msg)
        records.append(payload)
    return records


def _index_nodes(nodes: list[BioEvoKGNode]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for node in nodes:
        indexed[node.node_id] = node.model_dump(mode="json")
    return indexed
