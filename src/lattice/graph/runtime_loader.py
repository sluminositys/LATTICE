from __future__ import annotations

from pydantic import ConfigDict, Field

from lattice.config.settings import LatticeSettings
from lattice.db import Neo4jFullGraphStore, Neo4jHealthyGraphStore, QdrantGraphIndex
from lattice.graph.packaged import JsonlPackagedDemoGraphStoreLoader
from lattice.schemas import GraphProfile, LatticeBaseModel


class GraphRuntimeLoadError(ValueError):
    pass


class LoadedGraphRuntime(LatticeBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    profile: GraphProfile
    l0_store: object | None = None
    l1_store: object | None = None
    vector_index: object | None = None
    notes: list[str] = Field(default_factory=list)


def load_graph_runtime(
    settings: LatticeSettings,
    *,
    profile_id: str | None = None,
) -> LoadedGraphRuntime:
    resolved_profile_id = profile_id or settings.graph_profiles.active_profile_id
    if not resolved_profile_id:
        raise GraphRuntimeLoadError("No graph profile id was provided or configured.")
    profile = settings.graph_profiles.profiles.get(resolved_profile_id)
    if profile is None:
        raise GraphRuntimeLoadError(f"Graph profile is not configured: {resolved_profile_id}")

    if profile.mode == "demo":
        loader = JsonlPackagedDemoGraphStoreLoader()
        return LoadedGraphRuntime(
            profile=profile,
            l0_store=loader.load_l0_store(profile),
            l1_store=loader.load_l1_store(profile),
            vector_index=_load_qdrant_index(settings),
            notes=["Loaded packaged demoL0 and demoL1 stores."],
        )

    if settings.graph.l0_backend == "neo4j" and settings.graph.l1_backend == "neo4j":
        _require_neo4j_settings(settings)
        return LoadedGraphRuntime(
            profile=profile,
            l0_store=Neo4jFullGraphStore(
                uri=settings.databases.neo4j_uri or "",
                user=settings.databases.neo4j_user or "",
                password=settings.databases.neo4j_password or "",
                database=settings.databases.neo4j_database,
                graph_profile_id=profile.profile_id,
            ),
            l1_store=Neo4jHealthyGraphStore(
                uri=settings.databases.neo4j_uri or "",
                user=settings.databases.neo4j_user or "",
                password=settings.databases.neo4j_password or "",
                database=settings.databases.neo4j_database,
                graph_profile_id=profile.profile_id,
            ),
            vector_index=_load_qdrant_index(settings),
            notes=["Loaded Neo4j L0 and L1 stores."],
        )

    raise GraphRuntimeLoadError(
        "Unsupported graph backend combination: "
        f"{settings.graph.l0_backend}/{settings.graph.l1_backend}"
    )


def _require_neo4j_settings(settings: LatticeSettings) -> None:
    missing = []
    if not settings.databases.neo4j_uri:
        missing.append("databases.neo4j_uri")
    if not settings.databases.neo4j_user:
        missing.append("databases.neo4j_user")
    if not settings.databases.neo4j_password:
        missing.append("databases.neo4j_password")
    if missing:
        raise GraphRuntimeLoadError(f"Missing Neo4j settings: {', '.join(missing)}")


def _load_qdrant_index(settings: LatticeSettings) -> QdrantGraphIndex | None:
    if not settings.databases.qdrant_url:
        return None
    return QdrantGraphIndex(
        url=settings.databases.qdrant_url,
        api_key=settings.databases.qdrant_api_key,
        prefer_grpc=settings.databases.qdrant_prefer_grpc,
    )
