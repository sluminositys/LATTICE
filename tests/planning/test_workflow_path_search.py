from helix.core import TaskFingerprinter
from helix.planning import WorkflowPathSearch
from helix.projection import RuntimeViewProjector


def test_workflow_search_blocks_on_insufficient_context() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Plan RNA-seq QC")
    context = RuntimeViewProjector().project(fingerprint)
    result = WorkflowPathSearch().search(fingerprint, context)

    assert result.candidate_path_ids == []
    assert result.selected_workflow_path_id is None
    assert "no active ToolCallSpec is registered" in result.unresolved_requirements
