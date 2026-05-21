# HELIX Implementation Coverage

This file tracks which architecture concepts are represented in code and which remain open.

## Implemented

- Three-tier graph policy: L0 `FullGraphStore`, L1 `HealthyGraphStore`, L2 `RuntimeGraphContext`, and L1 direct-write prevention.
- Six-layer Bio-EvoKG schema: Task, Evidence, Workflow, Resource, Implementation, and Experience.
- L0/L1 graph record validation with provenance, lifecycle state, layer/type compatibility, and L1 `OperationalProfile`.
- Demo and production graph profiles.
- Packaged demoL0/demoL1 read path using the same graph schema and runtime projection structure as production.
- External L0/L1 asset validation and import interface.
- Neo4j L0/L1 graph adapters.
- PostgreSQL schema bootstrap, AgentEventLog adapter, and ToolCallSpec store.
- Qdrant node-vector index adapter.
- Runtime graph loading from configured profiles.
- Controlled L0 recall boundary.
- Task fingerprinting boundary.
- LangGraph plan flow.
- LangGraph execution flow.
- Workflow path search over L2 workflow nodes.
- AgenticExecutionPlanBuilder.
- Workflow verification blockers.
- PermissionGate modes.
- ToolCall registry, validator, dispatcher, and fail-closed behavior.
- Runtime backends for Python function, CLI, REST API, database API, and containerized CLI.
- Structured observations and execution experience GraphPatch generation.
- GraphPatch builder, validator, and auditor.
- MemoryHealthCompiler boundary and lifecycle state manager.
- HookBus.
- Append-only event logs.
- Session state machine.
- Candidate tool/workflow schemas.
- Capability gap detection.
- EvolutionAgent candidate patch generation.
- ToolBuilderAgent candidate Tool and ToolCallSpec patch generation.
- Failure-to-constraint extraction.
- ClaimVerifier boundary.
- CLI commands for planning, execution, database initialization, graph validation, and graph import.

## Explicit Deferrals

- First complete L0 construction from literature, broad domain discovery, or user-selected research fields is not implemented here because the user will build and provide it separately.
- First complete demoL0/demoL1 construction is not implemented here; only final demo graph assets should be packaged into the system.
- Real bioinformatics tools and domain-specific workflows are not bundled until real ToolCallSpec records and graph content are provided or discovered through the controlled capability path.
- API service endpoints are still pending because the CLI and core orchestration path are the current integration surface.

## Remaining Gaps

- ParameterSourceChecker is not implemented as a separate gate.
- Workflow ranking currently uses minimal active path ordering and needs richer OperationalProfile signals.
- ResultSanityChecker and deeper post-execution verification are not implemented.
- EvidenceChecker is not implemented beyond schema/provenance contracts.
- PreferenceConsolidator is not implemented.
- ExperienceReplay, FailurePatternMiner, WorkflowPatternMiner, and QualityExperienceUpdater are not implemented.
- CapabilityPromotion is not implemented beyond lifecycle state manager primitives.
- GraphPatch duplicate and conflict detection against real L0 are not implemented.
- Database migrations are bootstrap DDL strings, not versioned migrations.

## Current Expected Behavior

With valid L0/L1 assets and active ToolCallSpec nodes, `helix execute` can select an L2 workflow path, compile an AEP, pass permission checks, dispatch ToolCalls through registered backends, and write structured execution experience candidates to L0.

Without valid graph content or active ToolCallSpec records, HELIX returns structured blockers and capability-gap events instead of inventing a workflow.
