from lattice.schemas import AgenticExecutionStep, Provenance, StructuredObservation, ToolCallSpec
from lattice.toolcall import ToolCallDispatcher, ToolCallRegistry
from lattice.toolcall.backends import RuntimeBackend


class RecordingBackend:
    backend_name = "recording"

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        return StructuredObservation(
            observation_id="obs-1",
            toolcall_event_id=toolcall_event_id,
            status="success",
            outputs={"tool": spec.tool_name, "step": step.step_id},
            provenance=Provenance(source_type="test_backend"),
        )


def make_active_spec(runtime_backend: str = "recording") -> ToolCallSpec:
    return ToolCallSpec(
        toolcall_spec_id="toolcall-1",
        name="active tool",
        tool_name="active-tool",
        tool_version_policy="pinned",
        input_schema={"required": ["input_path"]},
        parameter_schema={"required": []},
        output_schema={"type": "object"},
        runtime_backend=runtime_backend,
        lifecycle_state="active_hot",
        provenance=Provenance(source_type="curator"),
    )


def make_step() -> AgenticExecutionStep:
    return AgenticExecutionStep(
        step_id="step-1",
        workflow_step_id="wf-step-1",
        toolcall_spec_id="toolcall-1",
        input_bindings={"input_path": "input.dat"},
    )


def test_dispatcher_returns_failure_when_validation_blocks() -> None:
    dispatcher = ToolCallDispatcher(registry=ToolCallRegistry())

    observation = dispatcher.dispatch(make_step())

    assert observation.status == "failure"
    assert observation.error_class == "ToolCallValidationFailed"


def test_dispatcher_fails_closed_without_backend() -> None:
    dispatcher = ToolCallDispatcher(registry=ToolCallRegistry([make_active_spec("cli")]))

    observation = dispatcher.dispatch(make_step())

    assert observation.status == "failure"
    assert observation.error_class == "RuntimeBackendUnavailable"
    assert observation.parsed_summary["reason"] == "No runtime backend registered: cli"


def test_dispatcher_executes_registered_backend() -> None:
    backend: RuntimeBackend = RecordingBackend()
    dispatcher = ToolCallDispatcher(
        registry=ToolCallRegistry([make_active_spec()]),
        backends={"recording": backend},
    )

    observation = dispatcher.dispatch(make_step())

    assert observation.status == "success"
    assert observation.outputs == {"tool": "active-tool", "step": "step-1"}
