import pytest

from helix.runtime import SessionStateMachine, SessionStateTransitionError


def test_session_state_machine_allows_documented_plan_blocked_path() -> None:
    machine = SessionStateMachine()
    status = "received"

    for next_status in [
        "fingerprinted",
        "runtime_context_projected",
        "planning",
        "workflow_verified",
        "plan_blocked",
        "completed",
    ]:
        status = machine.transition(status, next_status)

    assert status == "completed"


def test_session_state_machine_allows_execution_success_path() -> None:
    machine = SessionStateMachine()

    assert machine.transition("plan_verified", "executing") == "executing"
    assert machine.transition("executing", "execution_completed") == "execution_completed"
    assert machine.transition("execution_completed", "claim_verifying") == "claim_verifying"


def test_session_state_machine_rejects_skipping_fingerprint() -> None:
    with pytest.raises(SessionStateTransitionError):
        SessionStateMachine().transition("received", "planning")
