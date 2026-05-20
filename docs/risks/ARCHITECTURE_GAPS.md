# HELIX Architecture Gaps And Risks

Source architecture: `E:\donwloads\HELIX_architecture_v7.md`

This file records possible model, architecture, or engineering risks discovered while implementing HELIX. Items here are not blockers by default; they are decisions or constraints that need to be tracked explicitly.

## Open Items

### RISK-001: Graph backend is not specified

The v7 architecture defines L0, L1, L2 behavior clearly, but does not choose a storage backend. This affects transactionality, provenance queries, controlled recall, and materialized L1 compilation.

Current handling: implement graph stores as protocols first. Defer backend choice until the core contracts are stable.

### RISK-002: Workflow path search can become too domain-specific too early

The architecture requires bioinformatics-aware path search, but adding hard-coded biological workflow rules before schemas and provenance are stable would create brittle code.

Current handling: start with explicit contracts, hard constraints, and deterministic ordering signals. Add domain rules only through config or graph data.

### RISK-003: MemoryHealthCompiler needs policy-driven transitions, not fixed scores

The document explicitly avoids a fixed weighted formula for operational signals. A naive implementation could accidentally turn health compilation into a hidden score model.

Current handling: implement lifecycle transition policies as named rules loaded from configuration.

### RISK-004: Controlled L0 recall can leak low-quality knowledge into planning

The architecture allows controlled full graph recall when L1 is insufficient. Without strict temporary candidate status, low-provenance or deprecated material could influence plans incorrectly.

Current handling: enforce recall result statuses and make verifier/permission checks mandatory before any use.

### RISK-005: PlanMode exit conditions may be underspecified for real execution

The document lists exit conditions, but real execution will also need environment availability, tool installation checks, and data sensitivity checks.

Current handling: keep execution disabled until ToolCallSpec, PermissionGate, runtime backend, and environment checks exist.

### RISK-006: Experience layer could overgeneralize from sparse events

The architecture warns that single failures and single user feedback should not become global rules. This needs hard tests.

Current handling: add tests preventing one event from becoming a global blocker or lab preference without scope and approval.

### RISK-007: Initial task fingerprinting is conservative and incomplete

The first implementation creates a valid `TaskFingerprint` without inferring domain semantics. This avoids silent hallucinated classification, but it means the early plan-only flow will usually produce `unclassified` tasks until an LLM-backed or graph-backed fingerprinter is added.

Current handling: keep the prompt externalized and record missing fields in `ambiguity_items`.
