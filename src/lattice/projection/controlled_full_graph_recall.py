from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal, Protocol

from pydantic import Field

from lattice.schemas import LatticeBaseModel, LifecycleState, Provenance, TaskFingerprint

RecallCandidateStatus = Literal[
    "temporary_runtime_candidate",
    "candidate_tool",
    "candidate_workflow",
    "candidate_evidence",
    "candidate_constraint",
    "candidate_repair_action",
    "review_only",
    "blocked",
]


class FullGraphRecallCandidate(LatticeBaseModel):
    candidate_id: str
    candidate_status: RecallCandidateStatus
    lifecycle_state: LifecycleState
    payload: dict[str, Any] = Field(default_factory=dict)
    source_path: str
    lifecycle_history: list[str] = Field(default_factory=list)
    provenance: list[Provenance] = Field(default_factory=list)
    weak_candidate: bool = False
    blocked_reason: str | None = None


class ControlledFullGraphRecallResult(LatticeBaseModel):
    candidates: list[FullGraphRecallCandidate] = Field(default_factory=list)
    blocked_candidates: list[FullGraphRecallCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class FullGraphRecallProvider(Protocol):
    def recall_candidates(
        self,
        *,
        fingerprint: TaskFingerprint,
        reasons: Sequence[str],
        limit: int,
    ) -> list[FullGraphRecallCandidate]:
        """Return L0 recall candidates before LATTICE recall safety rules are applied."""


class ControlledFullGraphRecall:
    allowed_candidate_statuses: set[RecallCandidateStatus] = {
        "temporary_runtime_candidate",
        "candidate_tool",
        "candidate_workflow",
        "candidate_evidence",
        "candidate_constraint",
        "candidate_repair_action",
    }

    def __init__(self, provider: FullGraphRecallProvider, *, limit: int = 20) -> None:
        self.provider = provider
        self.limit = limit

    def recall(
        self,
        *,
        fingerprint: TaskFingerprint,
        reasons: Sequence[str],
    ) -> ControlledFullGraphRecallResult:
        raw_candidates = self.provider.recall_candidates(
            fingerprint=fingerprint,
            reasons=reasons,
            limit=self.limit,
        )
        candidates: list[FullGraphRecallCandidate] = []
        blocked_candidates: list[FullGraphRecallCandidate] = []
        warnings: list[str] = []

        for raw_candidate in raw_candidates[: self.limit]:
            candidate = _apply_recall_safety(raw_candidate)
            if candidate.candidate_status == "blocked":
                blocked_candidates.append(candidate)
            else:
                if (
                    candidate.candidate_status not in self.allowed_candidate_statuses
                    and candidate.candidate_status != "review_only"
                ):
                    candidate = candidate.model_copy(
                        update={
                            "candidate_status": "review_only",
                            "blocked_reason": "candidate status is review-only for planning",
                        }
                    )
                    warnings.append(f"Candidate moved to review_only: {candidate.candidate_id}")
                candidates.append(candidate)

        return ControlledFullGraphRecallResult(
            candidates=candidates,
            blocked_candidates=blocked_candidates,
            warnings=warnings,
        )


def _apply_recall_safety(candidate: FullGraphRecallCandidate) -> FullGraphRecallCandidate:
    if candidate.lifecycle_state == "tombstoned":
        return candidate.model_copy(
            update={
                "candidate_status": "blocked",
                "blocked_reason": "tombstoned content cannot enter planning",
            }
        )

    if candidate.lifecycle_state == "quarantined":
        return candidate.model_copy(
            update={
                "candidate_status": "review_only",
                "blocked_reason": "quarantined content is review-only",
            }
        )

    if candidate.lifecycle_state == "deprecated_reference":
        return candidate.model_copy(
            update={
                "candidate_status": "review_only",
                "blocked_reason": "deprecated content is only for trace or reproduction context",
            }
        )

    if not candidate.provenance:
        return candidate.model_copy(update={"weak_candidate": True})

    return candidate
