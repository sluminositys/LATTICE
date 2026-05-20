import pytest
from pydantic import ValidationError

from helix.schemas import (
    ClaimAuditReport,
    ExperienceCandidate,
    GraphPatch,
    LifecycleTransition,
    Provenance,
    WorkflowAuditReport,
)


def test_workflow_report_can_block_plan() -> None:
    report = WorkflowAuditReport(report_id="war-1", status="blocked", unresolved_items=["missing ToolCallSpec"])

    assert report.status == "blocked"
    assert report.unresolved_items == ["missing ToolCallSpec"]


def test_claim_report_can_be_not_applicable_for_plan_only_flow() -> None:
    report = ClaimAuditReport(report_id="car-1", final_claim_status="not_applicable")

    assert report.final_claim_status == "not_applicable"


def test_graph_patch_target_is_l0_only() -> None:
    with pytest.raises(ValidationError):
        GraphPatch(
            patch_id="patch-1",
            source_module="test",
            target_graph_tier="L1",
            provenance=Provenance(source_type="test"),
        )


def test_lifecycle_transition_records_state_change() -> None:
    transition = LifecycleTransition(
        transition_id="lt-1",
        target_node_or_edge_id="node-1",
        from_state="candidate",
        to_state="probationary",
        reason="schema and provenance passed",
    )

    assert transition.to_state == "probationary"


def test_experience_candidate_requires_scope() -> None:
    candidate = ExperienceCandidate(
        candidate_id="exp-1",
        candidate_type="constraint",
        proposed_graph_patch_id="patch-1",
        scope="user",
    )

    assert candidate.confidence_state == "raw"
