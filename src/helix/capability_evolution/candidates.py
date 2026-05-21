from __future__ import annotations

from typing import Any

from pydantic import Field, model_validator

from helix.schemas import HelixBaseModel, LifecycleState, Provenance


class CandidateTool(HelixBaseModel):
    candidate_id: str
    name: str
    tool_name: str
    runtime_backend: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    parameter_schema: dict[str, Any] = Field(default_factory=dict)
    permission_policy: dict[str, Any] = Field(default_factory=dict)
    provenance: Provenance
    lifecycle_state: LifecycleState = "candidate"

    @model_validator(mode="after")
    def require_candidate_or_probationary(self) -> CandidateTool:
        if self.lifecycle_state not in {"candidate", "probationary"}:
            msg = "CandidateTool cannot be created directly as an active capability."
            raise ValueError(msg)
        return self


class CandidateWorkflow(HelixBaseModel):
    candidate_id: str
    name: str
    workflow_steps: list[dict[str, Any]]
    provenance: Provenance
    lifecycle_state: LifecycleState = "candidate"

    @model_validator(mode="after")
    def require_candidate_or_probationary(self) -> CandidateWorkflow:
        if self.lifecycle_state not in {"candidate", "probationary"}:
            msg = "CandidateWorkflow cannot be created directly as an active workflow."
            raise ValueError(msg)
        return self
