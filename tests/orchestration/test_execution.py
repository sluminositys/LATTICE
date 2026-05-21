from __future__ import annotations

from typing import Any

from helix.orchestration import run_execution
from helix.schemas import (
    GraphContextSufficiencyReport,
    GraphPatch,
    Provenance,
    RuntimeGraphContext,
    TaskFingerprint,
    ToolCallSpec,
)
from helix.toolcall import PythonFunctionBackend


class FakeHealthyGraphStore:
    def project_runtime_context(self, fingerprint: TaskFingerprint) -> RuntimeGraphContext:
        spec = ToolCallSpec(
            toolcall_spec_id="toolcall-double",
            name="Double value",
            tool_name="double",
            tool_version_policy="pinned",
            input_schema={"required": ["value"]},
            output_schema={"required": ["doubled"]},
            runtime_backend="python_function",
            permission_policy={"function_name": "double"},
            lifecycle_state="active_hot",
            provenance=Provenance(source_type="test"),
        )
        return RuntimeGraphContext(
            graph_context_id="rgc-test",
            task_fingerprint_id=fingerprint.fingerprint_id,
            source_graph_tier="L1",
            G_workflow={
                "nodes": [
                    {
                        "node_id": "workflow-path-1",
                        "layer": "workflow",
                        "node_type": "WorkflowPath",
                        "lifecycle_state": "active_hot",
                        "attributes": {"step_ids": ["workflow-step-1"]},
                    },
                    {
                        "node_id": "workflow-step-1",
                        "layer": "workflow",
                        "node_type": "WorkflowStep",
                        "lifecycle_state": "active_hot",
                        "attributes": {
                            "workflow_path_id": "workflow-path-1",
                            "toolcall_spec_id": "toolcall-double",
                            "input_bindings": {"value": 2},
                        },
                    },
                ],
                "edges": [],
            },
            G_resource={
                "nodes": [
                    {
                        "node_id": "implementation-toolcall-double",
                        "layer": "implementation",
                        "node_type": "ToolCallSpec",
                        "lifecycle_state": "active_hot",
                        "attributes": spec.model_dump(mode="json"),
                    }
                ],
                "edges": [],
            },
            sufficiency_report=GraphContextSufficiencyReport(
                report_id="gcsr-test",
                status="sufficient",
            ),
        )

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return None


class FakeFullGraphStore:
    def __init__(self) -> None:
        self.applied_patch: GraphPatch | None = None

    def apply_patch(self, patch: GraphPatch) -> str:
        self.applied_patch = patch
        return "write-1"

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return None


def test_execution_flow_dispatches_toolcall_and_writes_experience_patch() -> None:
    full_store = FakeFullGraphStore()

    state = run_execution(
        "Run executable workflow",
        session_id="session-1",
        healthy_graph_store=FakeHealthyGraphStore(),
        full_graph_store=full_store,
        runtime_backends={
            "python_function": PythonFunctionBackend(
                {"double": lambda value: {"doubled": value * 2}}
            )
        },
    )

    assert state["status"] == "executed"
    assert state["permission_decision"].allowed is True
    assert state["observations"][0].status == "success"
    assert state["observations"][0].outputs == {"doubled": 4}
    assert state["graph_write_id"] == "write-1"
    assert full_store.applied_patch is not None
    assert full_store.applied_patch.nodes_to_add[0]["node_type"] == "ExecutionTrace"
