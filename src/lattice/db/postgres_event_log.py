from __future__ import annotations

import importlib
import json
from typing import Any

from lattice.runtime import AgentEvent, AgentEventLog


class PostgresStoreError(RuntimeError):
    pass


class PostgresSchemaManager:
    def __init__(self, *, dsn: str, connection_factory: Any | None = None) -> None:
        self.dsn = dsn
        self.connection_factory = connection_factory or _connect

    def create_core_tables(self) -> None:
        with self.connection_factory(self.dsn) as conn:
            with conn.cursor() as cur:
                for statement in CORE_TABLE_SQL:
                    cur.execute(statement)
            conn.commit()


class PostgresAgentEventLog(AgentEventLog):
    def __init__(self, *, dsn: str, connection_factory: Any | None = None) -> None:
        self.dsn = dsn
        self.connection_factory = connection_factory or _connect

    def append(self, event: AgentEvent) -> None:
        payload = event.model_dump(mode="json")
        with self.connection_factory(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO agent_events (
                        event_id, session_id, event_type, payload, provenance,
                        graph_patch_ids, l6_node_ids, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        event.event_id,
                        event.session_id,
                        event.event_type,
                        json.dumps(payload["payload"], ensure_ascii=False),
                        json.dumps(payload["provenance"], ensure_ascii=False),
                        json.dumps(payload["graph_patch_ids"], ensure_ascii=False),
                        json.dumps(payload["l6_node_ids"], ensure_ascii=False),
                        event.created_at,
                    ),
                )
            conn.commit()

    def read_all(self) -> list[AgentEvent]:
        with self.connection_factory(self.dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                    SELECT event_id, session_id, event_type, payload, provenance,
                           graph_patch_ids, l6_node_ids, created_at
                    FROM agent_events
                    ORDER BY created_at ASC, event_id ASC
                    """
            )
            rows = cur.fetchall()

        events: list[AgentEvent] = []
        for row in rows:
            events.append(
                AgentEvent.model_validate(
                    {
                        "event_id": row[0],
                        "session_id": row[1],
                        "event_type": row[2],
                        "payload": _load_json(row[3]),
                        "provenance": _load_json(row[4]),
                        "graph_patch_ids": _load_json(row[5]),
                        "l6_node_ids": _load_json(row[6]),
                        "created_at": row[7],
                    }
                )
            )
        return events


CORE_TABLE_SQL = [
    """
    CREATE TABLE IF NOT EXISTS graph_profiles (
        profile_id TEXT PRIMARY KEY,
        mode TEXT NOT NULL,
        schema_version TEXT NOT NULL,
        l0_source TEXT NOT NULL,
        l1_source TEXT NOT NULL,
        mutable BOOLEAN NOT NULL,
        builder_enabled BOOLEAN NOT NULL,
        evolution_enabled BOOLEAN NOT NULL,
        health_policy TEXT NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS agent_events (
        event_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        payload JSONB NOT NULL DEFAULT '{}'::jsonb,
        provenance JSONB NOT NULL,
        graph_patch_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
        l6_node_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
        created_at TIMESTAMPTZ NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS graph_patches (
        patch_id TEXT PRIMARY KEY,
        source_module TEXT NOT NULL,
        target_graph_tier TEXT NOT NULL,
        source_event_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
        nodes_to_add JSONB NOT NULL DEFAULT '[]'::jsonb,
        edges_to_add JSONB NOT NULL DEFAULT '[]'::jsonb,
        nodes_to_update JSONB NOT NULL DEFAULT '[]'::jsonb,
        edges_to_update JSONB NOT NULL DEFAULT '[]'::jsonb,
        lifecycle_transitions JSONB NOT NULL DEFAULT '[]'::jsonb,
        provenance JSONB NOT NULL,
        approval_status TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS patch_audit_reports (
        audit_id TEXT PRIMARY KEY,
        patch_id TEXT NOT NULL REFERENCES graph_patches(patch_id),
        status TEXT NOT NULL,
        blockers JSONB NOT NULL DEFAULT '[]'::jsonb,
        warnings JSONB NOT NULL DEFAULT '[]'::jsonb,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS toolcall_specs (
        toolcall_spec_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        tool_name TEXT NOT NULL,
        tool_version_policy TEXT NOT NULL,
        input_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
        output_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
        parameter_schema JSONB NOT NULL DEFAULT '{}'::jsonb,
        runtime_backend TEXT NOT NULL,
        permission_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
        parameter_source_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
        lifecycle_state TEXT NOT NULL,
        provenance JSONB NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id TEXT,
        status TEXT NOT NULL,
        active_graph_profile_id TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX IF NOT EXISTS agent_events_session_idx ON agent_events(session_id, created_at)",
    (
        "CREATE INDEX IF NOT EXISTS graph_patches_status_idx "
        "ON graph_patches(approval_status, risk_level)"
    ),
    "CREATE INDEX IF NOT EXISTS toolcall_specs_lifecycle_idx ON toolcall_specs(lifecycle_state)",
]


def _connect(dsn: str) -> Any:
    try:
        psycopg = importlib.import_module("psycopg")
    except ImportError as error:
        msg = "psycopg package is required for PostgreSQL adapters."
        raise PostgresStoreError(msg) from error
    return psycopg.connect(dsn)


def _load_json(value: Any) -> Any:
    if isinstance(value, str):
        return json.loads(value)
    return value
