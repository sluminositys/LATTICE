import pytest
from pydantic import ValidationError

from helix.runtime import AgentEvent, FileAgentEventLog
from helix.schemas import Provenance


def test_file_event_log_appends_without_overwriting(tmp_path) -> None:
    log_path = tmp_path / "events.jsonl"
    event_log = FileAgentEventLog(log_path)

    event_log.append(
        AgentEvent(
            event_id="event-1",
            session_id="session-1",
            event_type="UserRequestReceived",
            provenance=[Provenance(source_type="user")],
        )
    )
    event_log.append(
        AgentEvent(
            event_id="event-2",
            session_id="session-1",
            event_type="TaskFingerprinted",
            provenance=[Provenance(source_type="task_fingerprinter")],
        )
    )

    raw_lines = log_path.read_text(encoding="utf-8").splitlines()
    events = event_log.read_all()

    assert len(raw_lines) == 2
    assert [event.event_id for event in events] == ["event-1", "event-2"]


def test_agent_event_requires_provenance() -> None:
    with pytest.raises(ValidationError):
        AgentEvent(
            event_id="event-1",
            session_id="session-1",
            event_type="UserRequestReceived",
            provenance=[],
        )
