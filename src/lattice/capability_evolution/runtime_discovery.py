from __future__ import annotations

from typing import Any, Literal, Protocol

from pydantic import Field

from lattice.planning import WorkflowSearchResult
from lattice.schemas import (
    AgenticExecutionPlan,
    CapabilityGap,
    GraphPatch,
    LatticeBaseModel,
    RuntimeGraphContext,
    TaskFingerprint,
)

RuntimeDiscoveryStatus = Literal[
    "not_needed",
    "not_configured",
    "no_candidate",
    "candidate_plan_ready",
]


class RuntimeDiscoveryResult(LatticeBaseModel):
    status: RuntimeDiscoveryStatus
    reason: str | None = None
    execution_plan: AgenticExecutionPlan | None = None
    discovered_skills: list[dict[str, object]] = Field(default_factory=list)
    toolcall_specs: list[Any] = Field(default_factory=list)
    graph_patches: list[GraphPatch] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @property
    def has_executable_plan(self) -> bool:
        return self.execution_plan is not None


class RuntimeCapabilityDiscoverer(Protocol):
    """Runtime-side capability discovery port.

    Implementations can use external search, Biomni-like tool discovery, user-supplied
    adapters, or other agents. G2 remains a reference context; this port supplies a
    temporary execution plan when the projected graph does not already contain one.
    """

    def discover(
        self,
        *,
        request: str,
        fingerprint: TaskFingerprint,
        runtime_context: RuntimeGraphContext,
        workflow_search_result: WorkflowSearchResult,
        capability_gaps: list[CapabilityGap],
    ) -> RuntimeDiscoveryResult:
        """Return a temporary execution plan and candidate graph updates when available."""


class NoopRuntimeCapabilityDiscoverer:
    def discover(
        self,
        *,
        request: str,
        fingerprint: TaskFingerprint,
        runtime_context: RuntimeGraphContext,
        workflow_search_result: WorkflowSearchResult,
        capability_gaps: list[CapabilityGap],
    ) -> RuntimeDiscoveryResult:
        if not capability_gaps and _workflow_ready(workflow_search_result):
            return RuntimeDiscoveryResult(status="not_needed")
        return RuntimeDiscoveryResult(
            status="not_configured",
            reason="No runtime capability discoverer is configured.",
            notes=[
                "G2/G1 was treated as reference context only; execution needs an external "
                "runtime discoverer to propose a temporary plan."
            ],
        )


def _workflow_ready(search_result: WorkflowSearchResult) -> bool:
    return (
        search_result.selected_workflow_path_id is not None
        and not search_result.unresolved_requirements
    )
