from lattice.planning import WorkflowSearchResult
from lattice.verification import WorkflowVerifier


def test_workflow_verifier_blocks_without_selected_path() -> None:
    report = WorkflowVerifier().verify(
        WorkflowSearchResult(
            unresolved_requirements=[
                "no active L5 skill view has been projected",
                "no healthy graph store is configured",
            ]
        )
    )

    assert report.status == "blocked"
    assert [blocker.code for blocker in report.blockers] == ["NO_WORKFLOW_PATH"]


def test_workflow_verifier_passes_selected_path() -> None:
    report = WorkflowVerifier().verify(
        WorkflowSearchResult(candidate_path_ids=["path-1"], selected_workflow_path_id="path-1")
    )

    assert report.status == "pass"
