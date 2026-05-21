# HELIX

HELIX 是一个独立的 Python agent 系统，用于把用户任务转化为可审计、可阻断、可逐步执行的工作流计划。系统当前优先实现核心 agent 主流程、图上下文投影、计划门控、工具调用边界、事件日志、正式构图接口和能力演化接口。

HELIX 支持两类图运行 profile：正式模式和 demo 模式。正式模式由 HELIX 的 builder/evolution 流程根据用户配置的数据库、LLM provider 和研究领域逐步构建 L0，并通过 MemoryHealthCompiler 生成 L1 healthy graph。demo 模式只读取随系统打包的 demoL0 和 demoL1 图资产；demo 图的构建过程在项目外部完成，运行时不启动 builder、evolution 或 GraphPatch 写入。两种模式使用同一套 schema、graph store 结构和 runtime 读取路径。

当前仓库不内置示例实验、mock data、虚假工具接口或预设领域工作流。正式图与后续 demo 图资产都必须保留 provenance、审计信息、生命周期状态和 schema 版本。

## 当前能力

- 基于 LangGraph 的 plan-only 主编排流程
- 任务指纹、运行时图上下文投影和上下文充分性检查
- workflow path 搜索、验证和退出门控
- ToolCallSpec 注册、校验、派发和 runtime backend 协议
- GraphPatch、图存储、MemoryHealthCompiler 和 controlled recall 的接口边界
- demo/production graph profile schema 与只读 demo policy
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
