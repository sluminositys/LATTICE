from helix.core import TaskFingerprinter
from helix.projection import RuntimeViewProjector


def test_runtime_view_projector_reports_insufficient_without_l1_store() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Plan requested workflow")
    context = RuntimeViewProjector().project(fingerprint)

    assert context.task_fingerprint_id == fingerprint.fingerprint_id
    assert context.source_graph_tier == "L1"
    assert context.sufficiency_report.status == "insufficient"
    assert (
        "no healthy graph store is configured"
        in context.sufficiency_report.missing_workflow_info
    )
