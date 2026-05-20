from __future__ import annotations

from typing import Any, cast
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from typing_extensions import NotRequired, TypedDict

from helix.core import TaskFingerprinter
from helix.schemas import (
    Blocker,
    GraphContextSufficiencyReport,
    RuntimeGraphContext,
    TaskFingerprint,
    WorkflowAuditReport,
)


class PlanOnlyState(TypedDict):
    request: str
    session_id: str
    status: NotRequired[str]
    task_fingerprint: NotRequired[TaskFingerprint]
    runtime_context: NotRequired[RuntimeGraphContext]
    candidate_workflow_path_ids: NotRequired[list[str]]
    workflow_report: NotRequired[WorkflowAuditReport]
    permission_decision: NotRequired[str]
    response: NotRequired[str]


def build_plan_only_graph() -> Any:
    graph = StateGraph(PlanOnlyState)
    graph.add_node("receive_request", receive_request)
    graph.add_node("fingerprint_task", fingerprint_task)
    graph.add_node("project_runtime_context", project_runtime_context)
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


def run_plan_only(request: str, *, session_id: str | None = None) -> PlanOnlyState:
    compiled = build_plan_only_graph()
    initial_state: PlanOnlyState = {
        "request": request,
        "session_id": session_id or f"session-{uuid4()}",
    }
    result = compiled.invoke(initial_state)
    return cast(PlanOnlyState, result)


def receive_request(state: PlanOnlyState) -> PlanOnlyState:
    return {**state, "status": "received"}


def fingerprint_task(state: PlanOnlyState) -> PlanOnlyState:
    fingerprint = TaskFingerprinter().fingerprint(state["request"], user_id="local")
    return {**state, "status": "fingerprinted", "task_fingerprint": fingerprint}


def project_runtime_context(state: PlanOnlyState) -> PlanOnlyState:
    fingerprint = state["task_fingerprint"]
    report = GraphContextSufficiencyReport(
        report_id=f"gcsr-{uuid4()}",
        status="insufficient",
        missing_workflow_info=["no healthy graph store is configured"],
        missing_toolcall_info=["no active ToolCallSpec is registered"],
        missing_evidence_info=["no evidence view has been projected"],
        controlled_recall_required=False,
    )
    context = RuntimeGraphContext(
        graph_context_id=f"rgc-{uuid4()}",
        task_fingerprint_id=fingerprint.fingerprint_id,
        source_graph_tier="L1",
        sufficiency_report=report,
    )
    return {**state, "status": "runtime_context_projected", "runtime_context": context}


def search_workflow_path(state: PlanOnlyState) -> PlanOnlyState:
    return {**state, "status": "planning", "candidate_workflow_path_ids": []}


def verify_workflow(state: PlanOnlyState) -> PlanOnlyState:
    report = WorkflowAuditReport(
        report_id=f"war-{uuid4()}",
        status="blocked",
        blockers=[
            Blocker(
                code="NO_WORKFLOW_PATH",
                message="No verified workflow path is available in the runtime context.",
            ),
            Blocker(
                code="NO_TOOLCALL_SPEC",
                message="No active ToolCallSpec is registered for execution.",
            ),
        ],
        unresolved_items=["configure L1 graph store", "register real ToolCallSpec"],
    )
    return {**state, "status": "workflow_verified", "workflow_report": report}


def compile_aep(state: PlanOnlyState) -> PlanOnlyState:
    report = state["workflow_report"]
    if report.status == "blocked":
        return {**state, "status": "plan_blocked"}
    return {**state, "status": "plan_verified"}


def permission_check(state: PlanOnlyState) -> PlanOnlyState:
    if state["status"] == "plan_blocked":
        return {**state, "permission_decision": "not_applicable"}
    return {**state, "permission_decision": "plan_only"}


def produce_response(state: PlanOnlyState) -> PlanOnlyState:
    report = state["workflow_report"]
    if report.status == "blocked":
        blocker_text = "; ".join(blocker.code for blocker in report.blockers)
        response = f"Plan blocked: {blocker_text}"
    else:
        response = "Plan verified."
    return {**state, "response": response}
