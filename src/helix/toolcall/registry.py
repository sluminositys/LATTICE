from __future__ import annotations

from collections.abc import Iterable

from helix.schemas import ToolCallSpec


class ToolCallRegistryError(ValueError):
    pass


class ToolCallRegistry:
    active_lifecycle_states = frozenset({"active_hot", "active_warm"})

    def __init__(self, specs: Iterable[ToolCallSpec] = ()) -> None:
        self._specs = {spec.toolcall_spec_id: spec for spec in specs}

    def get(self, toolcall_spec_id: str) -> ToolCallSpec | None:
        return self._specs.get(toolcall_spec_id)

    def require_active(self, toolcall_spec_id: str) -> ToolCallSpec:
        spec = self.get(toolcall_spec_id)
        if spec is None:
            msg = f"ToolCallSpec is not registered: {toolcall_spec_id}"
            raise ToolCallRegistryError(msg)

        if spec.lifecycle_state not in self.active_lifecycle_states:
            msg = (
                "ToolCallSpec is registered but not active: "
                f"{toolcall_spec_id} ({spec.lifecycle_state})"
            )
            raise ToolCallRegistryError(msg)
        return spec
