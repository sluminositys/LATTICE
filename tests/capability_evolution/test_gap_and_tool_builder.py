from __future__ import annotations

from lattice.capability_evolution import (
    CapabilityGapDetector,
    EvolutionAgent,
    ToolBuilderAgent,
    ToolDiscoveryRecord,
)
from lattice.core import TaskFingerprinter
from lattice.planning import WorkflowSearchResult
from lattice.runtime import AgentEvent
from lattice.schemas import GraphContextSufficiencyReport, Provenance, RuntimeGraphContext


def test_gap_detector_converts_unresolved_toolcall_need_to_gap() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Need a workflow")
    context = RuntimeGraphContext(
        graph_context_id="rgc-1",
        task_fingerprint_id=fingerprint.fingerprint_id,
        source_graph_tier="G1",
        sufficiency_report=GraphContextSufficiencyReport(
            report_id="gcsr-1",
            status="insufficient",
            missing_toolcall_info=["ToolCallSpec missing"],
        ),
    )
    search_result = WorkflowSearchResult(unresolved_requirements=["ToolCallSpec missing"])

    gaps = CapabilityGapDetector().detect(
        fingerprint=fingerprint,
        runtime_context=context,
        workflow_search_result=search_result,
    )

    assert len(gaps) == 1
    assert gaps[0].gap_type == "toolcall_spec"
    assert gaps[0].task_fingerprint_id == fingerprint.fingerprint_id


def test_evolution_agent_proposes_g0_gap_patch() -> None:
    fingerprint = TaskFingerprinter().fingerprint("Need a workflow")
    context = RuntimeGraphContext(
        graph_context_id="rgc-1",
        task_fingerprint_id=fingerprint.fingerprint_id,
        source_graph_tier="G1",
        sufficiency_report=GraphContextSufficiencyReport(
            report_id="gcsr-1",
            status="insufficient",
        ),
    )
    gap = CapabilityGapDetector().detect(
        fingerprint=fingerprint,
        runtime_context=context,
        workflow_search_result=WorkflowSearchResult(
            unresolved_requirements=["no active workflow path nodes projected from G1"]
        ),
    )[0]
    event = AgentEvent(
        event_id="event-1",
        session_id="session-1",
        event_type="CapabilityGapDetected",
        payload=gap.model_dump(mode="json"),
        provenance=[Provenance(source_type="test")],
    )

    request, patch = EvolutionAgent().propose_gap_patch(gaps=[gap], source_events=[event])

    assert request.proposed_graph_patch_id == patch.patch_id
    assert patch.target_graph_tier == "G0"
    assert patch.nodes_to_add[0]["node_type"] == "QualitySignal"


def test_tool_builder_proposes_tool_and_implementation_profile_patch() -> None:
    discovery = ToolDiscoveryRecord(
        discovery_id="discovery-1",
        name="External tool",
        tool_name="external-tool",
        description="A discovered executable capability.",
        runtime_backend="cli",
        input_schema={"required": ["input_path"]},
        output_schema={"required": ["output_path"]},
        permission_policy={"command": ["external-tool", "{{inputs.input_path}}"]},
        source_refs=["paper:1"],
        provenance=Provenance(source_type="tool_discovery"),
    )
    event = AgentEvent(
        event_id="event-1",
        session_id="session-1",
        event_type="CandidateToolCreated",
        payload={},
        provenance=[Provenance(source_type="test")],
    )

    patch = ToolBuilderAgent().propose_tool_graph_patch(
        discovery=discovery,
        source_events=[event],
    )

    assert [node["node_type"] for node in patch.nodes_to_add] == [
        "Tool",
        "ToolImplementationProfile",
    ]
    assert patch.edges_to_add[0]["edge_type"] == "HAS_IMPLEMENTATION_PROFILE"
    tool_specs = patch.nodes_to_add[1]["attributes"]["agent_callability"]["tool_call_specs"]
    assert tool_specs[0]["runtime_backend"] == "cli"
