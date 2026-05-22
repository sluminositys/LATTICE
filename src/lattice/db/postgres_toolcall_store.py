from __future__ import annotations

import json
from typing import Any

from lattice.db.postgres_event_log import _connect, _load_json
from lattice.schemas import Provenance, ToolCallSpec


class PostgresToolCallSpecStore:
    def __init__(self, *, dsn: str, connection_factory: Any | None = None) -> None:
        self.dsn = dsn
        self.connection_factory = connection_factory or _connect

    def upsert(self, spec: ToolCallSpec) -> None:
        payload = spec.model_dump(mode="json")
        with self.connection_factory(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO toolcall_specs (
                        toolcall_spec_id, name, tool_name, tool_version_policy,
                        input_schema, output_schema, parameter_schema, runtime_backend,
                        permission_policy, parameter_source_policy, lifecycle_state, provenance
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (toolcall_spec_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        tool_name = EXCLUDED.tool_name,
                        tool_version_policy = EXCLUDED.tool_version_policy,
                        input_schema = EXCLUDED.input_schema,
                        output_schema = EXCLUDED.output_schema,
                        parameter_schema = EXCLUDED.parameter_schema,
                        runtime_backend = EXCLUDED.runtime_backend,
                        permission_policy = EXCLUDED.permission_policy,
                        parameter_source_policy = EXCLUDED.parameter_source_policy,
                        lifecycle_state = EXCLUDED.lifecycle_state,
                        provenance = EXCLUDED.provenance
                    """,
                    (
                        spec.toolcall_spec_id,
                        spec.name,
                        spec.tool_name,
                        spec.tool_version_policy,
                        json.dumps(payload["input_schema"], ensure_ascii=False),
                        json.dumps(payload["output_schema"], ensure_ascii=False),
                        json.dumps(payload["parameter_schema"], ensure_ascii=False),
                        spec.runtime_backend,
                        json.dumps(payload["permission_policy"], ensure_ascii=False),
                        json.dumps(payload["parameter_source_policy"], ensure_ascii=False),
                        spec.lifecycle_state,
                        json.dumps(payload["provenance"], ensure_ascii=False),
                    ),
                )
            conn.commit()

    def get(self, toolcall_spec_id: str) -> ToolCallSpec | None:
        with self.connection_factory(self.dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                    SELECT toolcall_spec_id, name, tool_name, tool_version_policy,
                           input_schema, output_schema, parameter_schema, runtime_backend,
                           permission_policy, parameter_source_policy, lifecycle_state, provenance
                    FROM toolcall_specs
                    WHERE toolcall_spec_id = %s
                    """,
                (toolcall_spec_id,),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return _row_to_spec(row)

    def list_active(self) -> list[ToolCallSpec]:
        with self.connection_factory(self.dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                    SELECT toolcall_spec_id, name, tool_name, tool_version_policy,
                           input_schema, output_schema, parameter_schema, runtime_backend,
                           permission_policy, parameter_source_policy, lifecycle_state, provenance
                    FROM toolcall_specs
                    WHERE lifecycle_state IN ('active_hot', 'active_warm')
                    ORDER BY toolcall_spec_id ASC
                    """
            )
            rows = cur.fetchall()
        return [_row_to_spec(row) for row in rows]


def _row_to_spec(row: Any) -> ToolCallSpec:
    provenance = _load_json(row[11])
    return ToolCallSpec(
        toolcall_spec_id=row[0],
        name=row[1],
        tool_name=row[2],
        tool_version_policy=row[3],
        input_schema=_load_json(row[4]),
        output_schema=_load_json(row[5]),
        parameter_schema=_load_json(row[6]),
        runtime_backend=row[7],
        permission_policy=_load_json(row[8]),
        parameter_source_policy=_load_json(row[9]),
        lifecycle_state=row[10],
        provenance=Provenance.model_validate(provenance),
    )
