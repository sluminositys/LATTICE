# HELIX Implementation TODO

Source architecture: `E:\donwloads\HELIX_architecture_v7.md`

This TODO is the working backlog for building HELIX as an independent Python agent system. Each small completed unit should be committed separately and reflected in `IMPLEMENTATION_LOG.md`.

## Current Build Policy

- Build from small, reversible modules.
- Keep parameters and runtime policy in `config/`.
- Do not add mock data, fake experiments, or fake external APIs.
- Do not let any module write L1 directly.
- Do not execute unregistered tools.
- Use `uv` for environment management.
- Use LangChain and LangGraph for the agent framework.
- Keep operational logs and generated diagnostics under `D:\workspace\codex`.

## Phase 0: Repository And Tracking

- [x] Create independent project directory at `D:\workspace\HELIX`.
- [x] Initialize git repository on `main`.
- [x] Add remote `git@github.com:sluminositys/HELIX.git`.
- [x] Add progress ledger docs.
- [x] Add architecture decomposition docs.
- [x] Add architecture risks and gaps record.
- [x] Commit tracking docs.
- [ ] Add repository hygiene files.
- [x] Add repository hygiene files.

## Phase 1: Minimal Python Project

- [x] Create `pyproject.toml` with `uv` project metadata.
- [x] Set Python version policy.
- [ ] Add runtime dependencies:
  - [x] `pydantic`
  - [x] `pydantic-settings`
  - [x] `pyyaml`
  - [x] `langchain`
  - [x] `langgraph`
  - [x] `typing-extensions`
- [ ] Add dev dependencies:
  - [x] `pytest`
  - [x] `ruff`
  - [x] `mypy`
- [x] Create `src/helix/`.
- [x] Add package `__init__.py`.
- [x] Add placeholder test directory.
- [x] Generate `uv.lock`.
- [x] Commit minimal project metadata.

## Phase 2: Configuration Layer

- [x] Create `config/base.yaml`.
- [x] Create `config/dev.yaml`.
- [x] Create `config/logging.yaml`.
- [x] Create `config/permissions.yaml`.
- [x] Create `config/graph_health.yaml`.
- [x] Create `config/tool_registry.yaml`.
- [x] Implement settings loader in `src/helix/config/`.
- [x] Support environment variable overrides.
- [x] Add tests for settings loading.
- [ ] Commit config layer.

## Phase 3: Core Object Contracts

- [x] Add schema package skeleton.
- [x] Implement shared base model conventions.
- [x] Add `TaskFingerprint`.
- [x] Add `GraphContextSufficiencyReport`.
- [x] Add `RuntimeGraphContext`.
- [x] Add `AgenticExecutionPlan` and plan step model.
- [x] Add `ToolCallSpec`.
- [x] Add `StructuredObservation`.
- [x] Add `WorkflowAuditReport`.
- [x] Add `ClaimAuditReport`.
- [x] Add `LifecycleTransition`.
- [x] Add `GraphPatch`.
- [x] Add `ExperienceCandidate`.
- [x] Add schema validation tests.
- [x] Commit remaining core schema contracts.

## Phase 4: Append-Only Runtime Event Log

- [x] Define `AgentEvent`.
- [x] Define event type enum from architecture section 18.
- [x] Add append-only file event log backend.
- [x] Add event provenance requirements.
- [x] Add tests preventing event overwrite.
- [ ] Commit runtime event log.

## Phase 5: Graph Tier Interfaces

- [x] Define `FullGraphStore` protocol for L0.
- [x] Define `HealthyGraphStore` protocol for L1.
- [x] Define `RuntimeGraphContext` usage boundary for L2.
- [x] Define graph tier policy checks.
- [x] Add tests ensuring GraphPatch cannot target L1.
- [x] Commit graph tier contracts.
- [x] Document database adapter requirements for future L0/L1 backends.
- [x] Add graph-construction bootstrap workflow using existing GraphPatch and MemoryHealthCompiler path.

## Phase 6: LangGraph Plan-Only Flow

- [x] Define session state model.
- [ ] Create LangGraph node skeletons:
  - [x] receive request
  - [x] fingerprint task
  - [x] project runtime context
  - [x] search workflow path
  - [x] verify workflow
  - [x] compile AEP
  - [x] permission check
  - [x] produce response
- [x] Add plan-only stopping behavior.
- [x] Add tests for state transitions.
- [x] Commit orchestration skeleton.

## Phase 7: Task Fingerprinting

- [x] Implement task fingerprinting interface.
- [x] Keep LLM prompt/template externalized.
- [x] Return ambiguity items instead of guessing silently.
- [x] Add tests for deterministic non-LLM normalization.
- [ ] Commit task fingerprint module.

## Phase 8: Runtime Projection

- [x] Implement five-view projector interfaces.
- [ ] Implement sufficiency checker.
- [ ] Implement controlled recall boundary without direct L1 promotion.
- [x] Add tests for insufficient context.
- [ ] Commit runtime projection module.

## Phase 9: Planning And Verification

- [x] Implement workflow path search contracts.
- [ ] Implement deterministic ordering tuple.
- [x] Implement workflow verifier skeleton.
- [ ] Implement parameter source checker skeleton.
- [ ] Compile AEP only after verifier pass or warning.
- [ ] Add blocked-plan tests.
- [ ] Commit planning and verification.

## Phase 10: Permissions And ToolCall

- [x] Implement `PermissionGate`.
- [x] Implement permission mode policies.
- [x] Implement ToolCall registry.
- [x] Implement ToolCall validator.
- [x] Implement dispatcher boundary.
- [x] Add no-unregistered-tool tests.
- [x] Commit permissions and ToolCall base.

## Phase 11: GraphPatch Write Path

- [x] Implement patch builder from events.
- [x] Implement patch validator.
- [x] Implement patch auditor.
- [ ] Add audit checks:
  - [x] schema completeness
  - [x] provenance completeness
  - [x] source event validity
  - [ ] duplicate detection placeholder
  - [ ] conflict detection placeholder
  - [x] lifecycle transition validity
  - [x] target tier restriction
- [x] Commit GraphPatch builder/validator/auditor pipeline.

## Phase 12: Memory Health Compiler

- [x] Implement compiler input/output contracts.
- [x] Implement lifecycle state manager.
- [ ] Implement health policy config.
- [ ] Implement candidate promotion gates.
- [ ] Implement quarantine/retirement policy skeletons.
- [ ] Add tests that only compiler updates L1 materialization.
- [x] Add tests that only compiler updates L1 materialization.
- [x] Commit graph health compiler skeleton.

## Phase 13: Experience And Capability Evolution

- [ ] Implement failure-to-constraint candidate extraction.
- [ ] Implement preference consolidation boundaries.
- [ ] Implement capability gap candidate records.
- [ ] Implement candidate ToolCallSpec builder boundaries.
- [ ] Add tests preventing single failure from becoming global hard rule.
- [ ] Commit evolution modules.

## Phase 14: Entrypoints

- [x] Add CLI plan command.
- [ ] Add API app skeleton only after core flow exists.
- [x] Add structured output for blocked/verified plans.
- [ ] Commit full app entrypoints.

## Active Next Steps

- [x] Commit database integration requirements.
- [x] Commit ToolCall validator.
- [x] Commit ToolCall dispatcher boundary.
- [x] Commit lifecycle state manager.
- [x] Commit plan-only event logging.
- [x] Commit GraphPatch validator.
- [ ] Start controlled full graph recall boundary.
- [ ] Start capability evolution candidate records.
- [ ] Start failure-to-constraint extraction.
- [x] Commit graph-construction bootstrap workflow.

## Latest Validation

- [x] `uv run pytest` (`51 passed`)
- [x] `uv run ruff check .`
- [x] `uv run mypy`
- [x] `uv run helix plan "Plan RNA-seq QC workflow" --session-id session-20260521 --event-log D:\workspace\codex\logs\2026-05-21\helix-plan-events-20260521.jsonl`
- [x] Push `main` to `origin/main`
