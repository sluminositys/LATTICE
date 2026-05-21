from __future__ import annotations

import importlib
from typing import Any

from pydantic import Field

from helix.schemas import BioEvoKGNode, HelixBaseModel


class QdrantStoreError(RuntimeError):
    pass


class QdrantSearchHit(HelixBaseModel):
    point_id: str
    score: float
    payload: dict[str, Any] = Field(default_factory=dict)


class QdrantGraphIndex:
    def __init__(
        self,
        *,
        url: str,
        api_key: str | None = None,
        prefer_grpc: bool = False,
        client: Any | None = None,
    ) -> None:
        self.client = client or _create_qdrant_client(
            url=url,
            api_key=api_key,
            prefer_grpc=prefer_grpc,
        )

    def upsert_node_embedding(
        self,
        *,
        collection_name: str,
        node: BioEvoKGNode,
        vector: list[float],
        graph_profile_id: str,
        graph_tier: str,
    ) -> None:
        payload = {
            "node_id": node.node_id,
            "graph_profile_id": graph_profile_id,
            "graph_tier": graph_tier,
            "layer": node.layer,
            "node_type": node.node_type,
            "canonical_name": node.canonical_name,
            "lifecycle_state": node.lifecycle_state,
        }
        point = {
            "id": f"{graph_profile_id}:{graph_tier}:{node.node_id}",
            "vector": vector,
            "payload": payload,
        }
        self.client.upsert(collection_name=collection_name, points=[point])

    def search(
        self,
        *,
        collection_name: str,
        query_vector: list[float],
        limit: int = 20,
        query_filter: dict[str, Any] | None = None,
    ) -> list[QdrantSearchHit]:
        hits = self.client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=query_filter,
        )
        return [
            QdrantSearchHit(
                point_id=str(hit.id),
                score=float(hit.score),
                payload=dict(hit.payload or {}),
            )
            for hit in hits
        ]


def _create_qdrant_client(
    *,
    url: str,
    api_key: str | None,
    prefer_grpc: bool,
) -> Any:
    try:
        qdrant_client = importlib.import_module("qdrant_client")
    except ImportError as error:
        msg = "qdrant-client package is required for Qdrant adapters."
        raise QdrantStoreError(msg) from error
    return qdrant_client.QdrantClient(url=url, api_key=api_key, prefer_grpc=prefer_grpc)
