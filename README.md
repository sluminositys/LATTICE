# LATTICE

**Layered Agent for Tool-Augmented Task Intelligence, Curation, and Evolution in Genomics and Bioinformatics**

LATTICE 是一个独立的 Python agent-native workflow knowledge graph system，用于把用户提出的生物信息学研究需求转化为可检索、可验证、可执行、可审计、可持续进化的工作流。

系统核心不是把大模型包装成问答接口，而是围绕三层图谱和 ToolCall 执行闭环工作：

- L0 Persistent Full Bio-EvoKG：保存完整知识、候选能力、执行经验、GraphPatch、审计和生命周期记录。
- L1 Memory-Healthy Working Bio-EvoKG：由健康化策略筛选出的默认工作图，只保留可默认参与规划和执行的健康内容。
- L2 Task-conditioned Runtime GraphContext：每次请求从 L1 动态投影出的五个运行时子图，用于当次规划、执行和验证。

L0 和 L1 使用同一套六层异构图 schema：

- Task
- Evidence
- Workflow
- Resource
- Implementation
- Experience

demo 模式和正式模式也使用同一套 schema。demoL0/demoL1 的构建过程在项目外完成，最终资产可以随系统打包进入 demo 模式；运行时只读取 demoL0/demoL1，不启动 builder、evolution 或图写入。正式模式同样支持外部构建好的 L0/L1 资产导入，并通过数据库适配器接入 Neo4j、PostgreSQL 和 Qdrant。

当前仓库不内置示例实验、虚假接口、mock 数据集或预设领域工作流。真实图资产、工具能力和领域内容都应通过 schema 校验、资产导入、ToolCallSpec 注册和 GraphPatch 治理进入系统。

## 当前能力

- LangGraph 编排的规划流程和可执行流程。
- TaskFingerprint、RuntimeGraphContext、AgenticExecutionPlan、ToolCallSpec、StructuredObservation、GraphPatch 等核心 schema。
- L0/L1 六层异构图节点、边、OperationalProfile 和资产校验。
- demo/production graph profile 策略，以及只读 demo 图运行模式。
- Neo4j L0/L1 图存储适配器。
- PostgreSQL core table 初始化、AgentEventLog 和 ToolCallSpec store。
- Qdrant 图节点向量索引适配器。
- CLI / Python / REST / database / containerized CLI RuntimeBackend。
- ToolCall 注册、校验、派发和失败关闭。
- 能力缺口检测、候选进化请求、候选工具和 ToolCallSpec GraphPatch 生成。
- 执行经验转 Experience 层 GraphPatch，并可经审计后写入 L0。
- MemoryHealthCompiler、生命周期状态管理、controlled L0 recall 和 HookBus 边界。

## 常用命令

```powershell
uv sync --dev
uv run pytest
uv run ruff check .
uv run mypy
```

```powershell
uv run lattice --help
uv run lattice db init-postgres --config-dir config
uv run lattice graph validate-assets --l0-path <L0资产目录> --l1-path <L1资产目录>
uv run lattice graph import-assets --config-dir config --graph-profile <profile> --tier L0 --asset-path <L0资产目录>
uv run lattice plan "<用户请求>" --config-dir config --graph-profile <profile>
uv run lattice execute "<用户请求>" --config-dir config --graph-profile <profile>
```

运行日志、命令记录、诊断输出和临时产物应放在 `D:\workspace\codex` 下，不直接写到仓库根目录。
