import pytest
from pydantic import ValidationError

from helix.capability_evolution import CandidateTool, CandidateWorkflow, ToolCallSpecBuilder
from helix.schemas import Provenance
from helix.toolcall import ToolCallRegistry, ToolCallRegistryError


def make_candidate_tool() -> CandidateTool:
    return CandidateTool(
        candidate_id="candidate-tool",
        name="Candidate tool",
        tool_name="candidate-tool",
        runtime_backend="cli",
        input_schema={"required": ["input_path"]},
        output_schema={"type": "object"},
        provenance=Provenance(source_type="curator"),
    )


def test_candidate_tool_cannot_start_active() -> None:
    with pytest.raises(ValidationError):
        CandidateTool(
            candidate_id="candidate-tool",
            name="Candidate tool",
            tool_name="candidate-tool",
            runtime_backend="cli",
            input_schema={"required": ["input_path"]},
            output_schema={"type": "object"},
            lifecycle_state="active_hot",
            provenance=Provenance(source_type="curator"),
        )


def test_candidate_workflow_cannot_start_active() -> None:
    with pytest.raises(ValidationError):
        CandidateWorkflow(
            candidate_id="workflow-1",
            name="workflow candidate",
            workflow_steps=[],
            lifecycle_state="active_warm",
            provenance=Provenance(source_type="curator"),
        )


def test_toolcall_spec_builder_preserves_candidate_lifecycle() -> None:
    spec = ToolCallSpecBuilder().build_from_candidate_tool(make_candidate_tool())

    assert spec.lifecycle_state == "candidate"
    with pytest.raises(ToolCallRegistryError):
        ToolCallRegistry([spec]).require_active(spec.toolcall_spec_id)
