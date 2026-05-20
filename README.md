# HELIX

HELIX is an independent Python agent system based on the v7 architecture in `E:\donwloads\HELIX_architecture_v7.md`.

The implementation starts with a plan-only flow and expands toward controlled execution, graph patching, memory health compilation, and experience-driven capability evolution.

## Development

```powershell
uv sync --dev
uv run pytest
uv run helix plan "Plan RNA-seq QC workflow"
uv run helix plan "Plan RNA-seq QC workflow" --event-log D:/workspace/codex/logs/2026-05-21/helix-plan-events.jsonl
```

Operational logs, command transcripts, diagnostics, and generated artifacts should be stored under `D:\workspace\codex`, not in this repository.
