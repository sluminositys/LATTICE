from __future__ import annotations

from typing import Any

from lattice.capability_evolution import RuntimeDiscoveryResult
from lattice.orchestration import run_execution
from lattice.schemas import (
    AgenticExecutionPlan,
    AgenticExecutionStep,
    GraphContextSufficiencyReport,
    GraphPatch,
    Provenance,
    RuntimeGraphContext,
    TaskFingerprint,
    ToolCallSpec,
)
from lattice.toolcall import PythonFunctionBackend


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
            source_graph_tier="G1",
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
                        "node_type": "ToolImplementationProfile",
                        "lifecycle_state": "active_hot",
                        "attributes": {
                            "agent_callability": {
                                "enabled": True,
                                "tool_call_specs": [spec.model_dump(mode="json")],
                            }
                        },
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
        self.applied_patches: list[GraphPatch] = []

    def apply_patch(self, patch: GraphPatch) -> str:
        self.applied_patch = patch
        self.applied_patches.append(patch)
        return f"write-{len(self.applied_patches)}"

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


class EmptyHealthyGraphStore:
    def __init__(self) -> None:
        self.applied_patches: list[GraphPatch] = []

    def project_runtime_context(self, fingerprint: TaskFingerprint) -> RuntimeGraphContext:
        return RuntimeGraphContext(
            graph_context_id="rgc-empty",
            task_fingerprint_id=fingerprint.fingerprint_id,
            source_graph_tier="G1",
            sufficiency_report=GraphContextSufficiencyReport(
                report_id="gcsr-empty",
                status="insufficient",
                missing_workflow_info=["no active workflow path nodes projected from G1"],
                missing_toolcall_info=["no active ToolCallSpec is registered"],
                controlled_recall_required=True,
                controlled_recall_reason="G1 lacks a ready path for this request.",
            ),
        )

    def materialize_from_patches(self, patches: list[GraphPatch]) -> str:
        self.applied_patches.extend(patches)
        return f"g1-write-{len(self.applied_patches)}"

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return None


class StaticRuntimeDiscoverer:
    def discover(
        self,
        *,
        request: str,
        fingerprint: TaskFingerprint,
        runtime_context: RuntimeGraphContext,
        workflow_search_result: Any,
        capability_gaps: list[Any],
    ) -> RuntimeDiscoveryResult:
        spec = ToolCallSpec(
            toolcall_spec_id="runtime-toolcall-increment",
            name="Runtime discovered increment",
            tool_name="increment",
            tool_version_policy="runtime_discovered",
            input_schema={"required": ["value"]},
            output_schema={"required": ["incremented"]},
            runtime_backend="python_function",
            permission_policy={"function_name": "increment"},
            lifecycle_state="active_warm",
            provenance=Provenance(source_type="runtime_capability_discovery"),
        )
        plan = AgenticExecutionPlan(
            plan_id="aep-runtime-discovered",
            task_fingerprint_id=fingerprint.fingerprint_id,
            runtime_graph_context_id=runtime_context.graph_context_id,
            selected_workflow_path_id="runtime-discovered-path",
            steps=[
                AgenticExecutionStep(
                    step_id="runtime-step-1",
                    workflow_step_id="runtime-step-1",
                    toolcall_spec_id=spec.toolcall_spec_id,
                    input_bindings={"value": 2},
                )
            ],
            provenance=[Provenance(source_type="runtime_capability_discovery")],
        )
        patch = GraphPatch(
            patch_id="patch-runtime-discovered",
            source_event_ids=["event-runtime-discovery"],
            source_module="RuntimeCapabilityDiscovery",
            nodes_to_add=[
                {
                    "node_id": "resource-tool-increment",
                    "layer": "resource",
                    "node_type": "Tool",
                    "canonical_name": "increment",
                    "attributes": {"tool_name": "increment", "request": request},
                    "lifecycle_state": "probationary",
                    "provenance": [{"source_type": "runtime_capability_discovery"}],
                },
                {
                    "node_id": "implementation-profile-increment",
                    "layer": "implementation",
                    "node_type": "ToolImplementationProfile",
                    "canonical_name": "increment implementation profile",
                    "attributes": {
                        "software_id": "resource-tool-increment",
                        "software_name": "increment",
                        "agent_callability": {
                            "enabled": True,
                            "tool_call_specs": [spec.model_dump(mode="json")],
                        },
                    },
                    "lifecycle_state": "probationary",
                    "provenance": [{"source_type": "runtime_capability_discovery"}],
                },
            ],
            provenance=Provenance(source_type="runtime_capability_discovery"),
            approval_status="proposed",
        )
        return RuntimeDiscoveryResult(
            status="candidate_plan_ready",
            reason="G2 had no mandatory path, so runtime discovery supplied a temporary plan.",
            execution_plan=plan,
            toolcall_specs=[spec],
            graph_patches=[patch],
        )


def test_execution_can_use_runtime_discovery_when_g2_has_no_path() -> None:
    full_store = FakeFullGraphStore()
    healthy_store = EmptyHealthyGraphStore()

    state = run_execution(
        "Use a tool not already present in G2",
        session_id="session-2",
        healthy_graph_store=healthy_store,
        full_graph_store=full_store,
        runtime_discoverer=StaticRuntimeDiscoverer(),
        runtime_backends={
            "python_function": PythonFunctionBackend(
                {"increment": lambda value: {"incremented": value + 1}}
            )
        },
    )

    assert state["status"] == "executed"
    assert state["workflow_report"].status == "pass"
    assert state["runtime_discovery_result"].status == "candidate_plan_ready"
    assert state["observations"][0].outputs == {"incremented": 3}
    assert [patch.patch_id for patch in full_store.applied_patches] == [
        "patch-runtime-discovered",
        state["experience_patch"].patch_id,
    ]
    assert [patch.target_graph_tier for patch in healthy_store.applied_patches] == ["G1", "G1"]
