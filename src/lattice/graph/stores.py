from __future__ import annotations

from typing import Any, Protocol

from lattice.schemas import GraphPatch, RuntimeGraphContext, TaskFingerprint


class FullGraphStore(Protocol):
    """G0 store port. New graph knowledge enters through audited GraphPatch only."""

    def apply_patch(self, patch: GraphPatch) -> str:
        """Apply an audited patch to G0 and return a durable write id."""

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Return a G0 node by id when present."""


class HealthyGraphStore(Protocol):
    """G1 store port. G1 is a compiler output and has no direct write API."""

    def project_runtime_context(self, fingerprint: TaskFingerprint) -> RuntimeGraphContext:
        """Project a G2 runtime context from healthy graph content."""

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Return a G1 node by id when present."""
