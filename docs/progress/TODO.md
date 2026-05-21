# HELIX Implementation TODO

This backlog tracks the project as an independent Python HELIX agent system. Keep changes small, commit frequently, and update this file with each implementation slice.

## Build Policy

- Use `uv` for environment management.
- Keep runtime parameters in `config/`.
- Do not add mock experiments, fake external APIs, bundled sample workflows, or hidden demo construction scripts.
- L0 and L1 graph assets must pass the shared six-layer schema before use.
- Any new graph knowledge enters L0 through GraphPatch or explicit external asset import.
- L1 is a healthy materialization and must not be directly mutated by normal agent execution.
- Tool execution must go through active ToolCallSpec plus PermissionGate plus RuntimeBackend.
- Operational logs and generated reports belong under `D:\workspace\codex`.

## Completed Foundation

- [x] Create independent project directory at `D:\workspace\HELIX`.
- [x] Initialize git repository and remote `git@github.com:sluminositys/HELIX.git`.
- [x] Add Python package metadata, `uv.lock`, ruff, mypy, and pytest.
- [x] Add typed settings loader and environment overrides.
- [x] Add core schemas for task, runtime context, AEP, ToolCall, observations, verification, GraphPatch, experience, graph profiles, and six-layer Bio-EvoKG records.
- [x] Add append-only file AgentEventLog.
- [x] Add session state machine.
- [x] Add graph tier protocols and policy checks.
- [x] Add MemoryHealthCompiler boundary and lifecycle state manager.
- [x] Add controlled L0 recall boundary.
- [x] Add HookBus boundary.
- [x] Add CLI entrypoint.

## Completed Graph And Database Integration

- [x] Add demo/production graph profile policies.
- [x] Add packaged demoL0/demoL1 loader with read-only stores.
- [x] Project packaged demoL1 through the same five runtime views as production L1.
- [x] Add graph asset validation and import path for externally built L0/L1.
- [x] Add Neo4j L0 store with GraphPatch apply and external record replacement.
- [x] Add Neo4j L1 store with runtime context projection and external record replacement.
- [x] Add PostgreSQL core table initializer.
- [x] Add PostgreSQL AgentEventLog adapter.
- [x] Add PostgreSQL ToolCallSpec store.
- [x] Add Qdrant graph node vector index adapter.
- [x] Add config keys for Neo4j, PostgreSQL, and Qdrant.

## Completed Planning, Execution, And Evolution

- [x] Add LangGraph plan flow.
- [x] Add LangGraph execution flow.
- [x] Add WorkflowPathSearch over L2 workflow nodes.
- [x] Add AgenticExecutionPlanBuilder from selected workflow steps.
- [x] Add WorkflowVerifier blockers for missing path, missing ToolCallSpec, missing executable steps, and unresolved requirements.
- [x] Add PermissionGate modes for read-only, plan-only, approval-required, and execution modes.
- [x] Add ToolCallRegistry loading from RuntimeGraphContext.
- [x] Add ToolCallValidator and ToolCallDispatcher.
- [x] Add RuntimeBackend implementations for Python functions, CLI, REST API, database API, and containerized CLI.
- [x] Add execution experience GraphPatch generation.
- [x] Add ability to write audited execution experience patches to L0.
- [x] Add capability gap detector.
- [x] Add EvolutionAgent for L0 candidate gap patches.
- [x] Add ToolBuilderAgent for candidate Tool and ToolCallSpec GraphPatch creation.

## Active Next Steps

- [ ] Add production API layer after CLI and core flow stabilize.
- [ ] Add versioned database migrations instead of only bootstrap DDL strings.
- [ ] Add concrete Qdrant collection creation policy once embedding model settings are finalized.
- [ ] Add richer WorkflowPathSearch ranking signals from OperationalProfile.
- [ ] Add parameter source checker as a separate gate before execution.
- [ ] Add result sanity checker and deeper claim/workflow post-execution verification.
- [ ] Expand MemoryHealthCompiler from boundary/reporting into policy-driven materialization.
- [ ] Add graph patch duplicate/conflict detection against real L0 queries.
- [ ] Add admin approval workflow for high-risk GraphPatch writes.
- [ ] Add LLM-backed TaskFingerprinter and graph-backed disambiguation after model provider config is finalized.
- [ ] Add external ToolDiscovery ingestion interface for user-built or separately discovered tools.
- [ ] Add packaging path for user-supplied demoL0/demoL1 assets when the demo graph is ready.

## Explicitly Deferred

- [ ] First complete L0 construction from literature and broad domain discovery: deferred because the user will build and provide it separately.
- [ ] First complete demoL0/demoL1 construction: deferred because the user will build it externally and only package final graph assets into HELIX.
- [ ] Bundled bioinformatics tools and domain-specific workflows: deferred until real ToolCallSpec and graph content are supplied or discovered through the controlled tool-building path.

## Latest Validation

- [x] `uv run pytest` (`103 passed`)
- [x] `uv run ruff check .`
- [x] `uv run mypy`
