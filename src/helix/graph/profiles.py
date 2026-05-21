from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from helix.graph.stores import FullGraphStore, HealthyGraphStore
from helix.schemas import GraphProfile


class GraphProfileRegistryError(ValueError):
    pass


class GraphProfileRegistry:
    def __init__(self, profiles: Iterable[GraphProfile] = ()) -> None:
        self._profiles = {profile.profile_id: profile for profile in profiles}

    def require(self, profile_id: str) -> GraphProfile:
        profile = self._profiles.get(profile_id)
        if profile is None:
            msg = f"Graph profile is not registered: {profile_id}"
            raise GraphProfileRegistryError(msg)
        return profile

    def list_profiles(self) -> list[GraphProfile]:
        return list(self._profiles.values())

    def list_demo_profiles(self) -> list[GraphProfile]:
        return [profile for profile in self._profiles.values() if profile.mode == "demo"]


class GraphProfileStoreLoader(Protocol):
    """Load stores for a configured graph profile.

    Packaged demo profiles and production profiles use the same store ports. Demo
    loaders must load packaged demoL0 and demoL1 assets; production loaders can
    connect to configured database-backed L0 and L1 stores.
    """

    def load_l0_store(self, profile: GraphProfile) -> FullGraphStore:
        """Return the L0 store for the profile."""

    def load_l1_store(self, profile: GraphProfile) -> HealthyGraphStore:
        """Return the L1 store for the profile."""
