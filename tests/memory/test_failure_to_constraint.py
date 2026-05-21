import pytest

from helix.memory import FailureToConstraintExtractor
from helix.runtime import AgentEvent
from helix.schemas import Provenance


def make_failure_event() -> AgentEvent:
    return AgentEvent(
        event_id="event-1",
        session_id="session-1",
        event_type="ToolCallFailed",
        payload={"tool_name": "candidate-tool", "error_class": "MissingInput"},
        provenance=[Provenance(source_type="toolcall_runtime")],
    )


def test_failure_to_constraint_extracts_candidate_constraint() -> None:
    constraint = FailureToConstraintExtractor().extract(make_failure_event())

    assert constraint.type == "failure_condition"
    assert constraint.subject == "candidate-tool"
    assert constraint.object == "MissingInput"
    assert constraint.severity == "warning"
    assert constraint.lifecycle_state == "candidate"


def test_single_failure_cannot_be_global_blocker() -> None:
    with pytest.raises(ValueError):
        FailureToConstraintExtractor().extract(
            make_failure_event(),
            scope="global",
            severity="blocker",
        )


def test_non_failure_event_is_rejected() -> None:
    event = AgentEvent(
        event_id="event-1",
        session_id="session-1",
        event_type="TaskFingerprinted",
        provenance=[Provenance(source_type="task_fingerprinter")],
    )

    with pytest.raises(ValueError):
        FailureToConstraintExtractor().extract(event)
