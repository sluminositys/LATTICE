# HELIX Decisions

## DEC-001: Repository Location

Status: accepted

Use `D:\workspace\HELIX` as the project repository. Keep `D:\workspace` as a parent workspace only.

## DEC-002: Build Order

Status: accepted

Build tracking docs first, then `uv` project metadata, then config, schemas, event log, graph boundaries, and only then LangGraph orchestration.

## DEC-003: First Runtime Mode

Status: accepted

The first usable HELIX flow is `plan_only`. Tool execution remains disabled until ToolCall registry, PermissionGate, and runtime backend checks are implemented.

## DEC-004: Graph Store Backend

Status: pending

Do not choose a concrete graph database in the first implementation pass. Define L0/L1 store protocols first.
