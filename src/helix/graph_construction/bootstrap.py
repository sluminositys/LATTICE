from __future__ import annotations

from typing import Literal

from pydantic import Field

from helix.graph import FullGraphStore, GraphTierPolicy, GraphTierPolicyError
from helix.graph_health import MemoryHealthCompiler, MemoryHealthCompileReport
from helix.graph_patch import GraphPatchAuditor, PatchAuditReport
from helix.schemas import GraphPatch, GraphProfile, HelixBaseModel


class GraphConstructionBootstrapResult(HelixBaseModel):
    status: Literal["blocked", "applied_to_l0_and_compiled_l1"]
    patch_id: str
    audit_report: PatchAuditReport
    durable_write_id: str | None = None
    memory_health_report: MemoryHealthCompileReport | None = None
    notes: list[str] = Field(default_factory=list)


class GraphConstructionBootstrapWorkflow:
    """Bootstrap mode for HELIX's existing graph-construction workflow.

    This is not a new agent type. It composes the existing L0 GraphPatch write path and
    MemoryHealthCompiler so an initial graph build can run once a real database adapter exists.
    """

    def __init__(
        self,
        *,
        full_graph_store: FullGraphStore,
        graph_profile: GraphProfile | None = None,
        graph_tier_policy: GraphTierPolicy | None = None,
        auditor: GraphPatchAuditor | None = None,
        memory_health_compiler: MemoryHealthCompiler | None = None,
    ) -> None:
        self.full_graph_store = full_graph_store
        self.graph_profile = graph_profile
        self.graph_tier_policy = graph_tier_policy or GraphTierPolicy()
        self.auditor = auditor or GraphPatchAuditor()
        self.memory_health_compiler = memory_health_compiler or MemoryHealthCompiler()

    def run(self, patch: GraphPatch) -> GraphConstructionBootstrapResult:
        audit_report = self.auditor.audit(patch)
        if audit_report.status == "blocked":
            return GraphConstructionBootstrapResult(
                status="blocked",
                patch_id=patch.patch_id,
                audit_report=audit_report,
                notes=["Graph construction bootstrap stopped before L0 write."],
            )

        if self.graph_profile is not None:
            try:
                self.graph_tier_policy.assert_builder_allowed(self.graph_profile)
                self.graph_tier_policy.assert_graph_patch_writes_allowed(self.graph_profile)
            except GraphTierPolicyError as error:
                return GraphConstructionBootstrapResult(
                    status="blocked",
                    patch_id=patch.patch_id,
                    audit_report=audit_report,
                    notes=[str(error)],
                )

        durable_write_id = self.full_graph_store.apply_patch(patch)
        memory_health_report = self.memory_health_compiler.compile([patch])
        return GraphConstructionBootstrapResult(
            status="applied_to_l0_and_compiled_l1",
            patch_id=patch.patch_id,
            audit_report=audit_report,
            durable_write_id=durable_write_id,
            memory_health_report=memory_health_report,
            notes=[
                "GraphPatch applied to L0 through FullGraphStore.",
                "MemoryHealthCompiler ran after L0 write.",
            ],
        )
