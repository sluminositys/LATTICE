from __future__ import annotations

from typing import Literal

SessionStatus = Literal[
    "received",
    "fingerprinted",
    "runtime_context_projected",
    "planning",
    "workflow_verified",
    "plan_blocked",
    "plan_verified",
    "executing",
    "execution_failed",
    "execution_completed",
    "claim_verifying",
    "experience_extracting",
    "graph_patch_proposed",
    "graph_patch_applied_to_L0",
    "memory_health_compiling",
    "healthy_graph_updated",
    "completed",
]


class SessionStateTransitionError(ValueError):
    pass


class SessionStateMachine:
    allowed_transitions: dict[SessionStatus, frozenset[SessionStatus]] = {
        "received": frozenset({"fingerprinted"}),
        "fingerprinted": frozenset({"runtime_context_projected"}),
        "runtime_context_projected": frozenset({"planning"}),
        "planning": frozenset({"workflow_verified"}),
        "workflow_verified": frozenset({"plan_verified", "plan_blocked"}),
        "plan_blocked": frozenset({"completed"}),
        "plan_verified": frozenset({"executing", "completed"}),
        "executing": frozenset({"execution_completed", "execution_failed"}),
        "execution_completed": frozenset({"claim_verifying"}),
        "execution_failed": frozenset({"experience_extracting"}),
        "claim_verifying": frozenset({"experience_extracting"}),
        "experience_extracting": frozenset({"graph_patch_proposed"}),
        "graph_patch_proposed": frozenset({"graph_patch_applied_to_L0"}),
        "graph_patch_applied_to_L0": frozenset({"memory_health_compiling"}),
        "memory_health_compiling": frozenset({"healthy_graph_updated"}),
        "healthy_graph_updated": frozenset({"completed"}),
        "completed": frozenset(),
    }

    def assert_transition_allowed(self, current: SessionStatus, next_status: SessionStatus) -> None:
        if next_status not in self.allowed_transitions[current]:
            msg = f"Invalid session transition: {current} -> {next_status}"
            raise SessionStateTransitionError(msg)

    def transition(self, current: SessionStatus, next_status: SessionStatus) -> SessionStatus:
        self.assert_transition_allowed(current, next_status)
        return next_status
