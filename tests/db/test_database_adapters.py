from __future__ import annotations

from typing import Any

from lattice.db import (
    Neo4jFullGraphStore,
    PostgresAgentEventLog,
    PostgresSchemaManager,
    PostgresToolCallSpecStore,
    QdrantGraphIndex,
)
from lattice.runtime import AgentEvent
from lattice.schemas import (
    BioEvoKGGraphRecords,
    BioEvoKGNode,
    Provenance,
    ToolCallSpec,
)


class FakeCursor:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, statement: str, params: object | None = None) -> None:
        self.connection.statements.append(statement)
        self.connection.params.append(params)

    def fetchone(self) -> object | None:
        return self.connection.fetchone_row

    def fetchall(self) -> list[object]:
        return self.connection.fetchall_rows


class FakeConnection:
    def __init__(self) -> None:
        self.statements: list[str] = []
        self.params: list[object | None] = []
        self.commits = 0
        self.fetchone_row: object | None = None
        self.fetchall_rows: list[object] = []

    def __enter__(self) -> FakeConnection:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        self.commits += 1


class FakeTx:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def run(self, query: str, **params: Any) -> list[object]:
        self.calls.append((query, params))
        return []


class FakeSession:
    def __init__(self, tx: FakeTx) -> None:
        self.tx = tx

    def __enter__(self) -> FakeSession:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute_write(self, fn: Any, *args: object) -> object:
        return fn(self.tx, *args)


class FakeNeo4jDriver:
    def __init__(self) -> None:
        self.tx = FakeTx()

    def session(self, database: str | None = None) -> FakeSession:
        return FakeSession(self.tx)


class FakeQdrantHit:
    def __init__(self) -> None:
        self.id = "point-1"
        self.score = 0.75
        self.payload = {"node_id": "node-1"}


class FakeQdrantClient:
    def __init__(self) -> None:
        self.upserts: list[dict[str, Any]] = []

    def upsert(self, **kwargs: Any) -> None:
        self.upserts.append(kwargs)

    def search(self, **kwargs: Any) -> list[FakeQdrantHit]:
        return [FakeQdrantHit()]


def make_toolcall_spec() -> ToolCallSpec:
    return ToolCallSpec(
        toolcall_spec_id="toolcall-1",
        name="Tool",
        tool_name="tool",
        tool_version_policy="pinned",
        input_schema={"required": ["input"]},
        output_schema={"type": "object"},
        runtime_backend="cli",
        lifecycle_state="active_hot",
        provenance=Provenance(source_type="test"),
    )


def make_node() -> BioEvoKGNode:
    return BioEvoKGNode(
        node_id="node-1",
        layer="task",
        node_type="Task",
        canonical_name="Task",
        lifecycle_state="candidate",
        provenance=[Provenance(source_type="test")],
    )


def test_postgres_schema_manager_creates_core_tables() -> None:
    connection = FakeConnection()

    PostgresSchemaManager(
        dsn="postgresql://test",
        connection_factory=lambda _dsn: connection,
    ).create_core_tables()

    assert connection.commits == 1
    assert any("CREATE TABLE IF NOT EXISTS agent_events" in sql for sql in connection.statements)


def test_postgres_toolcall_store_upserts_and_reads_specs() -> None:
    connection = FakeConnection()
    spec = make_toolcall_spec()
    row = (
        spec.toolcall_spec_id,
        spec.name,
        spec.tool_name,
        spec.tool_version_policy,
        spec.input_schema,
        spec.output_schema,
        spec.parameter_schema,
        spec.runtime_backend,
        spec.permission_policy,
        spec.parameter_source_policy,
        spec.lifecycle_state,
        spec.provenance.model_dump(mode="json"),
    )
    connection.fetchone_row = row
    connection.fetchall_rows = [row]
    store = PostgresToolCallSpecStore(
        dsn="postgresql://test",
        connection_factory=lambda _dsn: connection,
    )

    store.upsert(spec)

    assert connection.commits == 1
    assert store.get("toolcall-1") == spec
    assert store.list_active() == [spec]


def test_postgres_event_log_round_trips_events() -> None:
    connection = FakeConnection()
    event = AgentEvent(
        event_id="event-1",
        session_id="session-1",
        event_type="UserRequestReceived",
        payload={"request": "x"},
        provenance=[Provenance(source_type="test")],
    )
    connection.fetchall_rows = [
        (
            event.event_id,
            event.session_id,
            event.event_type,
            event.payload,
            [item.model_dump(mode="json") for item in event.provenance],
            event.graph_patch_ids,
            event.l6_node_ids,
            event.created_at,
        )
    ]
    log = PostgresAgentEventLog(
        dsn="postgresql://test",
        connection_factory=lambda _dsn: connection,
    )

    log.append(event)

    assert connection.commits == 1
    assert log.read_all()[0] == event


def test_neo4j_full_graph_store_replaces_l0_records() -> None:
    driver = FakeNeo4jDriver()
    records = BioEvoKGGraphRecords(graph_tier="G0", nodes=[make_node()], edges=[])

    write_id = Neo4jFullGraphStore(
        uri="bolt://test",
        user="neo4j",
        password="password",
        graph_profile_id="profile-1",
        driver=driver,
    ).replace_records(records)

    assert write_id.startswith("neo4j-import-")
    assert any("DETACH DELETE" in query for query, _params in driver.tx.calls)
    assert any("MERGE (n:BioEvoKGNode" in query for query, _params in driver.tx.calls)


def test_qdrant_graph_index_upserts_and_searches_node_vectors() -> None:
    client = FakeQdrantClient()
    index = QdrantGraphIndex(url="http://qdrant", client=client)

    index.upsert_node_embedding(
        collection_name="lattice",
        node=make_node(),
        vector=[0.1, 0.2],
        graph_profile_id="profile-1",
        graph_tier="G0",
    )
    hits = index.search(collection_name="lattice", query_vector=[0.1, 0.2])

    assert client.upserts[0]["points"][0]["id"] == "profile-1:G0:node-1"
    assert hits[0].point_id == "point-1"
    assert hits[0].payload == {"node_id": "node-1"}
