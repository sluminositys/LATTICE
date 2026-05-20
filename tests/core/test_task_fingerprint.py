from helix.core import TaskFingerprinter


def test_task_fingerprinter_is_conservative_about_unknown_fields() -> None:
    fingerprint = TaskFingerprinter().fingerprint("  Analyze ATAC-seq peaks  ", user_id="user-1")

    assert fingerprint.task == "Analyze ATAC-seq peaks"
    assert fingerprint.user_id == "user-1"
    assert fingerprint.execution_intent == "plan_only"
    assert fingerprint.task_category == "unclassified"
    assert "task_category" in fingerprint.ambiguity_items
