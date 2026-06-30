from lattice.orchestration import run_plan_only
from lattice.runtime import FileAgentEventLog


def test_plan_only_flow_blocks_without_graph() -> None:
    state = run_plan_only("Plan requested workflow", session_id="session-1")

    assert state["status"] == "plan_blocked"
    assert state["task_fingerprint"].execution_intent == "plan_only"
    assert state["runtime_context"].sufficiency_report.status == "insufficient"
    assert state["workflow_report"].status == "blocked"
    assert state["permission_decision"].allowed is False
    assert state["permission_decision"].blocked_by == ["NO_WORKFLOW_PATH"]
    assert state["response"] == "Plan blocked: NO_WORKFLOW_PATH"


def test_plan_only_flow_appends_event_log(tmp_path) -> None:
    event_log = FileAgentEventLog(tmp_path / "events.jsonl")

    run_plan_only("Plan requested workflow", session_id="session-1", event_log=event_log)

    events = event_log.read_all()
    assert [event.event_type for event in events] == [
        "UserRequestReceived",
        "PlanModeEntered",
        "TaskFingerprinted",
        "RuntimeGraphContextProjected",
        "WorkflowPathSelected",
        "CapabilityGapDetected",
        "EvolutionRequested",
        "WorkflowVerified",
        "PermissionChecked",
    ]
    assert {event.session_id for event in events} == {"session-1"}
