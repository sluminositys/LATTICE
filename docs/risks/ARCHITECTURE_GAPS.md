# HELIX Architecture Gaps And Risks

Design source: user-provided HELIX architecture planning document.

This file records possible model, architecture, or engineering risks discovered while implementing HELIX. Items here are not blockers by default; they are decisions or constraints that need to be tracked explicitly.

## Open Items

### RISK-001: Graph backend is not specified

The source architecture defines L0, L1, L2 behavior clearly, but does not choose a storage backend. This affects transactionality, provenance queries, controlled recall, and materialized L1 compilation.

Current handling: implement graph stores as protocols first. Defer backend choice until the core contracts are stable.

Follow-up: `docs/architecture/DATABASE_REQUIREMENTS.md` defines the adapter requirements and minimum L0/L1 primitives so a future database can be installed without changing agent-layer code.

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

Current handling: execution now exists behind ToolCallSpec, PermissionGate, RuntimeBackend, and fail-closed dispatcher checks. Environment availability and data sensitivity policies still need dedicated checks before broad unattended execution.

### RISK-006: Experience layer could overgeneralize from sparse events

The architecture warns that single failures and single user feedback should not become global rules. This needs hard tests.

Current handling: add tests preventing one event from becoming a global blocker or lab preference without scope and approval.

### RISK-007: Initial task fingerprinting is conservative and incomplete

The first implementation creates a valid `TaskFingerprint` without inferring domain semantics. This avoids silent hallucinated classification, but it means the early plan-only flow will usually produce `unclassified` tasks until an LLM-backed or graph-backed fingerprinter is added.

Current handling: keep the prompt externalized and record missing fields in `ambiguity_items`.

### RISK-008: Externally built L0/L1 assets can be structurally valid but semantically weak

The current system can validate six-layer schema, provenance, lifecycle states, and L1 operational profiles. It cannot prove that externally supplied literature-derived graph content is biologically complete or methodologically correct by schema alone.

Current handling: external L0/L1 assets must enter through graph asset validation/import, and runtime execution remains gated by workflow verification, PermissionGate, ToolCallSpec validation, and experience logging.

### RISK-009: Tool discovery must not bypass lifecycle governance

The evolution path can propose new tools and ToolCallSpec records, but any direct activation of discovered tools would bypass memory health and approval controls.

Current handling: `ToolBuilderAgent` only creates candidate graph mutations. Candidate ToolCallSpec records are not active in `ToolCallRegistry` until promoted through lifecycle policy.

### RISK-010: Runtime backend power differs by agent role

Execution agents should not mutate graphs freely, while evolution and tool-building agents need to propose graph mutations and candidate ToolCallSpec records. Treating all agents with one permission rule would either make execution unsafe or make evolution useless.

Current handling: normal execution writes only structured experience candidates through audited L0 GraphPatch. Capability evolution creates candidate L0 GraphPatch records, not direct L1 writes or active tools.
