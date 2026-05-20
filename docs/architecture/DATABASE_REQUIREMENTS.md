# HELIX Database Integration Requirements

Source architecture: `E:\donwloads\HELIX_architecture_v7.md`

This document defines the database integration contract for HELIX. It intentionally does not choose or require a concrete graph database yet. The first full run can populate L0 and L1 through dedicated builder agents after the database is installed.

## Design Position

- L0 is the authoritative full graph and audit store.
- L1 is a materialized healthy graph produced only by `MemoryHealthCompiler`.
- L2 is an in-memory per-request `RuntimeGraphContext`.
- Graph writes enter through `GraphPatch`; no module writes graph storage directly.
- Graph backends must be replaceable behind Python protocols.

## L0 Persistent Full Graph Requirements

The L0 backend must support:

- Durable graph nodes and edges.
- Append-only audit history for `GraphPatch`.
- Logical deletion through tombstone records.
- Lifecycle history for every node and edge.
- Provenance metadata on every node and edge.
- Source identity for external resources.
- Query by node id, edge id, lifecycle state, source path, source type, and layer.
- Transactional patch application.
- Ability to retain quarantined, deprecated, retired, and tombstoned records.

Minimum write primitive:

```text
apply_patch(GraphPatch) -> durable_write_id
```

Minimum read primitives:

```text
get_node(node_id)
get_edge(edge_id)
query_nodes(filters)
query_edges(filters)
get_lifecycle_history(target_id)
get_patch_history(target_id)
```

## L1 Healthy Graph Requirements

The L1 backend must support:

- Materialization from `MemoryHealthCompiler` output only.
- Read-only access for normal agent planning.
- Projection by `TaskFingerprint`.
- Filtering by lifecycle state and operational profile.
- Efficient traversal across Task, Evidence, Workflow, Resource, Implementation, and Experience layers.
- Versioned snapshots or materialization ids for reproducibility.

Forbidden L1 write primitive:

```text
GraphPatch -> L1
```

Allowed L1 update primitive:

```text
MemoryHealthCompiler materialization -> L1 snapshot
```

## L2 Runtime Context Requirements

L2 is not a database. It is a request-scoped object composed of:

- `G_task`
- `G_evidence`
- `G_workflow`
- `G_resource`
- `G_experience_preference`
- temporary candidates from controlled L0 recall
- sufficiency report
- provenance

## Candidate Backend Options

The current code keeps backend choice open. Viable future adapters include:

- Neo4j for labeled property graph traversal.
- ArangoDB for multi-model graph and document storage.
- PostgreSQL plus Apache AGE if operational simplicity matters.
- DuckDB or SQLite only for local prototypes, not as the long-term graph system.

## Adapter Boundary

Future database adapters should implement:

- `helix.graph.FullGraphStore`
- `helix.graph.HealthyGraphStore`

Adapters should live outside core contracts, for example:

```text
src/helix/graph/adapters/neo4j_l0.py
src/helix/graph/adapters/neo4j_l1.py
```

## First Full Run Expectation

The first complete run can use dedicated subagents or builder jobs to:

- ingest source architecture and curated domain resources into L0,
- construct initial ToolCallSpec records,
- propose GraphPatch records,
- audit and apply GraphPatch records to L0,
- run `MemoryHealthCompiler`,
- materialize L1,
- then allow normal plan/execution flows to use L1 projection.

Until then, the correct behavior is to return structured insufficient-context reports instead of hallucinating graph content.
