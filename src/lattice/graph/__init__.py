"""Graph tier interfaces and policies."""

from lattice.graph.importer import GraphAssetImporter, GraphAssetImportReport, GraphRecordStore
from lattice.graph.packaged import (
    JsonlPackagedDemoGraphStoreLoader,
    PackagedFullGraphStore,
    PackagedGraphStoreError,
    PackagedHealthyGraphStore,
    load_graph_records,
    load_packaged_demo_graph_manifest,
)
from lattice.graph.policies import GraphTierPolicy, GraphTierPolicyError
from lattice.graph.profiles import (
    GraphProfileRegistry,
    GraphProfileRegistryError,
    GraphProfileStoreLoader,
)
from lattice.graph.stores import FullGraphStore, HealthyGraphStore


def __getattr__(name: str) -> object:
    if name in {"GraphRuntimeLoadError", "LoadedGraphRuntime", "load_graph_runtime"}:
        from lattice.graph import runtime_loader

        return getattr(runtime_loader, name)
    raise AttributeError(f"module 'lattice.graph' has no attribute {name!r}")

__all__ = [
    "FullGraphStore",
    "GraphAssetImporter",
    "GraphAssetImportReport",
    "GraphProfileRegistry",
    "GraphProfileRegistryError",
    "GraphProfileStoreLoader",
    "GraphRuntimeLoadError",
    "GraphTierPolicy",
    "GraphTierPolicyError",
    "HealthyGraphStore",
    "JsonlPackagedDemoGraphStoreLoader",
    "LoadedGraphRuntime",
    "PackagedFullGraphStore",
    "PackagedGraphStoreError",
    "PackagedHealthyGraphStore",
    "load_graph_records",
    "load_packaged_demo_graph_manifest",
    "load_graph_runtime",
    "GraphRecordStore",
]
