from lattice.schemas import (
    AgenticExecutionPlan,
    AgenticExecutionStep,
    Provenance,
    StructuredObservation,
    ToolCallSpec,
)


def test_agentic_execution_plan_can_be_planned_without_execution() -> None:
    step = AgenticExecutionStep(
        step_id="step-1",
        workflow_step_id="wf-step-1",
        toolcall_spec_id="toolcall-1",
    )
    plan = AgenticExecutionPlan(
        plan_id="aep-1",
        task_fingerprint_id="tf-1",
        runtime_graph_context_id="rgc-1",
        selected_workflow_path_id="path-1",
        steps=[step],
    )

    assert plan.status == "planned"
    assert plan.steps[0].toolcall_spec_id == "toolcall-1"


def test_toolcall_spec_requires_provenance_and_lifecycle() -> None:
    spec = ToolCallSpec(
        toolcall_spec_id="toolcall-1",
        name="Registered QC tool",
        tool_name="qc-tool",
        tool_version_policy="pinned",
        runtime_backend="cli",
        lifecycle_state="candidate",
        provenance=Provenance(source_type="curator"),
    )

    assert spec.lifecycle_state == "candidate"
    assert spec.permission_policy == {}


def test_structured_observation_is_not_raw_stdout() -> None:
    observation = StructuredObservation(
        observation_id="obs-1",
        toolcall_event_id="event-1",
        status="failure",
        error_class="ToolUnavailable",
        parsed_summary={"reason": "tool is not registered as active"},
        provenance=Provenance(source_type="toolcall_runtime"),
    )

    assert observation.outputs == {}
    assert observation.parsed_summary["reason"] == "tool is not registered as active"
