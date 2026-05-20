from helix.schemas import (
    GraphContextSufficiencyReport,
    RuntimeGraphContext,
    TaskFingerprint,
)


def test_task_fingerprint_defaults_to_plan_only() -> None:
    fingerprint = TaskFingerprint(
        fingerprint_id="tf-1",
        user_id="user-1",
        task="Build a workflow for RNA-seq quality control",
        task_category="rna_seq_qc",
        data_types=["fastq"],
    )

    assert fingerprint.execution_intent == "plan_only"
    assert fingerprint.input_formats == []


def test_runtime_context_can_report_insufficient_graph_context() -> None:
    report = GraphContextSufficiencyReport(
        report_id="gcsr-1",
        status="insufficient",
        missing_workflow_info=["no verified workflow path"],
        controlled_recall_required=True,
        controlled_recall_reason="L1 lacks candidate workflows",
    )
    context = RuntimeGraphContext(
        graph_context_id="rgc-1",
        task_fingerprint_id="tf-1",
        source_graph_tier="L1",
        sufficiency_report=report,
    )

    assert context.sufficiency_report.status == "insufficient"
    assert context.temporary_candidates == []
