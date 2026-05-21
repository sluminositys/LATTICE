from __future__ import annotations

import sys

from helix.schemas import AgenticExecutionStep, Provenance, ToolCallSpec
from helix.toolcall import CliBackend, DatabaseApiBackend, PythonFunctionBackend


def make_step() -> AgenticExecutionStep:
    return AgenticExecutionStep(
        step_id="step-1",
        workflow_step_id="workflow-step-1",
        toolcall_spec_id="toolcall-1",
        input_bindings={"message": "hello"},
        parameter_bindings={"suffix": "world"},
    )


def make_spec(*, runtime_backend: str, permission_policy: dict[str, object]) -> ToolCallSpec:
    return ToolCallSpec(
        toolcall_spec_id="toolcall-1",
        name="test tool",
        tool_name="test-tool",
        tool_version_policy="pinned",
        input_schema={"required": ["message"]},
        output_schema={"type": "object"},
        runtime_backend=runtime_backend,
        permission_policy=permission_policy,
        lifecycle_state="active_hot",
        provenance=Provenance(source_type="test"),
    )


def test_python_function_backend_executes_registered_function() -> None:
    backend = PythonFunctionBackend(
        {"join": lambda message, suffix: {"joined": f"{message} {suffix}"}}
    )
    spec = make_spec(
        runtime_backend="python_function",
        permission_policy={"function_name": "join"},
    )

    observation = backend.execute(step=make_step(), spec=spec, toolcall_event_id="event-1")

    assert observation.status == "success"
    assert observation.outputs == {"joined": "hello world"}


def test_cli_backend_blocks_unregistered_executable() -> None:
    backend = CliBackend(allowed_executables={"allowed"})
    spec = make_spec(
        runtime_backend="cli",
        permission_policy={"command": ["blocked", "--version"]},
    )

    observation = backend.execute(step=make_step(), spec=spec, toolcall_event_id="event-1")

    assert observation.status == "failure"
    assert observation.error_class == "CliExecutableNotAllowed"


def test_cli_backend_resolves_inputs_without_shell() -> None:
    backend = CliBackend(allowed_executables={sys.executable}, timeout_seconds=10)
    spec = make_spec(
        runtime_backend="cli",
        permission_policy={
            "command": [sys.executable, "-c", "print('{{inputs.message}} {{params.suffix}}')"]
        },
    )

    observation = backend.execute(step=make_step(), spec=spec, toolcall_event_id="event-1")

    assert observation.status == "success"
    assert observation.outputs["stdout"].strip() == "hello world"


def test_database_api_backend_uses_registered_query_handler() -> None:
    backend = DatabaseApiBackend(
        {"lookup": lambda message, suffix: {"record": f"{message}-{suffix}"}}
    )
    spec = make_spec(
        runtime_backend="database_api",
        permission_policy={"query_handler": "lookup"},
    )

    observation = backend.execute(step=make_step(), spec=spec, toolcall_event_id="event-1")

    assert observation.status == "success"
    assert observation.outputs == {"record": "hello-world"}
