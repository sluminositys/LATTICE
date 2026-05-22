from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from typing import Any, Literal, Protocol
from uuid import uuid4

from lattice.schemas import AgenticExecutionStep, Provenance, StructuredObservation, ToolCallSpec


class RuntimeBackend(Protocol):
    backend_name: str

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        """Execute a validated ToolCall step and return a structured observation."""


class PythonFunctionBackend:
    backend_name = "python_function"

    def __init__(self, functions: Mapping[str, Callable[..., Any]]) -> None:
        self.functions = dict(functions)

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        function_name = str(spec.permission_policy.get("function_name") or spec.tool_name)
        function = self.functions.get(function_name)
        if function is None:
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="PythonFunctionUnavailable",
                reason=f"No registered Python function: {function_name}",
            )

        try:
            outputs = function(**step.input_bindings, **step.parameter_bindings)
        except Exception as error:  # pragma: no cover - defensive boundary
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class=error.__class__.__name__,
                reason=str(error),
            )
        if not isinstance(outputs, dict):
            outputs = {"result": outputs}
        return _backend_success(
            toolcall_event_id=toolcall_event_id,
            backend_name=self.backend_name,
            outputs=outputs,
        )


class CliBackend:
    backend_name = "cli"

    def __init__(
        self,
        *,
        allowed_executables: set[str] | None = None,
        timeout_seconds: int = 600,
    ) -> None:
        self.allowed_executables = allowed_executables
        self.timeout_seconds = timeout_seconds

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        command = spec.permission_policy.get("command")
        if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="InvalidCliCommandPolicy",
                reason="CLI backend requires permission_policy.command as list[str].",
            )
        if not command:
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="InvalidCliCommandPolicy",
                reason="CLI command cannot be empty.",
            )
        executable = command[0]
        if self.allowed_executables is not None and executable not in self.allowed_executables:
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="CliExecutableNotAllowed",
                reason=f"Executable is not allowed: {executable}",
            )

        resolved_command = [
            _resolve_token(item, step.input_bindings, step.parameter_bindings) for item in command
        ]
        try:
            completed = subprocess.run(
                resolved_command,
                capture_output=True,
                check=False,
                shell=False,
                text=True,
                timeout=self.timeout_seconds,
            )
        except Exception as error:  # pragma: no cover - defensive boundary
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class=error.__class__.__name__,
                reason=str(error),
            )

        status: Literal["success", "failure"] = (
            "success" if completed.returncode == 0 else "failure"
        )
        return StructuredObservation(
            observation_id=f"obs-{uuid4()}",
            toolcall_event_id=toolcall_event_id,
            status=status,
            outputs={
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "returncode": completed.returncode,
                "command": resolved_command,
            },
            error_class=None if completed.returncode == 0 else "CliProcessFailed",
            parsed_summary={"returncode": completed.returncode},
            provenance=Provenance(source_type=f"{self.backend_name}_backend"),
        )


class RestApiBackend:
    backend_name = "rest_api"

    def __init__(self, *, allowed_hosts: set[str] | None = None, timeout_seconds: int = 60) -> None:
        self.allowed_hosts = allowed_hosts
        self.timeout_seconds = timeout_seconds

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        method = str(spec.permission_policy.get("method", "GET")).upper()
        url = spec.permission_policy.get("url")
        if not isinstance(url, str):
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="InvalidRestPolicy",
                reason="REST backend requires permission_policy.url.",
            )
        host = urllib.parse.urlparse(url).netloc
        if self.allowed_hosts is not None and host not in self.allowed_hosts:
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="RestHostNotAllowed",
                reason=f"Host is not allowed: {host}",
            )

        body = None
        headers = {"Content-Type": "application/json"}
        if method in {"POST", "PUT", "PATCH"}:
            body = json.dumps(
                {"inputs": step.input_bindings, "parameters": step.parameter_bindings}
            ).encode("utf-8")
        request = urllib.request.Request(url=url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                return _backend_success(
                    toolcall_event_id=toolcall_event_id,
                    backend_name=self.backend_name,
                    outputs={
                        "status_code": response.status,
                        "body": _try_json(raw),
                    },
                )
        except urllib.error.HTTPError as error:
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="RestHttpError",
                reason=f"{error.code}: {error.reason}",
            )
        except Exception as error:  # pragma: no cover - defensive boundary
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class=error.__class__.__name__,
                reason=str(error),
            )


class DatabaseApiBackend:
    backend_name = "database_api"

    def __init__(self, query_handlers: Mapping[str, Callable[..., dict[str, Any]]]) -> None:
        self.query_handlers = dict(query_handlers)

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        handler_name = str(spec.permission_policy.get("query_handler") or spec.tool_name)
        handler = self.query_handlers.get(handler_name)
        if handler is None:
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="DatabaseQueryHandlerUnavailable",
                reason=f"No registered database query handler: {handler_name}",
            )
        try:
            outputs = handler(**step.input_bindings, **step.parameter_bindings)
        except Exception as error:  # pragma: no cover - defensive boundary
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class=error.__class__.__name__,
                reason=str(error),
            )
        return _backend_success(
            toolcall_event_id=toolcall_event_id,
            backend_name=self.backend_name,
            outputs=outputs,
        )


class ContainerizedCliBackend(CliBackend):
    backend_name = "containerized_cli"

    def __init__(
        self,
        *,
        allowed_images: set[str] | None = None,
        timeout_seconds: int = 1200,
    ) -> None:
        super().__init__(allowed_executables={"docker"}, timeout_seconds=timeout_seconds)
        self.allowed_images = allowed_images

    def execute(
        self,
        *,
        step: AgenticExecutionStep,
        spec: ToolCallSpec,
        toolcall_event_id: str,
    ) -> StructuredObservation:
        image = spec.permission_policy.get("container_image")
        command = spec.permission_policy.get("container_command")
        if not isinstance(image, str) or not isinstance(command, list):
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="InvalidContainerPolicy",
                reason="Container backend requires container_image and container_command.",
            )
        if self.allowed_images is not None and image not in self.allowed_images:
            return _backend_failure(
                toolcall_event_id=toolcall_event_id,
                backend_name=self.backend_name,
                error_class="ContainerImageNotAllowed",
                reason=f"Container image is not allowed: {image}",
            )
        spec_for_cli = spec.model_copy(
            update={
                "permission_policy": {
                    "command": ["docker", "run", "--rm", image, *command],
                }
            }
        )
        return super().execute(step=step, spec=spec_for_cli, toolcall_event_id=toolcall_event_id)


def _backend_success(
    *,
    toolcall_event_id: str,
    backend_name: str,
    outputs: dict[str, Any],
) -> StructuredObservation:
    return StructuredObservation(
        observation_id=f"obs-{uuid4()}",
        toolcall_event_id=toolcall_event_id,
        status="success",
        outputs=outputs,
        provenance=Provenance(source_type=f"{backend_name}_backend"),
    )


def _backend_failure(
    *,
    toolcall_event_id: str,
    backend_name: str,
    error_class: str,
    reason: str,
) -> StructuredObservation:
    return StructuredObservation(
        observation_id=f"obs-{uuid4()}",
        toolcall_event_id=toolcall_event_id,
        status="failure",
        error_class=error_class,
        parsed_summary={"reason": reason},
        provenance=Provenance(source_type=f"{backend_name}_backend"),
    )


def _resolve_token(
    token: str,
    inputs: Mapping[str, Any],
    parameters: Mapping[str, Any],
) -> str:
    resolved = token
    for key, value in inputs.items():
        resolved = resolved.replace(f"{{{{inputs.{key}}}}}", str(value))
    for key, value in parameters.items():
        resolved = resolved.replace(f"{{{{params.{key}}}}}", str(value))
    return resolved


def _try_json(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw
