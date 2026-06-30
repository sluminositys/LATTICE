from lattice.core import TaskFingerprinter
from lattice.planning import WorkflowPathSearch
from lattice.projection import RuntimeViewProjector


def test_workflow_search_blocks_on_insufficient_context() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Plan requested workflow")
    context = RuntimeViewProjector().project(fingerprint)
    result = WorkflowPathSearch().search(fingerprint, context)

    assert result.candidate_path_ids == []
    assert result.selected_workflow_path_id is None
    assert "no active L5 skill view has been projected" in result.unresolved_requirements
