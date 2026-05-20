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
- [ ] Commit remaining core schema contracts.

## Phase 4: Append-Only Runtime Event Log

- [ ] Define `AgentEvent`.
- [ ] Define event type enum from architecture section 18.
- [ ] Add append-only file event log backend.
- [ ] Add event provenance requirements.
- [ ] Add tests preventing event overwrite.
- [ ] Commit runtime event log.

## Phase 5: Graph Tier Interfaces

- [ ] Define `FullGraphStore` protocol for L0.
- [ ] Define `HealthyGraphStore` protocol for L1.
- [ ] Define `RuntimeGraphContext` usage boundary for L2.
- [ ] Define graph tier policy checks.
- [ ] Add tests ensuring GraphPatch cannot target L1.
- [ ] Commit graph tier contracts.

## Phase 6: LangGraph Plan-Only Flow

- [ ] Define session state model.
- [ ] Create LangGraph node skeletons:
  - [ ] receive request
  - [ ] fingerprint task
  - [ ] project runtime context
  - [ ] search workflow path
  - [ ] verify workflow
  - [ ] compile AEP
  - [ ] permission check
  - [ ] produce response
- [ ] Add plan-only stopping behavior.
- [ ] Add tests for state transitions.
- [ ] Commit orchestration skeleton.

## Phase 7: Task Fingerprinting

- [ ] Implement task fingerprinting interface.
- [ ] Keep LLM prompt/template externalized.
- [ ] Return ambiguity items instead of guessing silently.
- [ ] Add tests for deterministic non-LLM normalization.
- [ ] Commit task fingerprint module.

## Phase 8: Runtime Projection

- [ ] Implement five-view projector interfaces.
- [ ] Implement sufficiency checker.
- [ ] Implement controlled recall boundary without direct L1 promotion.
- [ ] Add tests for insufficient context.
- [ ] Commit runtime projection module.

## Phase 9: Planning And Verification

- [ ] Implement workflow path search contracts.
- [ ] Implement deterministic ordering tuple.
- [ ] Implement workflow verifier skeleton.
- [ ] Implement parameter source checker skeleton.
- [ ] Compile AEP only after verifier pass or warning.
- [ ] Add blocked-plan tests.
- [ ] Commit planning and verification.

## Phase 10: Permissions And ToolCall

- [ ] Implement `PermissionGate`.
- [ ] Implement permission mode policies.
- [ ] Implement ToolCall registry.
- [ ] Implement ToolCall validator.
- [ ] Implement dispatcher boundary.
- [ ] Add no-unregistered-tool tests.
- [ ] Commit permissions and ToolCall base.

## Phase 11: GraphPatch Write Path

- [ ] Implement patch builder from events.
- [ ] Implement patch validator.
- [ ] Implement patch auditor.
- [ ] Add audit checks:
  - [ ] schema completeness
  - [ ] provenance completeness
  - [ ] source event validity
  - [ ] duplicate detection placeholder
  - [ ] conflict detection placeholder
  - [ ] lifecycle transition validity
  - [ ] target tier restriction
- [ ] Commit GraphPatch pipeline.

## Phase 12: Memory Health Compiler

- [ ] Implement compiler input/output contracts.
- [ ] Implement lifecycle state manager.
- [ ] Implement health policy config.
- [ ] Implement candidate promotion gates.
- [ ] Implement quarantine/retirement policy skeletons.
- [ ] Add tests that only compiler updates L1 materialization.
- [ ] Commit graph health compiler skeleton.

## Phase 13: Experience And Capability Evolution

- [ ] Implement failure-to-constraint candidate extraction.
- [ ] Implement preference consolidation boundaries.
- [ ] Implement capability gap candidate records.
- [ ] Implement candidate ToolCallSpec builder boundaries.
- [ ] Add tests preventing single failure from becoming global hard rule.
- [ ] Commit evolution modules.

## Phase 14: Entrypoints

- [ ] Add CLI plan command.
- [ ] Add API app skeleton only after core flow exists.
- [ ] Add structured output for blocked/verified plans.
- [ ] Commit entrypoints.

## Active Next Steps

- [x] Finish Phase 0 docs and commit.
- [x] Commit repository hygiene files.
- [x] Build Phase 1 minimal Python project and commit.
- [ ] Build Phase 2 configuration layer and commit.
- [ ] Build Phase 3 first schema group and commit.
