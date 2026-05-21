from __future__ import annotations

from collections.abc import Sequence
from uuid import uuid4

from helix.schemas import ClaimAuditReport, Provenance


class ClaimVerifier:
    def verify(
        self,
        claims: Sequence[str],
        *,
        provenance: list[Provenance] | None = None,
    ) -> ClaimAuditReport:
        if not claims:
            return ClaimAuditReport(
                report_id=f"car-{uuid4()}",
                final_claim_status="not_applicable",
                provenance=provenance or [],
            )

        return ClaimAuditReport(
            report_id=f"car-{uuid4()}",
            claims=list(claims),
            unsupported_claims=list(claims),
            final_claim_status="unsupported",
            provenance=provenance or [],
        )
