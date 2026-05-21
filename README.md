# HELIX

HELIX 是一个独立的 Python agent 系统，用于把用户任务转化为可审计、可阻断、可逐步执行的工作流计划。系统当前优先实现核心 agent 主流程、图上下文投影、计划门控、工具调用边界、事件日志和后续能力演化接口。

当前仓库不内置示例实验、mock data、虚假工具接口或预设领域工作流。真实工具、数据库、L0 全量图和 L1 healthy graph 后续应通过受控接口接入，并保留 provenance、审计和生命周期状态。

## 当前能力

- 基于 LangGraph 的 plan-only 主编排流程
- 任务指纹、运行时图上下文投影和上下文充分性检查
- workflow path 搜索、验证和退出门控
- ToolCallSpec 注册、校验、派发和 runtime backend 协议
- GraphPatch、图存储、MemoryHealthCompiler 和 controlled recall 的接口边界
- HookBus、事件日志、session 状态机和候选能力演化模块
- 基于 `uv` 的 Python 环境管理

## 开发命令

```powershell
uv sync --dev
uv run pytest
uv run ruff check .
uv run mypy
```

查看 CLI 入口：

```powershell
uv run helix --help
```

运行日志、命令记录、诊断输出和临时产物应放在 `D:\workspace\codex` 下，不直接写到仓库根目录。
