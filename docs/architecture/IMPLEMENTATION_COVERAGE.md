# HELIX Implementation Coverage

Design source: user-provided HELIX architecture planning document.

This file tracks which architecture concepts are represented in code and which remain intentionally deferred until real database and ToolCall installation.

## Implemented Code Boundaries

- Three-tier graph policy: `FullGraphStore`, `HealthyGraphStore`, and L1 direct-write prevention.
- Graph construction bootstrap: `GraphConstructionBootstrapWorkflow`.
- Runtime graph context: `RuntimeGraphContext`, `GraphContextSufficiencyReport`, `RuntimeViewProjector`, and `GraphContextSufficiencyChecker`.
- Controlled L0 recall: `ControlledFullGraphRecall`, `FullGraphRecallProvider`, recall candidate status protection, tombstone blocking, quarantine review-only handling, and weak-provenance marking.
- Agent planning chain: conservative `TaskFingerprinter`, LangGraph plan-only orchestration, `WorkflowPathSearch`, `WorkflowVerifier`, `ExitPlanGate`, and `PermissionGate`.
- ToolCall layer: `ToolCallSpec`, `ToolCallRegistry`, `ToolCallValidator`, `ToolCallDispatcher`, `RuntimeBackend`, and `StructuredObservation`.
- Verification layer: `WorkflowAuditReport`, `ClaimAuditReport`, and `ClaimVerifier`.
- Runtime control: `HookBus`, hook lifecycle events, append-only `AgentEventLog`, and `SessionStateMachine`.
- GraphPatch write path: `GraphPatch`, `GraphPatchBuilder`, `GraphPatchValidator`, and `GraphPatchAuditor`.
- Memory health: `MemoryHealthCompiler` and `LifecycleStateManager`.
- Evolution boundaries: `CandidateTool`, `CandidateWorkflow`, `ToolCallSpecBuilder`, `FailureToConstraintExtractor`, and `Constraint`.
- Entrypoint: `helix plan` with optional `--event-log`.

## Intentionally Deferred Until Real Infrastructure Exists

- Concrete L0 database adapter.
- Concrete L1 healthy graph adapter.
- Initial full L0 graph population.
- Initial L1 materialized healthy graph.
- Real bioinformatics `ToolCallSpec` records.
- Real runtime backend adapters for CLI, Python, R, REST, database, container, and remote jobs.
- Domain-specific workflow templates.
- Domain-specific evidence sources and resource records.

These are deferred because the architecture requires real provenance, real ToolCall contracts, and audited GraphPatch writes. Adding fake bioinformatics tools or fake graph records would violate the design constraints.

## Remaining Architecture Gaps

- `ParameterSourceChecker` is not implemented.
- Deterministic workflow ranking tuple is not implemented beyond blocked-boundary behavior.
- `ResultSanityChecker` is not implemented.
- `EvidenceChecker` is not implemented.
- `PreferenceConsolidator` is not implemented.
- `ExperienceReplay`, `FailurePatternMiner`, `WorkflowPatternMiner`, and `QualityExperienceUpdater` are not implemented.
- `CapabilityGapDetector`, `WorkflowCandidateBuilder`, and `CapabilityPromotion` are not implemented.
- Concrete graph adapters are not implemented.
- Concrete runtime backend adapters are not implemented.
- API service endpoints are not implemented.

## Current Expected Behavior

Until L0/L1 data and active ToolCallSpec records exist, `helix plan` should return structured blocked plans instead of hallucinating a workflow.

That behavior is intentional and verified by tests.
