from __future__ import annotations

from uuid import uuid4

from lattice.capability_evolution.candidates import CandidateTool, ToolDiscoveryRecord
from lattice.capability_evolution.toolcall_spec_builder import ToolCallSpecBuilder
from lattice.graph_patch import GraphPatchBuilder
from lattice.runtime import AgentEvent
from lattice.schemas import GraphPatch, ToolCallSpec


class ToolBuilderAgent:
    def build_candidate_tool(self, discovery: ToolDiscoveryRecord) -> CandidateTool:
        return CandidateTool(
            candidate_id=f"tool-{discovery.discovery_id}",
            name=discovery.name,
            tool_name=discovery.tool_name,
            runtime_backend=discovery.runtime_backend,
            input_schema=discovery.input_schema,
            output_schema=discovery.output_schema,
            parameter_schema=discovery.parameter_schema,
            permission_policy=discovery.permission_policy,
            provenance=discovery.provenance,
        )

    def build_toolcall_spec_candidate(self, discovery: ToolDiscoveryRecord) -> ToolCallSpec:
        return ToolCallSpecBuilder().build_from_candidate_tool(
            self.build_candidate_tool(discovery)
        )

    def propose_tool_graph_patch(
        self,
        *,
        discovery: ToolDiscoveryRecord,
        source_events: list[AgentEvent],
    ) -> GraphPatch:
        candidate_tool = self.build_candidate_tool(discovery)
        spec = ToolCallSpecBuilder().build_from_candidate_tool(candidate_tool)
        patch = GraphPatchBuilder().build_candidate(
            source_events=source_events,
            source_module="ToolBuilderAgent",
            provenance=discovery.provenance,
        )
        tool_node_id = f"resource-tool-{candidate_tool.candidate_id}"
        profile_node_id = f"implementation-profile-{spec.toolcall_spec_id}"
        patch.nodes_to_add.extend(
            [
                {
                    "node_id": tool_node_id,
                    "layer": "resource",
                    "node_type": "Tool",
                    "canonical_name": candidate_tool.name,
                    "attributes": {
                        "tool_name": candidate_tool.tool_name,
                        "description": discovery.description,
                        "source_refs": discovery.source_refs,
                    },
                    "lifecycle_state": candidate_tool.lifecycle_state,
                    "provenance": [candidate_tool.provenance.model_dump(mode="json")],
                },
                {
                    "node_id": profile_node_id,
                    "layer": "implementation",
                    "node_type": "ToolImplementationProfile",
                    "canonical_name": f"{spec.name} implementation profile",
                    "attributes": {
                        "software_id": tool_node_id,
                        "software_name": candidate_tool.name,
                        "agent_callability": {
                            "enabled": True,
                            "tool_call_specs": [spec.model_dump(mode="json")],
                        },
                    },
                    "lifecycle_state": spec.lifecycle_state,
                    "provenance": [spec.provenance.model_dump(mode="json")],
                },
            ]
        )
        patch.edges_to_add.append(
            {
                "edge_id": f"edge-{uuid4()}",
                "edge_type": "HAS_IMPLEMENTATION_PROFILE",
                "source_node_id": tool_node_id,
                "target_node_id": profile_node_id,
                "source_layer": "resource",
                "target_layer": "implementation",
                "source_type": "tool_builder_agent",
                "lifecycle_state": spec.lifecycle_state,
                "provenance": [spec.provenance.model_dump(mode="json")],
            }
        )
        return patch
