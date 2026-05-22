# LATTICE Architecture Decomposition

Design source: user-provided LATTICE architecture planning document.

## Core Invariants

- All new knowledge enters L0 first.
- L1 is generated only by `MemoryHealthCompiler`.
- L2 is a per-request runtime context, not a storage layer.
- L0/L1 database adapters stay behind graph store protocols until a concrete backend is installed.
- No workflow execution happens without `TaskFingerprint`.
- No path search happens without `RuntimeGraphContext`.
- No ToolCall happens without verified AEP, `ToolCallSpec`, and `PermissionGate`.
- No experience is written without `AgentEventLog`.
- No graph mutation happens without `GraphPatch`.
- Natural-language reflection is not a long-term memory primitive.

## Independent Module Groups

### Foundation

- `config`: external settings and runtime policy.
- `schemas`: Pydantic contracts shared across modules.
- `runtime`: event log, session state, task state, observations.
- `hooks`: lifecycle event bus.

### Graph Knowledge System

- `graph`: L0 and L1 store protocols, graph tier policy.
- `projection`: L2 five-view context projection.
- `graph_patch`: graph write path and auditing.
- `graph_health`: health compilation from L0 to L1.

### Agent Planning System

- `orchestration`: LangGraph state machine.
- `core`: task fingerprinting, provenance, response generation.
- `planning`: workflow path search and AEP compilation.
- `verification`: workflow and claim verification.
- `permissions`: plan mode, permission gate, risk policies.

### Execution System

- `toolcall`: registry, schemas, validators, dispatcher, observations.
- `toolcall.backends`: real backend adapters only after contracts exist.

### Evolution System

- `memory`: experience replay, failure-to-constraint, preference consolidation.
- `capability_evolution`: new tool and workflow candidate lifecycle.

## First Usable Flow

The first usable flow is intentionally plan-only:

```text
request
  -> TaskFingerprint
  -> RuntimeGraphContext or insufficiency report
  -> CandidateWorkflowPathSet or blocked reason
  -> WorkflowAuditReport
  -> AgenticExecutionPlan if verified
  -> PermissionGate decision
  -> response
  -> AgentEventLog
```

Tool execution, graph writes, memory health compilation, and evolution are added after this flow is stable.

## Initial Python Package Layout

```text
src/lattice/
  app/
  capability_evolution/
  config/
  core/
  graph/
  graph_health/
  graph_patch/
  hooks/
  memory/
  orchestration/
  permissions/
  planning/
  projection/
  runtime/
  schemas/
  toolcall/
    backends/
  verification/
```
