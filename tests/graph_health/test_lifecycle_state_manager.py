import pytest

from lattice.graph_health import LifecycleStateError, LifecycleStateManager
from lattice.schemas import LifecycleTransition


def test_lifecycle_manager_allows_capability_promotion_path() -> None:
    manager = LifecycleStateManager()

    assert manager.next_capability_promotion_state("candidate") == "probationary"
    assert manager.next_capability_promotion_state("probationary") == "active_warm"
    assert manager.next_capability_promotion_state("active_warm") == "active_hot"


def test_lifecycle_manager_allows_pollution_path() -> None:
    manager = LifecycleStateManager()

    assert manager.next_pollution_state("probationary") == "quarantined"
    assert manager.next_pollution_state("quarantined") == "retired"
    assert manager.next_pollution_state("retired") == "tombstoned"


def test_lifecycle_manager_rejects_invalid_transition() -> None:
    transition = LifecycleTransition(
        transition_id="lt-1",
        target_node_or_edge_id="tool-1",
        from_state="candidate",
        to_state="active_hot",
        reason="skip review",
    )

    with pytest.raises(LifecycleStateError):
        LifecycleStateManager().assert_transition_allowed(transition)
