from __future__ import annotations

from lattice.schemas import LifecycleState, LifecycleTransition


class LifecycleStateError(ValueError):
    pass


class LifecycleStateManager:
    allowed_transitions: dict[LifecycleState, frozenset[LifecycleState]] = {
        "candidate": frozenset({"probationary", "quarantined", "retired", "tombstoned"}),
        "probationary": frozenset({"active_warm", "quarantined", "retired", "tombstoned"}),
        "active_warm": frozenset(
            {"active_hot", "cold_reference", "deprecated_reference", "quarantined", "retired"}
        ),
        "active_hot": frozenset({"active_warm", "deprecated_reference", "quarantined", "retired"}),
        "cold_reference": frozenset(
            {"active_warm", "deprecated_reference", "quarantined", "retired"}
        ),
        "deprecated_reference": frozenset({"retired", "tombstoned"}),
        "quarantined": frozenset({"retired", "tombstoned"}),
        "retired": frozenset({"tombstoned"}),
        "tombstoned": frozenset(),
    }

    def assert_transition_allowed(self, transition: LifecycleTransition) -> None:
        allowed_targets = self.allowed_transitions[transition.from_state]
        if transition.to_state not in allowed_targets:
            msg = f"Invalid lifecycle transition: {transition.from_state} -> {transition.to_state}"
            raise LifecycleStateError(msg)

    def next_capability_promotion_state(self, state: LifecycleState) -> LifecycleState:
        if state == "candidate":
            return "probationary"
        if state == "probationary":
            return "active_warm"
        if state == "active_warm":
            return "active_hot"
        msg = f"No promotion path from lifecycle state: {state}"
        raise LifecycleStateError(msg)

    def next_pollution_state(self, state: LifecycleState) -> LifecycleState:
        if state in {"candidate", "probationary", "active_warm", "active_hot", "cold_reference"}:
            return "quarantined"
        if state == "quarantined":
            return "retired"
        if state == "retired":
            return "tombstoned"
        msg = f"No pollution path from lifecycle state: {state}"
        raise LifecycleStateError(msg)
