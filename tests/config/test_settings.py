from helix.config import load_settings


def test_loads_base_dev_settings() -> None:
    settings = load_settings("config")

    assert settings.app_name == "HELIX"
    assert settings.environment == "dev"
    assert settings.logging.level == "DEBUG"
    assert settings.permissions.default_mode == "plan_only"
    assert settings.tool_registry.allow_unregistered_tools is False


def test_environment_overrides(monkeypatch) -> None:
    monkeypatch.setenv("HELIX_GRAPH__CONTROLLED_RECALL_LIMIT", "7")
    monkeypatch.setenv("HELIX_LOGGING__JSON_LOGS", "true")

    settings = load_settings("config")

    assert settings.graph.controlled_recall_limit == 7
    assert settings.logging.json_logs is True
