from __future__ import annotations

from typing import Literal

from pydantic import Field

from helix.schemas.common import Blocker, HelixBaseModel, Provenance, WarningItem


class WorkflowAuditReport(HelixBaseModel):
    report_id: str
    status: Literal["pass", "warning", "blocked", "repaired"]
    blockers: list[Blocker] = Field(default_factory=list)
    warnings: list[WarningItem] = Field(default_factory=list)
    repairs_applied: list[str] = Field(default_factory=list)
    triggered_constraints: list[str] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)


class ClaimAuditReport(HelixBaseModel):
    report_id: str
    claims: list[str] = Field(default_factory=list)
    evidence_links: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    contradicted_claims: list[str] = Field(default_factory=list)
    final_claim_status: Literal[
        "supported",
        "weakly_supported",
        "unsupported",
        "contradicted",
        "not_applicable",
    ]
    provenance: list[Provenance] = Field(default_factory=list)
