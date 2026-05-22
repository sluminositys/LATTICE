from lattice.config import load_settings


def test_loads_base_dev_settings() -> None:
    settings = load_settings("config")

    assert settings.app_name == "LATTICE"
    assert settings.environment == "dev"
    assert settings.logging.level == "DEBUG"
    assert settings.permissions.default_mode == "plan_only"
    assert settings.tool_registry.allow_unregistered_tools is False
    assert settings.graph_profiles.active_profile_id is None
    assert settings.graph_profiles.profiles == {}
    assert settings.databases.neo4j_uri is None


def test_environment_overrides(monkeypatch) -> None:
    monkeypatch.setenv("LATTICE_GRAPH__CONTROLLED_RECALL_LIMIT", "7")
    monkeypatch.setenv("LATTICE_LOGGING__JSON_LOGS", "true")
    monkeypatch.setenv("LATTICE_DATABASES__POSTGRES_DSN", "postgresql://localhost/lattice")

    settings = load_settings("config")

    assert settings.graph.controlled_recall_limit == 7
    assert settings.logging.json_logs is True
    assert settings.databases.postgres_dsn == "postgresql://localhost/lattice"
