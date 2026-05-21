from __future__ import annotations

from typing import Any, cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from typing_extensions import NotRequired, TypedDict

from helix.core import TaskFingerprinter
from helix.graph import HealthyGraphStore
from helix.permissions import PermissionDecision, PermissionGate
from helix.planning import WorkflowPathSearch, WorkflowSearchResult
from helix.projection import RuntimeViewProjector
from helix.runtime import AgentEvent, AgentEventLog
from helix.schemas import (
    Provenance,
    RuntimeGraphContext,
    TaskFingerprint,
    WorkflowAuditReport,
)
from helix.verification import WorkflowVerifier


class PlanOnlyState(TypedDict):
    request: str
    session_id: str
    status: NotRequired[str]
    task_fingerprint: NotRequired[TaskFingerprint]
    runtime_context: NotRequired[RuntimeGraphContext]
    workflow_search_result: NotRequired[WorkflowSearchResult]
    workflow_report: NotRequired[WorkflowAuditReport]
    permission_decision: NotRequired[PermissionDecision]
    response: NotRequired[str]


def build_plan_only_graph(
    *,
    healthy_graph_store: HealthyGraphStore | None = None,
) -> Any:
    graph = StateGraph(PlanOnlyState)
    graph.add_node("receive_request", receive_request)
    graph.add_node("fingerprint_task", fingerprint_task)
    graph.add_node(
        "project_runtime_context",
        lambda state: project_runtime_context(state, healthy_graph_store=healthy_graph_store),
    )
    graph.add_node("search_workflow_path", search_workflow_path)
    graph.add_node("verify_workflow", verify_workflow)
    graph.add_node("compile_aep", compile_aep)
    graph.add_node("permission_check", permission_check)
    graph.add_node("produce_response", produce_response)

    graph.add_edge(START, "receive_request")
    graph.add_edge("receive_request", "fingerprint_task")
    graph.add_edge("fingerprint_task", "project_runtime_context")
    graph.add_edge("project_runtime_context", "search_workflow_path")
    graph.add_edge("search_workflow_path", "verify_workflow")
    graph.add_edge("verify_workflow", "compile_aep")
    graph.add_edge("compile_aep", "permission_check")
    graph.add_edge("permission_check", "produce_response")
    graph.add_edge("produce_response", END)
    return graph.compile()


def run_plan_only(
    request: str,
    *,
    session_id: str | None = None,
    event_log: AgentEventLog | None = None,
    healthy_graph_store: HealthyGraphStore | None = None,
) -> PlanOnlyState:
    compiled = build_plan_only_graph(healthy_graph_store=healthy_graph_store)
    initial_state: PlanOnlyState = {
        "request": request,
        "session_id": session_id or f"session-{uuid4()}",
    }
    result = compiled.invoke(initial_state)
    final_state = cast(PlanOnlyState, result)
    if event_log is not None:
        append_plan_only_events(event_log, final_state)
    return final_state


def append_plan_only_events(event_log: AgentEventLog, state: PlanOnlyState) -> None:
    provenance = [Provenance(source_type="plan_only_orchestrator")]
    session_id = state["session_id"]
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type="UserRequestReceived",
            payload={"request": state["request"]},
            provenance=provenance,
        )
    )
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type="PlanModeEntered",
            payload={"mode": "plan_only"},
            provenance=provenance,
        )
    )
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type="TaskFingerprinted",
            payload=state["task_fingerprint"].model_dump(mode="json"),
            provenance=provenance,
        )
    )
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type="RuntimeGraphContextProjected",
            payload=state["runtime_context"].model_dump(mode="json"),
            provenance=provenance,
        )
    )
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type="WorkflowPathSelected",
            payload=state["workflow_search_result"].model_dump(mode="json"),
            provenance=provenance,
        )
    )
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type="WorkflowVerified",
            payload=state["workflow_report"].model_dump(mode="json"),
            provenance=provenance,
        )
    )
    event_log.append(
        AgentEvent(
            event_id=f"event-{uuid4()}",
            session_id=session_id,
            event_type="PermissionChecked",
            payload=state["permission_decision"].model_dump(mode="json"),
            provenance=provenance,
        )
    )


def receive_request(state: PlanOnlyState) -> PlanOnlyState:
    return {**state, "status": "received"}


def fingerprint_task(state: PlanOnlyState) -> PlanOnlyState:
    fingerprint = TaskFingerprinter().fingerprint(state["request"], user_id="local")
    return {**state, "status": "fingerprinted", "task_fingerprint": fingerprint}


def project_runtime_context(
    state: PlanOnlyState,
    *,
    healthy_graph_store: HealthyGraphStore | None = None,
) -> PlanOnlyState:
    fingerprint = state["task_fingerprint"]
    context = RuntimeViewProjector(healthy_graph_store=healthy_graph_store).project(fingerprint)
    return {**state, "status": "runtime_context_projected", "runtime_context": context}


def search_workflow_path(state: PlanOnlyState) -> PlanOnlyState:
    result = WorkflowPathSearch().search(state["task_fingerprint"], state["runtime_context"])
    return {**state, "status": "planning", "workflow_search_result": result}


def verify_workflow(state: PlanOnlyState) -> PlanOnlyState:
    search_result = state["workflow_search_result"]
    report = WorkflowVerifier().verify(search_result)
    return {**state, "status": "workflow_verified", "workflow_report": report}


def compile_aep(state: PlanOnlyState) -> PlanOnlyState:
    report = state["workflow_report"]
    if report.status == "blocked":
        return {**state, "status": "plan_blocked"}
    return {**state, "status": "plan_verified"}


def permission_check(state: PlanOnlyState) -> PlanOnlyState:
    decision = PermissionGate().check_execution(state["workflow_report"], mode="plan_only")
    return {**state, "permission_decision": decision}


def produce_response(state: PlanOnlyState) -> PlanOnlyState:
    report = state["workflow_report"]
    if report.status == "blocked":
        blocker_text = "; ".join(blocker.code for blocker in report.blockers)
        response = f"Plan blocked: {blocker_text}"
    else:
        response = "Plan verified."
    return {**state, "response": response}
