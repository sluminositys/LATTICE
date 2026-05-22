import pytest

from lattice.schemas import LifecycleState, Provenance, ToolCallSpec
from lattice.toolcall import ToolCallRegistry, ToolCallRegistryError


def make_toolcall_spec(lifecycle_state: LifecycleState) -> ToolCallSpec:
    return ToolCallSpec(
        toolcall_spec_id="toolcall-1",
        name="real registered tool",
        tool_name="registered-tool",
        tool_version_policy="pinned",
        runtime_backend="cli",
        lifecycle_state=lifecycle_state,
        provenance=Provenance(source_type="curator"),
    )


def test_registry_rejects_unregistered_toolcall() -> None:
    with pytest.raises(ToolCallRegistryError):
        ToolCallRegistry().require_active("missing")


def test_registry_rejects_candidate_toolcall() -> None:
    registry = ToolCallRegistry([make_toolcall_spec("candidate")])

    with pytest.raises(ToolCallRegistryError):
        registry.require_active("toolcall-1")


def test_registry_returns_active_toolcall() -> None:
    spec = make_toolcall_spec("active_warm")
    registry = ToolCallRegistry([spec])

    assert registry.require_active("toolcall-1") is spec
