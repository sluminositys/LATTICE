from helix.core import TaskFingerprinter
from helix.projection import GraphContextSufficiencyChecker, RuntimeViewProjector


def test_sufficiency_checker_reads_runtime_context_report() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Plan requested workflow")
    context = RuntimeViewProjector().project(fingerprint)
    checker = GraphContextSufficiencyChecker()

    assert checker.check(context).status == "insufficient"
    assert checker.requires_controlled_recall(context) is False
