from helix.orchestration import run_plan_only


def test_plan_only_flow_blocks_without_graph_or_tool_specs() -> None:
    state = run_plan_only("Plan RNA-seq QC workflow", session_id="session-1")

    assert state["status"] == "plan_blocked"
    assert state["task_fingerprint"].execution_intent == "plan_only"
    assert state["runtime_context"].sufficiency_report.status == "insufficient"
    assert state["workflow_report"].status == "blocked"
    assert state["permission_decision"].allowed is False
    assert state["permission_decision"].blocked_by == ["NO_WORKFLOW_PATH", "NO_TOOLCALL_SPEC"]
    assert state["response"] == "Plan blocked: NO_WORKFLOW_PATH; NO_TOOLCALL_SPEC"
