from lattice.schemas import AgenticExecutionStep, Provenance, ToolCallSpec
from lattice.toolcall import ToolCallRegistry, ToolCallValidator


def make_active_spec() -> ToolCallSpec:
    return ToolCallSpec(
        toolcall_spec_id="toolcall-1",
        name="active tool",
        tool_name="active-tool",
        tool_version_policy="pinned",
        input_schema={"required": ["input_path"]},
        parameter_schema={"required": ["threads"]},
        output_schema={"type": "object"},
        runtime_backend="cli",
        lifecycle_state="active_warm",
        provenance=Provenance(source_type="curator"),
    )


def test_toolcall_validator_blocks_unregistered_spec() -> None:
    step = AgenticExecutionStep(
        step_id="step-1",
        workflow_step_id="wf-step-1",
        toolcall_spec_id="missing",
    )

    report = ToolCallValidator(ToolCallRegistry()).validate_step(step)

    assert report.status == "blocked"
    assert report.blockers == ["ToolCallSpec is not registered: missing"]


def test_toolcall_validator_blocks_missing_required_bindings() -> None:
    step = AgenticExecutionStep(
        step_id="step-1",
        workflow_step_id="wf-step-1",
        toolcall_spec_id="toolcall-1",
        input_bindings={},
        parameter_bindings={"threads": 4},
    )
    registry = ToolCallRegistry([make_active_spec()])

    report = ToolCallValidator(registry).validate_step(step)

    assert report.status == "blocked"
    assert report.blockers == ["Missing required input binding: input_path"]


def test_toolcall_validator_passes_complete_step() -> None:
    step = AgenticExecutionStep(
        step_id="step-1",
        workflow_step_id="wf-step-1",
        toolcall_spec_id="toolcall-1",
        input_bindings={"input_path": "input.dat"},
        parameter_bindings={"threads": 4},
    )
    registry = ToolCallRegistry([make_active_spec()])

    report = ToolCallValidator(registry).validate_step(step)

    assert report.status == "pass"
    assert report.blockers == []
