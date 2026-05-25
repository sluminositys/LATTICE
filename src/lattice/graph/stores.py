from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Protocol

from lattice.schemas import GraphPatch, RuntimeGraphContext, TaskFingerprint


class FullGraphStore(Protocol):
    """G0 store port. New graph knowledge enters through audited GraphPatch only."""

    def apply_patch(self, patch: GraphPatch) -> str:
        """Apply an audited patch to G0 and return a durable write id."""

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Return a G0 node by id when present."""


class HealthyGraphStore(Protocol):
    """G1 store port. Runtime reads G1 and compiler-approved updates can refresh it."""

    def project_runtime_context(self, fingerprint: TaskFingerprint) -> RuntimeGraphContext:
        """Project a G2 runtime context from healthy graph content."""

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """Return a G1 node by id when present."""

    def materialize_from_patches(self, patches: Iterable[GraphPatch]) -> str:
        """Refresh G1 from audited G0 patches and return a durable write id."""
