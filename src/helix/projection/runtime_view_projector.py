from __future__ import annotations

from uuid import uuid4

from helix.graph import HealthyGraphStore
from helix.schemas import GraphContextSufficiencyReport, RuntimeGraphContext, TaskFingerprint


class RuntimeViewProjector:
    def __init__(self, healthy_graph_store: HealthyGraphStore | None = None) -> None:
        self.healthy_graph_store = healthy_graph_store

    def project(self, fingerprint: TaskFingerprint) -> RuntimeGraphContext:
        if self.healthy_graph_store is not None:
            return self.healthy_graph_store.project_runtime_context(fingerprint)

        report = GraphContextSufficiencyReport(
            report_id=f"gcsr-{uuid4()}",
            status="insufficient",
            missing_workflow_info=["no healthy graph store is configured"],
            missing_toolcall_info=["no active ToolCallSpec is registered"],
            missing_evidence_info=["no evidence view has been projected"],
            controlled_recall_required=False,
        )
        return RuntimeGraphContext(
            graph_context_id=f"rgc-{uuid4()}",
            task_fingerprint_id=fingerprint.fingerprint_id,
            source_graph_tier="L1",
            sufficiency_report=report,
        )
