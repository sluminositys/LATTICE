from __future__ import annotations

from typing import Literal

from pydantic import Field

from lattice.graph import GraphTierPolicy, GraphTierPolicyError
from lattice.graph_patch.patch_validator import GraphPatchValidator
from lattice.schemas import GraphPatch, LatticeBaseModel


class PatchAuditReport(LatticeBaseModel):
    patch_id: str
    status: Literal["pass", "blocked"]
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GraphPatchAuditor:
    def __init__(
        self,
        graph_tier_policy: GraphTierPolicy | None = None,
        validator: GraphPatchValidator | None = None,
    ) -> None:
        self.graph_tier_policy = graph_tier_policy or GraphTierPolicy()
        self.validator = validator or GraphPatchValidator()

    def audit(self, patch: GraphPatch) -> PatchAuditReport:
        blockers: list[str] = []

        try:
            self.graph_tier_policy.assert_patch_targets_l0(patch)
        except GraphTierPolicyError as error:
            blockers.append(str(error))

        if not patch.source_event_ids:
            blockers.append("GraphPatch must reference at least one source event.")

        validation = self.validator.validate(patch)
        blockers.extend(validation.blockers)

        if blockers:
            return PatchAuditReport(
                patch_id=patch.patch_id,
                status="blocked",
                blockers=blockers,
                warnings=validation.warnings,
            )

        return PatchAuditReport(
            patch_id=patch.patch_id,
            status="pass",
            warnings=validation.warnings,
        )
