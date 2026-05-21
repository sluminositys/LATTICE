from collections.abc import Sequence

from helix.core import TaskFingerprinter
from helix.projection import ControlledFullGraphRecall, FullGraphRecallCandidate
from helix.schemas import Provenance, TaskFingerprint


class StaticRecallProvider:
    def __init__(self, candidates: list[FullGraphRecallCandidate]) -> None:
        self.candidates = candidates

    def recall_candidates(
        self,
        *,
        fingerprint: TaskFingerprint,
        reasons: Sequence[str],
        limit: int,
    ) -> list[FullGraphRecallCandidate]:
        return self.candidates[:limit]


def test_controlled_recall_blocks_tombstoned_content() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Need historical workflow")
    recall = ControlledFullGraphRecall(
        StaticRecallProvider(
            [
                FullGraphRecallCandidate(
                    candidate_id="candidate-1",
                    candidate_status="candidate_workflow",
                    lifecycle_state="tombstoned",
                    source_path="l0/workflow/candidate-1",
                    lifecycle_history=["candidate", "tombstoned"],
                    provenance=[Provenance(source_type="l0")],
                )
            ]
        )
    )

    result = recall.recall(fingerprint=fingerprint, reasons=["insufficient context"])

    assert result.candidates == []
    assert result.blocked_candidates[0].blocked_reason == "tombstoned content cannot enter planning"


def test_controlled_recall_marks_quarantined_as_review_only() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Need old tool")
    recall = ControlledFullGraphRecall(
        StaticRecallProvider(
            [
                FullGraphRecallCandidate(
                    candidate_id="candidate-1",
                    candidate_status="candidate_tool",
                    lifecycle_state="quarantined",
                    source_path="l0/tool/candidate-1",
                    lifecycle_history=["candidate", "quarantined"],
                    provenance=[Provenance(source_type="l0")],
                )
            ]
        )
    )

    result = recall.recall(fingerprint=fingerprint, reasons=["special capability"])

    assert result.candidates[0].candidate_status == "review_only"
    assert result.candidates[0].blocked_reason == "quarantined content is review-only"


def test_controlled_recall_marks_missing_provenance_as_weak_candidate() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Need cold evidence")
    recall = ControlledFullGraphRecall(
        StaticRecallProvider(
            [
                FullGraphRecallCandidate(
                    candidate_id="candidate-1",
                    candidate_status="candidate_evidence",
                    lifecycle_state="cold_reference",
                    source_path="l0/evidence/candidate-1",
                    lifecycle_history=["candidate", "cold_reference"],
                )
            ]
        )
    )

    result = recall.recall(fingerprint=fingerprint, reasons=["missing evidence"])

    assert result.candidates[0].weak_candidate is True
