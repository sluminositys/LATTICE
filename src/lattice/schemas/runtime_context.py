from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from lattice.schemas.common import LatticeBaseModel, Provenance


class GraphContextSufficiencyReport(LatticeBaseModel):
    report_id: str
    status: Literal["sufficient", "insufficient", "sufficient_with_warnings"]
    missing_task_info: list[str] = Field(default_factory=list)
    missing_workflow_info: list[str] = Field(default_factory=list)
    missing_toolcall_info: list[str] = Field(default_factory=list)
    missing_evidence_info: list[str] = Field(default_factory=list)
    missing_experience_info: list[str] = Field(default_factory=list)
    controlled_recall_required: bool = False
    controlled_recall_reason: str | None = None


class RuntimeGraphContext(LatticeBaseModel):
    graph_context_id: str
    task_fingerprint_id: str
    source_graph_tier: Literal["L1", "L1_plus_controlled_L0_recall"]
    G_task: dict[str, Any] = Field(default_factory=dict)
    G_evidence: dict[str, Any] = Field(default_factory=dict)
    G_workflow: dict[str, Any] = Field(default_factory=dict)
    G_resource: dict[str, Any] = Field(default_factory=dict)
    G_experience_preference: dict[str, Any] = Field(default_factory=dict)
    temporary_candidates: list[dict[str, Any]] = Field(default_factory=list)
    sufficiency_report: GraphContextSufficiencyReport
    provenance: list[Provenance] = Field(default_factory=list)
