from __future__ import annotations

from lattice.capability_evolution.candidates import CandidateTool
from lattice.schemas import ToolCallSpec


class ToolCallSpecBuilder:
    def build_from_candidate_tool(self, candidate: CandidateTool) -> ToolCallSpec:
        return ToolCallSpec(
            toolcall_spec_id=f"toolcall-{candidate.candidate_id}",
            name=candidate.name,
            tool_name=candidate.tool_name,
            tool_version_policy="candidate",
            input_schema=candidate.input_schema,
            output_schema=candidate.output_schema,
            parameter_schema=candidate.parameter_schema,
            runtime_backend=candidate.runtime_backend,
            permission_policy=candidate.permission_policy,
            lifecycle_state=candidate.lifecycle_state,
            provenance=candidate.provenance,
        )
