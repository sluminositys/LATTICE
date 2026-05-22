from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from lattice.schemas import GraphProfile

PermissionMode = Literal[
    "plan_only",
    "read_only",
    "safe_execute",
    "ask_before_execute",
    "admin_approved_execute",
    "graph_write_review",
    "headless_fail_closed",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModelSettings(StrictModel):
    chat_provider: str = "not_configured"
    chat_model: str = "not_configured"
    embedding_provider: str = "not_configured"
    embedding_model: str = "not_configured"


class RuntimePathSettings(StrictModel):
    output_root: Path = Path("D:/workspace/codex")
    runs_subdir: str = "runs"
    logs_subdir: str = "logs"
    artifacts_subdir: str = "artifacts"
    scratch_subdir: str = "scratch"


class DatabaseSettings(StrictModel):
    neo4j_uri: str | None = None
    neo4j_user: str | None = None
    neo4j_password: str | None = None
    neo4j_database: str | None = None
    postgres_dsn: str | None = None
    qdrant_url: str | None = None
    qdrant_api_key: str | None = None
    qdrant_prefer_grpc: bool = False


class GraphSettings(StrictModel):
    l0_backend: str = "protocol_only"
    l1_backend: str = "protocol_only"
    l0_dsn: str | None = None
    l1_dsn: str | None = None
    controlled_recall_limit: int = Field(default=20, ge=0)


class GraphProfilesSettings(StrictModel):
    active_profile_id: str | None = None
    profiles: dict[str, GraphProfile] = Field(default_factory=dict)


class ToolRegistrySettings(StrictModel):
    registry_path: Path = Path("config/tool_registry.yaml")
    allow_unregistered_tools: bool = False
    active_specs: list[str] = Field(default_factory=list)


class PermissionSettings(StrictModel):
    default_mode: PermissionMode = "plan_only"
    fail_closed: bool = True
    require_graph_write_review: bool = True
    blocked_modes: list[PermissionMode] = Field(default_factory=list)


LifecycleState = Literal[
    "candidate",
    "probationary",
    "active_hot",
    "active_warm",
    "cold_reference",
    "deprecated_reference",
    "quarantined",
    "retired",
    "tombstoned",
]


class GraphHealthSettings(StrictModel):
    compiler_mode: Literal["manual", "scheduled", "disabled"] = "manual"
    lifecycle_policy: str = "policy_driven"
    allow_direct_l1_write: bool = False
    lifecycle_states: list[LifecycleState] = Field(default_factory=list)


class LoggingSettings(StrictModel):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    json_logs: bool = False


class LatticeSettings(StrictModel):
    app_name: str = "LATTICE"
    environment: str = "dev"
    models: ModelSettings = Field(default_factory=ModelSettings)
    runtime_paths: RuntimePathSettings = Field(default_factory=RuntimePathSettings)
    databases: DatabaseSettings = Field(default_factory=DatabaseSettings)
    graph: GraphSettings = Field(default_factory=GraphSettings)
    graph_profiles: GraphProfilesSettings = Field(default_factory=GraphProfilesSettings)
    tool_registry: ToolRegistrySettings = Field(default_factory=ToolRegistrySettings)
    permissions: PermissionSettings = Field(default_factory=PermissionSettings)
    graph_health: GraphHealthSettings = Field(default_factory=GraphHealthSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)


def load_settings(
    config_dir: str | Path = "config",
    *,
    environment: str | None = None,
) -> LatticeSettings:
    """Load LATTICE settings from YAML files plus `LATTICE_` environment overrides."""

    config_path = Path(config_dir)
    env_name = environment or os.getenv("LATTICE_ENV") or "dev"
    files = [
        "base.yaml",
        "logging.yaml",
        "permissions.yaml",
        "graph_health.yaml",
        "graph_profiles.yaml",
        "tool_registry.yaml",
        f"{env_name}.yaml",
    ]

    raw: dict[str, Any] = {}
    for file_name in files:
        file_path = config_path / file_name
        if file_path.exists():
            raw = _deep_merge(raw, _read_yaml(file_path))

    raw = _deep_merge(raw, _env_overrides())
    return LatticeSettings.model_validate(raw)


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        msg = f"Config file must contain a YAML mapping: {path}"
        raise ValueError(msg)
    return loaded


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _env_overrides() -> dict[str, Any]:
    prefix = "LATTICE_"
    overrides: dict[str, Any] = {}
    for key, value in os.environ.items():
        if not key.startswith(prefix) or key == "LATTICE_ENV":
            continue

        path = key.removeprefix(prefix).lower().split("__")
        cursor = overrides
        for part in path[:-1]:
            next_cursor = cursor.setdefault(part, {})
            if not isinstance(next_cursor, dict):
                msg = f"Conflicting environment override path: {key}"
                raise ValueError(msg)
            cursor = next_cursor
        cursor[path[-1]] = _parse_env_value(value)
    return overrides


def _parse_env_value(value: str) -> Any:
    normalized = value.strip()
    lowered = normalized.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"none", "null"}:
        return None
    if normalized.isdecimal():
        return int(normalized)
    return value
