from __future__ import annotations

import importlib
import json
import re
from collections.abc import Iterable
from typing import Any, Literal
from uuid import uuid4

from lattice.graph.policies import GraphTierPolicy, GraphTierPolicyError
from lattice.graph.stores import FullGraphStore, HealthyGraphStore
from lattice.schemas import (
    BioEvoKGEdge,
    BioEvoKGGraphRecords,
    BioEvoKGNode,
    GraphContextSufficiencyReport,
    GraphPatch,
    Provenance,
    RuntimeGraphContext,
    TaskFingerprint,
)


class Neo4jStoreError(RuntimeError):
    pass


class Neo4jFullGraphStore(FullGraphStore):
    def __init__(
        self,
        *,
        uri: str,
        user: str,
        password: str,
        database: str | None = None,
        graph_profile_id: str,
        driver: Any | None = None,
    ) -> None:
        self.database = database
        self.graph_profile_id = graph_profile_id
        self.driver = driver or _create_neo4j_driver(uri=uri, user=user, password=password)

    def apply_patch(self, patch: GraphPatch) -> str:
        write_id = f"neo4j-write-{uuid4()}"
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._apply_patch_tx, patch, write_id)
        return write_id

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        query = """
        MATCH (n:BioEvoKGNode {
            graph_profile_id: $graph_profile_id,
            graph_tier: 'G0',
            node_id: $node_id
        })
        RETURN properties(n) AS node
        LIMIT 1
        """
        with self.driver.session(database=self.database) as session:
            record = session.execute_read(
                lambda tx: tx.run(
                    query,
                    graph_profile_id=self.graph_profile_id,
                    node_id=node_id,
                ).single()
            )
        if record is None:
            return None
        return dict(record["node"])

    def replace_records(self, records: BioEvoKGGraphRecords) -> str:
        write_id = f"neo4j-import-{uuid4()}"
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._replace_records_tx, records, write_id)
        return write_id

    def _apply_patch_tx(self, tx: Any, patch: GraphPatch, write_id: str) -> None:
        tx.run(
            """
            MERGE (p:GraphPatchRecord {patch_id: $patch_id})
            SET p.source_module = $source_module,
                p.target_graph_tier = $target_graph_tier,
                p.approval_status = $approval_status,
                p.risk_level = $risk_level,
                p.write_id = $write_id,
                p.payload_json = $payload_json
            """,
            patch_id=patch.patch_id,
            source_module=patch.source_module,
            target_graph_tier=patch.target_graph_tier,
            approval_status=patch.approval_status,
            risk_level=patch.risk_level,
            write_id=write_id,
            payload_json=patch.model_dump_json(),
        )
        for raw_node in patch.nodes_to_add:
            node = BioEvoKGNode.model_validate(raw_node)
            _merge_node(tx, self.graph_profile_id, "G0", node)
        for raw_edge in patch.edges_to_add:
            edge = BioEvoKGEdge.model_validate(raw_edge)
            _merge_edge(tx, self.graph_profile_id, "G0", edge)

    def _replace_records_tx(
        self,
        tx: Any,
        records: BioEvoKGGraphRecords,
        write_id: str,
    ) -> None:
        tx.run(
            """
            MATCH (n:BioEvoKGNode {graph_profile_id: $graph_profile_id, graph_tier: $graph_tier})
            DETACH DELETE n
            """,
            graph_profile_id=self.graph_profile_id,
            graph_tier=records.graph_tier,
        )
        for node in records.nodes:
            _merge_node(tx, self.graph_profile_id, records.graph_tier, node, write_id=write_id)
        for edge in records.edges:
            _merge_edge(tx, self.graph_profile_id, records.graph_tier, edge, write_id=write_id)


class Neo4jHealthyGraphStore(HealthyGraphStore):
    def __init__(
        self,
        *,
        uri: str,
        user: str,
        password: str,
        database: str | None = None,
        graph_profile_id: str,
        driver: Any | None = None,
    ) -> None:
        self.database = database
        self.graph_profile_id = graph_profile_id
        self.driver = driver or _create_neo4j_driver(uri=uri, user=user, password=password)

    def project_runtime_context(self, fingerprint: TaskFingerprint) -> RuntimeGraphContext:
        query = """
        MATCH (n:BioEvoKGNode {graph_profile_id: $graph_profile_id, graph_tier: 'G1'})
        WHERE n.lifecycle_state IN ['active_hot', 'active_warm']
        RETURN properties(n) AS node
        LIMIT 250
        """
        with self.driver.session(database=self.database) as session:
            records = session.execute_read(
                lambda tx: list(tx.run(query, graph_profile_id=self.graph_profile_id))
            )
        nodes = [dict(record["node"]) for record in records]
        by_layer: dict[str, list[dict[str, Any]]] = {
            "task": [],
            "evidence": [],
            "workflow": [],
            "resource": [],
            "skill": [],
            "experience": [],
        }
        for node in nodes:
            layer = node.get("layer")
            if layer in by_layer:
                by_layer[layer].append(node)

        missing: list[str] = []
        if not by_layer["workflow"]:
            missing.append("no workflow layer nodes projected from G1")
        if not by_layer["resource"]:
            missing.append("no resource layer nodes projected from G1")
        status: Literal["sufficient", "insufficient"] = (
            "sufficient" if not missing else "insufficient"
        )
        report = GraphContextSufficiencyReport(
            report_id=f"gcsr-{uuid4()}",
            status=status,
            missing_workflow_info=missing,
            controlled_recall_required=bool(missing),
            controlled_recall_reason="G1 projection did not provide enough runtime graph context"
            if missing
            else None,
        )
        return RuntimeGraphContext(
            graph_context_id=f"rgc-{uuid4()}",
            task_fingerprint_id=fingerprint.fingerprint_id,
            source_graph_tier="G1",
            G_task={"task": fingerprint.task, "nodes": by_layer["task"]},
            G_evidence={"nodes": by_layer["evidence"]},
            G_workflow={"nodes": by_layer["workflow"]},
            G_resource={"nodes": by_layer["resource"]},
            G_skill={"nodes": by_layer["skill"]},
            G_experience={"nodes": by_layer["experience"]},
            sufficiency_report=report,
            provenance=[
                Provenance(
                    source_type="neo4j_g1_projection",
                    source_id=self.graph_profile_id,
                )
            ],
        )

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        query = """
        MATCH (n:BioEvoKGNode {
            graph_profile_id: $graph_profile_id,
            graph_tier: 'G1',
            node_id: $node_id
        })
        RETURN properties(n) AS node
        LIMIT 1
        """
        with self.driver.session(database=self.database) as session:
            record = session.execute_read(
                lambda tx: tx.run(
                    query,
                    graph_profile_id=self.graph_profile_id,
                    node_id=node_id,
                ).single()
            )
        if record is None:
            return None
        return dict(record["node"])

    def materialize_from_patches(self, patches: Iterable[GraphPatch]) -> str:
        patch_list = list(patches)
        policy = GraphTierPolicy()
        for patch in patch_list:
            if patch.target_graph_tier != "G1":
                msg = "Neo4jHealthyGraphStore materialization requires G1 patches."
                raise Neo4jStoreError(msg)
            try:
                policy.assert_l1_update_source(patch.source_module)
            except GraphTierPolicyError as error:
                raise Neo4jStoreError(str(error)) from error

        write_id = f"neo4j-g1-materialize-{uuid4()}"
        with self.driver.session(database=self.database) as session:
            session.execute_write(self._materialize_patches_tx, patch_list, write_id)
        return write_id

    def replace_records(self, records: BioEvoKGGraphRecords) -> str:
        if records.graph_tier != "G1":
            msg = "Neo4jHealthyGraphStore can only import G1 records."
            raise Neo4jStoreError(msg)
        write_id = f"neo4j-g1-import-{uuid4()}"
        with self.driver.session(database=self.database) as session:
            session.execute_write(_replace_records_tx, self.graph_profile_id, records, write_id)
        return write_id

    def _materialize_patches_tx(
        self,
        tx: Any,
        patches: list[GraphPatch],
        write_id: str,
    ) -> None:
        for patch in patches:
            tx.run(
                """
                MERGE (p:GraphPatchRecord {patch_id: $patch_id, graph_tier: 'G1'})
                SET p.source_module = $source_module,
                    p.target_graph_tier = $target_graph_tier,
                    p.approval_status = $approval_status,
                    p.risk_level = $risk_level,
                    p.write_id = $write_id,
                    p.payload_json = $payload_json
                """,
                patch_id=patch.patch_id,
                source_module=patch.source_module,
                target_graph_tier=patch.target_graph_tier,
                approval_status=patch.approval_status,
                risk_level=patch.risk_level,
                write_id=write_id,
                payload_json=patch.model_dump_json(),
            )
            for raw_node in patch.nodes_to_add:
                node = BioEvoKGNode.model_validate(raw_node)
                _merge_node(tx, self.graph_profile_id, "G1", node, write_id=write_id)
            for raw_edge in patch.edges_to_add:
                edge = BioEvoKGEdge.model_validate(raw_edge)
                _merge_edge(tx, self.graph_profile_id, "G1", edge, write_id=write_id)


def _create_neo4j_driver(*, uri: str, user: str, password: str) -> Any:
    try:
        neo4j = importlib.import_module("neo4j")
    except ImportError as error:
        msg = "neo4j package is required for Neo4j graph stores."
        raise Neo4jStoreError(msg) from error
    return neo4j.GraphDatabase.driver(uri, auth=(user, password))


def _replace_records_tx(
    tx: Any,
    graph_profile_id: str,
    records: BioEvoKGGraphRecords,
    write_id: str,
) -> None:
    tx.run(
        """
        MATCH (n:BioEvoKGNode {graph_profile_id: $graph_profile_id, graph_tier: $graph_tier})
        DETACH DELETE n
        """,
        graph_profile_id=graph_profile_id,
        graph_tier=records.graph_tier,
    )
    for node in records.nodes:
        _merge_node(tx, graph_profile_id, records.graph_tier, node, write_id=write_id)
    for edge in records.edges:
        _merge_edge(tx, graph_profile_id, records.graph_tier, edge, write_id=write_id)


def _merge_node(
    tx: Any,
    graph_profile_id: str,
    graph_tier: str,
    node: BioEvoKGNode,
    *,
    write_id: str | None = None,
) -> None:
    labels = ":".join(
        [
            "BioEvoKGNode",
            f"{_pascal(node.layer)}Layer",
            _safe_label(node.node_type),
        ]
    )
    query = f"""
    MERGE (n:{labels} {{
        graph_profile_id: $graph_profile_id,
        graph_tier: $graph_tier,
        node_id: $node_id
    }})
    SET n += $properties
    """
    properties = _json_ready(node.model_dump(mode="json"))
    properties.update(
        {
            "graph_profile_id": graph_profile_id,
            "graph_tier": graph_tier,
            "write_id": write_id,
        }
    )
    tx.run(
        query,
        graph_profile_id=graph_profile_id,
        graph_tier=graph_tier,
        node_id=node.node_id,
        properties=properties,
    )


def _merge_edge(
    tx: Any,
    graph_profile_id: str,
    graph_tier: str,
    edge: BioEvoKGEdge,
    *,
    write_id: str | None = None,
) -> None:
    rel_type = _safe_relationship(edge.edge_type)
    query = f"""
    MATCH (s:BioEvoKGNode {{
        graph_profile_id: $graph_profile_id,
        graph_tier: $graph_tier,
        node_id: $source_node_id
    }})
    MATCH (t:BioEvoKGNode {{
        graph_profile_id: $graph_profile_id,
        graph_tier: $graph_tier,
        node_id: $target_node_id
    }})
    MERGE (s)-[r:{rel_type} {{edge_id: $edge_id}}]->(t)
    SET r += $properties
    """
    properties = _json_ready(edge.model_dump(mode="json"))
    properties.update(
        {
            "graph_profile_id": graph_profile_id,
            "graph_tier": graph_tier,
            "write_id": write_id,
        }
    )
    tx.run(
        query,
        graph_profile_id=graph_profile_id,
        graph_tier=graph_tier,
        source_node_id=edge.source_node_id,
        target_node_id=edge.target_node_id,
        edge_id=edge.edge_id,
        properties=properties,
    )


def _json_ready(payload: dict[str, Any]) -> dict[str, Any]:
    ready: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, dict | list):
            ready[key] = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            ready[key] = value
    return ready


def _pascal(value: str) -> str:
    return "".join(part.capitalize() for part in value.split("_"))


def _safe_label(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", value):
        msg = f"Unsafe Neo4j label: {value}"
        raise Neo4jStoreError(msg)
    return value


def _safe_relationship(value: str) -> str:
    if not re.fullmatch(r"[A-Z][A-Z0-9_]*", value):
        msg = f"Unsafe Neo4j relationship type: {value}"
        raise Neo4jStoreError(msg)
    return value
