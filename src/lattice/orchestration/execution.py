from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from typing_extensions import NotRequired, TypedDict

from lattice.capability_evolution import (
    CapabilityGapDetector,
    EvolutionAgent,
    EvolutionRequest,
    NoopRuntimeCapabilityDiscoverer,
    RuntimeCapabilityDiscoverer,
    RuntimeDiscoveryResult,
)
from lattice.core import TaskFingerprinter
from lattice.graph import FullGraphStore, HealthyGraphStore
from lattice.graph_health import MemoryHealthCompiler
from lattice.graph_patch import GraphPatchAuditor, PatchAuditReport
from lattice.permissions import PermissionDecision, PermissionGate
from lattice.planning import (
    AgenticExecutionPlanBuilder,
    WorkflowPathSearch,
    WorkflowSearchResult,
)
from lattice.projection import RuntimeViewProjector
from lattice.runtime import AgentEvent, AgentEventLog, AgentEventType
from lattice.schemas import (
    AgenticExecutionPlan,
    Blocker,
    CapabilityGap,
    GraphPatch,
    PermissionMode,
    Provenance,
    RuntimeGraphContext,
    StructuredObservation,
    TaskFingerprint,
    WorkflowAuditReport,
)
from lattice.toolcall import RuntimeBackend, ToolCallDispatcher, ToolCallRegistry
from lattice.verification import WorkflowVerifier


class ExecutionState(TypedDict):
    request: str
    session_id: str
    permission_mode: PermissionMode
    status: NotRequired[str]
    task_fingerprint: NotRequired[TaskFingerprint]
    runtime_context: NotRequired[RuntimeGraphContext]
    workflow_search_result: NotRequired[WorkflowSearchResult]
    capability_gaps: NotRequired[list[CapabilityGap]]
    evolution_request: NotRequired[EvolutionRequest]
    proposed_evolution_patch: NotRequired[GraphPatch | None]
    runtime_discovery_result: NotRequired[RuntimeDiscoveryResult]
    runtime_graph_patches: NotRequired[list[GraphPatch]]
    workflow_report: NotRequired[WorkflowAuditReport]
    execution_plan: NotRequired[AgenticExecutionPlan | None]
    permission_decision: NotRequired[PermissionDecision]
    observations: NotRequired[list[StructuredObservation]]
    experience_patch: NotRequired[GraphPatch | None]
    experience_patch_audit: NotRequired[PatchAuditReport | None]
    graph_patch_audits: NotRequired[list[PatchAuditReport]]
    graph_write_id: NotRequired[str | None]
    graph_update_write_ids: NotRequired[list[str]]
    healthy_graph_write_id: NotRequired[str | None]
    response: NotRequired[str]


def build_execution_graph(
    *,
    healthy_graph_store: HealthyGraphStore | None = None,
    full_graph_store: FullGraphStore | None = None,
    toolcall_registry: ToolCallRegistry | None = None,
    runtime_backends: Mapping[str, RuntimeBackend] | None = None,
    runtime_discoverer: RuntimeCapabilityDiscoverer | None = None,
    apply_experience_patch: bool = True,
) -> Any:
    graph = StateGraph(ExecutionState)
    graph.add_node("receive_request", receive_request)
    graph.add_node("fingerprint_task", fingerprint_task)
    graph.add_node(
        "project_runtime_context",
        lambda state: project_runtime_context(state, healthy_graph_store=healthy_graph_store),
    )
    graph.add_node("search_workflow_path", search_workflow_path)
    graph.add_node("detect_capability_gaps", detect_capability_gaps)
    graph.add_node("request_evolution", request_evolution)
    graph.add_node(
        "discover_runtime_capabilities",
        lambda state: discover_runtime_capabilities(
            state,
            runtime_discoverer=runtime_discoverer,
        ),
    )
    graph.add_node("verify_workflow", verify_workflow)
    graph.add_node("compile_execution_plan", compile_execution_plan)
    graph.add_node("permission_check", permission_check)
    graph.add_node(
        "execute_toolcalls",
        lambda state: execute_toolcalls(
            state,
            toolcall_registry=toolcall_registry,
            runtime_backends=runtime_backends,
        ),
    )
    graph.add_node("build_experience_patch", build_experience_patch)
    graph.add_node(
        "write_experience_patch",
        lambda state: write_experience_patch(
            state,
            full_graph_store=full_graph_store,
            healthy_graph_store=healthy_graph_store,
            apply_experience_patch=apply_experience_patch,
        ),
    )
    graph.add_node("produce_response", produce_response)

    graph.add_edge(START, "receive_request")
    graph.add_edge("receive_request", "fingerprint_task")
    graph.add_edge("fingerprint_task", "project_runtime_context")
    graph.add_edge("project_runtime_context", "search_workflow_path")
    graph.add_edge("search_workflow_path", "detect_capability_gaps")
    graph.add_edge("detect_capability_gaps", "request_evolution")
    graph.add_edge("request_evolution", "discover_runtime_capabilities")
    graph.add_edge("discover_runtime_capabilities", "verify_workflow")
    graph.add_edge("verify_workflow", "compile_execution_plan")
    graph.add_edge("compile_execution_plan", "permission_check")
    graph.add_edge("permission_check", "execute_toolcalls")
    graph.add_edge("execute_toolcalls", "build_experience_patch")
    graph.add_edge("build_experience_patch", "write_experience_patch")
    graph.add_edge("write_experience_patch", "produce_response")
    graph.add_edge("produce_response", END)
    return graph.compile()


def run_execution(
    request: str,
    *,
    session_id: str | None = None,
    event_log: AgentEventLog | None = None,
    permission_mode: PermissionMode = "safe_execute",
    healthy_graph_store: HealthyGraphStore | None = None,
    full_graph_store: FullGraphStore | None = None,
    toolcall_registry: ToolCallRegistry | None = None,
    runtime_backends: Mapping[str, RuntimeBackend] | None = None,
    runtime_discoverer: RuntimeCapabilityDiscoverer | None = None,
    apply_experience_patch: bool = True,
) -> ExecutionState:
    compiled = build_execution_graph(
        healthy_graph_store=healthy_graph_store,
        full_graph_store=full_graph_store,
        toolcall_registry=toolcall_registry,
        runtime_backends=runtime_backends,
        runtime_discoverer=runtime_discoverer,
        apply_experience_patch=apply_experience_patch,
    )
    initial_state: ExecutionState = {
        "request": request,
        "session_id": session_id or f"session-{uuid4()}",
        "permission_mode": permission_mode,
    }
    result = compiled.invoke(initial_state)
    final_state = cast(ExecutionState, result)
    if event_log is not None:
        append_execution_events(event_log, final_state)
    return final_state


def receive_request(state: ExecutionState) -> ExecutionState:
    return {**state, "status": "received"}


def fingerprint_task(state: ExecutionState) -> ExecutionState:
    fingerprint = TaskFingerprinter().fingerprint(state["request"], user_id="local")
    return {**state, "status": "fingerprinted", "task_fingerprint": fingerprint}


def project_runtime_context(
    state: ExecutionState,
    *,
    healthy_graph_store: HealthyGraphStore | None = None,
) -> ExecutionState:
    context = RuntimeViewProjector(healthy_graph_store=healthy_graph_store).project(
        state["task_fingerprint"]
    )
    return {**state, "status": "runtime_context_projected", "runtime_context": context}


def search_workflow_path(state: ExecutionState) -> ExecutionState:
    result = WorkflowPathSearch().search(state["task_fingerprint"], state["runtime_context"])
    return {**state, "status": "planning", "workflow_search_result": result}


def detect_capability_gaps(state: ExecutionState) -> ExecutionState:
    gaps = CapabilityGapDetector().detect(
        fingerprint=state["task_fingerprint"],
        runtime_context=state["runtime_context"],
        workflow_search_result=state["workflow_search_result"],
    )
    status = "capability_gap_detected" if gaps else state["status"]
    return {**state, "status": status, "capability_gaps": gaps}


def request_evolution(state: ExecutionState) -> ExecutionState:
    gaps = state.get("capability_gaps", [])
    if not gaps:
        return state
    source_event = AgentEvent(
        event_id=f"event-{uuid4()}",
        session_id=state["session_id"],
        event_type="CapabilityGapDetected",
        payload={"gap_ids": [gap.gap_id for gap in gaps]},
        provenance=[Provenance(source_type="execution_orchestrator")],
    )
    request, patch = EvolutionAgent().propose_gap_patch(
        gaps=gaps,
        source_events=[source_event],
    )
    return {
        **state,
        "status": "evolution_requested",
        "evolution_request": request,
        "proposed_evolution_patch": patch,
    }


def discover_runtime_capabilities(
    state: ExecutionState,
    *,
    runtime_discoverer: RuntimeCapabilityDiscoverer | None = None,
) -> ExecutionState:
    search_result = state["workflow_search_result"]
    workflow_ready = (
        search_result.selected_workflow_path_id is not None
        and not search_result.unresolved_requirements
    )
    discoverer = runtime_discoverer or NoopRuntimeCapabilityDiscoverer()
    result = discoverer.discover(
        request=state["request"],
        fingerprint=state["task_fingerprint"],
        runtime_context=state["runtime_context"],
        workflow_search_result=search_result,
        capability_gaps=state.get("capability_gaps", []),
    )
    update: ExecutionState = {
        **state,
        "runtime_discovery_result": result,
        "runtime_graph_patches": result.graph_patches,
    }
    if workflow_ready:
        return {**update, "status": state["status"]}
    if result.execution_plan is not None:
        return {
            **update,
            "status": "runtime_discovery_ready",
            "execution_plan": result.execution_plan,
        }
    return {**update, "status": "runtime_discovery_unavailable"}


def verify_workflow(state: ExecutionState) -> ExecutionState:
    discovery = state.get("runtime_discovery_result")
    if discovery is not None and discovery.execution_plan is not None:
        report = WorkflowAuditReport(
            report_id=f"war-{uuid4()}",
            status="pass",
            provenance=[Provenance(source_type="runtime_capability_discovery")],
        )
        return {**state, "status": "workflow_verified", "workflow_report": report}

    report = WorkflowVerifier().verify(state["workflow_search_result"])
    return {**state, "status": "workflow_verified", "workflow_report": report}


def compile_execution_plan(state: ExecutionState) -> ExecutionState:
    report = state["workflow_report"]
    if report.status == "blocked":
        return {**state, "status": "execution_blocked", "execution_plan": None}

    if state.get("execution_plan") is not None:
        return {**state, "status": "execution_plan_compiled"}

    plan = AgenticExecutionPlanBuilder().build(
        fingerprint=state["task_fingerprint"],
        runtime_context=state["runtime_context"],
        search_result=state["workflow_search_result"],
    )
    if plan is None:
        blocked_report = WorkflowAuditReport(
            report_id=f"war-{uuid4()}",
            status="blocked",
            blockers=[
                Blocker(
                    code="AEP_NOT_GENERATED",
                    message=(
                        "Workflow verification passed, but no executable AEP could be compiled."
                    ),
                )
            ],
            provenance=[Provenance(source_type="execution_orchestrator")],
        )
        return {
            **state,
            "status": "execution_blocked",
            "workflow_report": blocked_report,
            "execution_plan": None,
        }
    return {**state, "status": "execution_plan_compiled", "execution_plan": plan}


def permission_check(state: ExecutionState) -> ExecutionState:
    decision = PermissionGate().check_execution(
        state["workflow_report"],
        mode=state["permission_mode"],
    )
    return {**state, "permission_decision": decision}


def execute_toolcalls(
    state: ExecutionState,
    *,
    toolcall_registry: ToolCallRegistry | None = None,
    runtime_backends: Mapping[str, RuntimeBackend] | None = None,
) -> ExecutionState:
    decision = state["permission_decision"]
    plan = state.get("execution_plan")
    if not decision.allowed or plan is None:
        return {**state, "observations": [], "status": "execution_blocked"}

    registry = toolcall_registry or ToolCallRegistry.from_runtime_context(state["runtime_context"])
    discovery = state.get("runtime_discovery_result")
    if discovery is not None and discovery.toolcall_specs:
        registry = registry.with_specs(discovery.toolcall_specs)
    dispatcher = ToolCallDispatcher(registry=registry, backends=runtime_backends)
    observations = [dispatcher.dispatch(step) for step in plan.steps]
    status = (
        "executed"
        if all(obs.status == "success" for obs in observations)
        else "execution_failed"
    )
    return {**state, "observations": observations, "status": status}


def build_experience_patch(state: ExecutionState) -> ExecutionState:
    observations = state.get("observations", [])
    plan = state.get("execution_plan")
    if plan is None or not observations:
        return {**state, "experience_patch": None}

    source_event = AgentEvent(
        event_id=f"event-{uuid4()}",
        session_id=state["session_id"],
        event_type="ObservationParsed",
        payload={"observation_ids": [obs.observation_id for obs in observations]},
        provenance=[Provenance(source_type="execution_orchestrator")],
    )
    provenance = Provenance(source_type="execution_experience_recorder")
    patch = GraphPatch(
        patch_id=f"patch-{uuid4()}",
        source_event_ids=[source_event.event_id],
        source_module="ExecutionExperienceRecorder",
        provenance=provenance,
        approval_status="proposed",
    )
    trace_node_id = f"experience-execution-trace-{plan.plan_id}"
    patch.nodes_to_add.append(
        {
            "node_id": trace_node_id,
            "layer": "experience",
            "node_type": "ExecutionTrace",
            "canonical_name": f"Execution trace for {plan.plan_id}",
            "attributes": {
                "plan_id": plan.plan_id,
                "session_id": state["session_id"],
                "selected_workflow_path_id": plan.selected_workflow_path_id,
                "status": state["status"],
                "observation_ids": [obs.observation_id for obs in observations],
            },
            "lifecycle_state": "candidate",
            "provenance": [provenance.model_dump(mode="json")],
        }
    )
    for observation in observations:
        event_node_id = f"experience-toolcall-event-{observation.toolcall_event_id}"
        patch.nodes_to_add.append(
            {
                "node_id": event_node_id,
                "layer": "experience",
                "node_type": "ToolCallEvent",
                "canonical_name": f"ToolCall {observation.toolcall_event_id}",
                "attributes": observation.model_dump(mode="json"),
                "lifecycle_state": "candidate",
                "provenance": [observation.provenance.model_dump(mode="json")],
            }
        )
        patch.edges_to_add.append(
            {
                "edge_id": f"edge-{uuid4()}",
                "edge_type": "CALLED_TOOLCALL",
                "source_node_id": trace_node_id,
                "target_node_id": event_node_id,
                "source_layer": "experience",
                "target_layer": "experience",
                "source_type": "execution_experience_recorder",
                "lifecycle_state": "candidate",
                "provenance": [provenance.model_dump(mode="json")],
            }
        )
        if observation.status != "success":
            failure_node_id = f"experience-failure-{observation.observation_id}"
            patch.nodes_to_add.append(
                {
                    "node_id": failure_node_id,
                    "layer": "experience",
                    "node_type": "FailureCondition",
                    "canonical_name": observation.error_class or "ToolCall failure",
                    "attributes": {
                        "toolcall_event_id": observation.toolcall_event_id,
                        "error_class": observation.error_class,
                        "summary": observation.parsed_summary,
                    },
                    "lifecycle_state": "candidate",
                    "provenance": [observation.provenance.model_dump(mode="json")],
                }
            )
            patch.edges_to_add.append(
                {
                    "edge_id": f"edge-{uuid4()}",
                    "edge_type": "FAILED_WITH",
                    "source_node_id": event_node_id,
                    "target_node_id": failure_node_id,
                    "source_layer": "experience",
                    "target_layer": "experience",
                    "source_type": "execution_experience_recorder",
                    "lifecycle_state": "candidate",
                    "provenance": [provenance.model_dump(mode="json")],
                }
            )
    return {**state, "experience_patch": patch}


def write_experience_patch(
    state: ExecutionState,
    *,
    full_graph_store: FullGraphStore | None = None,
    healthy_graph_store: HealthyGraphStore | None = None,
    apply_experience_patch: bool = True,
) -> ExecutionState:
    experience_patch = state.get("experience_patch")
    patches = [*state.get("runtime_graph_patches", [])]
    if experience_patch is not None:
        patches.append(experience_patch)

    if not patches:
        return {
            **state,
            "experience_patch_audit": None,
            "graph_patch_audits": [],
            "graph_write_id": None,
            "graph_update_write_ids": [],
            "healthy_graph_write_id": None,
        }

    audits: list[PatchAuditReport] = []
    write_ids: list[str] = []
    written_patches: list[GraphPatch] = []
    experience_audit: PatchAuditReport | None = None
    auditor = GraphPatchAuditor()
    for patch in patches:
        audit = auditor.audit(patch)
        audits.append(audit)
        if experience_patch is not None and patch.patch_id == experience_patch.patch_id:
            experience_audit = audit
        if audit.status == "blocked" or full_graph_store is None or not apply_experience_patch:
            continue
        approved_patch = patch.model_copy(update={"approval_status": "approved"})
        write_ids.append(full_graph_store.apply_patch(approved_patch))
        written_patches.append(approved_patch)

    healthy_graph_write_id = _materialize_healthy_graph(
        healthy_graph_store=healthy_graph_store,
        written_patches=written_patches,
    )
    return {
        **state,
        "experience_patch_audit": experience_audit,
        "graph_patch_audits": audits,
        "graph_write_id": write_ids[-1] if write_ids else None,
        "graph_update_write_ids": write_ids,
        "healthy_graph_write_id": healthy_graph_write_id,
    }


def _materialize_healthy_graph(
    *,
    healthy_graph_store: HealthyGraphStore | None,
    written_patches: list[GraphPatch],
) -> str | None:
    if healthy_graph_store is None or not written_patches:
        return None
    materialize = getattr(healthy_graph_store, "materialize_from_patches", None)
    if materialize is None:
        return None

    report = MemoryHealthCompiler().compile(written_patches)
    if not report.materialized_l1:
        return None

    g1_patches = [
        patch.model_copy(
            update={
                "patch_id": f"{patch.patch_id}-g1",
                "target_graph_tier": "G1",
                "source_module": "MemoryHealthCompiler",
                "approval_status": "approved",
            }
        )
        for patch in written_patches
    ]
    return str(materialize(g1_patches))


def produce_response(state: ExecutionState) -> ExecutionState:
    if state.get("execution_plan") is None:
        blockers = "; ".join(blocker.code for blocker in state["workflow_report"].blockers)
        return {**state, "response": f"Execution blocked: {blockers}"}

    observations = state.get("observations", [])
    failed = [obs for obs in observations if obs.status != "success"]
    if failed:
        return {
            **state,
            "response": f"Execution completed with {len(failed)} failed ToolCall(s).",
        }
    return {**state, "response": f"Execution completed with {len(observations)} ToolCall(s)."}


def append_execution_events(event_log: AgentEventLog, state: ExecutionState) -> None:
    provenance = [Provenance(source_type="execution_orchestrator")]
    session_id = state["session_id"]
    _append(
        event_log,
        session_id,
        "UserRequestReceived",
        {"request": state["request"]},
        provenance,
    )
    _append(
        event_log,
        session_id,
        "TaskFingerprinted",
        state["task_fingerprint"].model_dump(mode="json"),
        provenance,
    )
    _append(
        event_log,
        session_id,
        "RuntimeGraphContextProjected",
        state["runtime_context"].model_dump(mode="json"),
        provenance,
    )
    _append(
        event_log,
        session_id,
        "WorkflowPathSelected",
        state["workflow_search_result"].model_dump(mode="json"),
        provenance,
    )
    for gap in state.get("capability_gaps", []):
        _append(
            event_log,
            session_id,
            "CapabilityGapDetected",
            gap.model_dump(mode="json"),
            provenance,
        )
    if state.get("evolution_request") is not None:
        proposed_patch = state.get("proposed_evolution_patch")
        _append(
            event_log,
            session_id,
            "EvolutionRequested",
            state["evolution_request"].model_dump(mode="json"),
            provenance,
            graph_patch_ids=[proposed_patch.patch_id] if proposed_patch is not None else [],
        )
    if state.get("runtime_discovery_result") is not None:
        discovery = state["runtime_discovery_result"]
        _append(
            event_log,
            session_id,
            "RuntimeCapabilityDiscoveryCompleted",
            discovery.model_dump(mode="json"),
            provenance,
            graph_patch_ids=[patch.patch_id for patch in discovery.graph_patches],
        )
    _append(
        event_log,
        session_id,
        "WorkflowVerified",
        state["workflow_report"].model_dump(mode="json"),
        provenance,
    )
    _append(
        event_log,
        session_id,
        "PermissionChecked",
        state["permission_decision"].model_dump(mode="json"),
        provenance,
    )
    for observation in state.get("observations", []):
        event_type: AgentEventType = (
            "ToolCallCompleted" if observation.status == "success" else "ToolCallFailed"
        )
        _append(
            event_log,
            session_id,
            event_type,
            observation.model_dump(mode="json"),
            provenance,
        )
    patch = state.get("experience_patch")
    if patch is not None:
        l6_node_ids = [
            str(node["node_id"])
            for node in patch.nodes_to_add
            if node.get("layer") == "experience" and "node_id" in node
        ]
        _append(
            event_log,
            session_id,
            "ExperienceCandidateCreated",
            {"patch_id": patch.patch_id},
            provenance,
            graph_patch_ids=[patch.patch_id],
            l6_node_ids=l6_node_ids,
        )
        _append(
            event_log,
            session_id,
            "GraphPatchProposed",
            patch.model_dump(mode="json"),
            provenance,
            graph_patch_ids=[patch.patch_id],
            l6_node_ids=l6_node_ids,
        )
    if state.get("graph_write_id") is not None and patch is not None:
        _append(
            event_log,
            session_id,
            "GraphPatchWritten",
            {"patch_id": patch.patch_id, "write_id": state["graph_write_id"]},
            provenance,
            graph_patch_ids=[patch.patch_id],
        )


def _append(
    event_log: AgentEventLog,
    session_id: str,
    event_type: AgentEventType,
    payload: dict[str, Any],
    provenance: list[Provenance],
    *,
    graph_patch_ids: list[str] | None = None,
    l6_node_ids: list[str] | None = None,
) -> None:
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type=event_type,
            payload=payload,
            provenance=provenance,
            graph_patch_ids=graph_patch_ids or [],
            l6_node_ids=l6_node_ids or [],
        )
    )
