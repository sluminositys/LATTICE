import pytest

from helix.hooks import HookBus, HookBusError, HookEvent, HookOutput
from helix.runtime import FileAgentEventLog
from helix.schemas import Provenance


def test_hook_bus_collects_runtime_warnings() -> None:
    bus = HookBus()

    bus.register(
        "PreWorkflowSearch",
        lambda event: HookOutput(warnings=[f"checking {event.payload['request']}"]),
        handler_name="warning_hook",
    )

    outputs = bus.emit(
        HookEvent(
            event_type="PreWorkflowSearch",
            session_id="session-1",
            payload={"request": "plan"},
        )
    )

    assert outputs[0].warnings == ["checking plan"]


def test_hook_bus_blocks_direct_l1_write_attempts() -> None:
    bus = HookBus()
    bus.register(
        "PreGraphWrite",
        lambda event: HookOutput(requested_l1_write=True),
        handler_name="bad_hook",
    )

    with pytest.raises(HookBusError):
        bus.emit(HookEvent(event_type="PreGraphWrite", session_id="session-1"))


def test_hook_bus_appends_outputs_to_event_log(tmp_path) -> None:
    event_log = FileAgentEventLog(tmp_path / "events.jsonl")
    bus = HookBus(event_log=event_log)
    bus.register(
        "PostWorkflowVerification",
        lambda event: HookOutput(audit_records=[{"status": "checked"}]),
        handler_name="audit_hook",
    )

    bus.emit(
        HookEvent(
            event_type="PostWorkflowVerification",
            session_id="session-1",
            provenance=[Provenance(source_type="test")],
        )
    )

    events = event_log.read_all()
    assert events[0].event_type == "PostWorkflowVerification"
    assert events[0].payload["hook_outputs"][0]["audit_records"] == [{"status": "checked"}]
