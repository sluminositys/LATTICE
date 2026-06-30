from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator
from typing_extensions import Self

from lattice.schemas.common import LatticeBaseModel, LifecycleState, Provenance

KnowledgeLayer = Literal[
    "task",
    "evidence",
    "workflow",
    "resource",
    "skill",
    "experience",
]

TaskNodeType = Literal[
    "Task",
    "TaskCategory",
    "DataType",
    "InputFormat",
    "Species",
    "StudyDesign",
    "OutputGoal",
    "TaskIntent",
    "TaskFingerprintTemplate",
]

EvidenceNodeType = Literal[
    "Paper",
    "Preprint",
    "OpenAccessArticle",
    "PaperSection",
    "EvidenceSpan",
    "Protocol",
    "BenchmarkStudy",
    "DatabaseRecord",
    "EvidenceSource",
    "ExternalEvidenceSource",
    "CuratorDecision",
]

WorkflowNodeType = Literal[
    "WorkflowTemplate",
    "WorkflowPath",
    "WorkflowStep",
    "Method",
    "QCStep",
    "AnalysisStep",
    "ValidationStep",
    "InterpretationStep",
    "RepairAction",
    "WorkflowPatch",
]

ResourceNodeType = Literal[
    "Tool",
    "Software",
    "Package",
    "Database",
    "API",
    "WebService",
    "ReferenceDataset",
    "AnnotationResource",
]

SkillNodeType = Literal[
    "ToolUsageSkill",
    "ParameterGuidance",
    "EnvironmentSpec",
    "FailureMode",
    "UsageConstraint",
    "RecoveryStrategy",
    "QualityCheckpoint",
]

ExperienceNodeType = Literal[
    "WorkflowLevelInsight",
    "TaskLevelConstraint",
    "MethodComparison",
    "CrossToolPattern",
    "DomainHeuristic",
    "FailureRecord",
    "SuccessPattern",
    "GraphPatchRecord",
    "LifecycleTransitionRecord",
]

HeterogeneousNodeType = (
    TaskNodeType
    | EvidenceNodeType
    | WorkflowNodeType
    | ResourceNodeType
    | SkillNodeType
    | ExperienceNodeType
)

TaskEdgeType = Literal[
    "BELONGS_TO",
    "ACCEPTS_DATA_TYPE",
    "REQUIRES_INPUT_FORMAT",
    "PRODUCES_OUTPUT_GOAL",
    "HAS_REQUIRED_CHECK",
    "HAS_EVIDENCE",
    "EXTRACTED_FROM",
]

EvidenceEdgeType = Literal[
    "REPORTS_METHOD",
    "REPORTS_WORKFLOW",
    "SUPPORTS_WORKFLOW",
    "SUPPORTS_CLAIM",
    "REFUTES_CLAIM",
    "BENCHMARKS_METHOD",
    "VALIDATED_BY",
    "REPORTS_EXPERIENCE",
]

WorkflowEdgeType = Literal[
    "HAS_STEP",
    "NEXT_STEP",
    "REQUIRES_INPUT",
    "PRODUCES_OUTPUT",
    "USES_METHOD",
    "USES_TOOL",
    "USES_DATABASE",
    "USES_REFERENCE",
    "VALIDATED_BY",
    "HAS_REPAIR_ACTION",
    "HAS_FAILURE_RISK",
]

ResourceEdgeType = Literal[
    "IMPLEMENTS_METHOD",
    "ACCEPTS_FORMAT",
    "PRODUCES_FORMAT",
    "ALTERNATIVE_TO",
    "INCOMPATIBLE_WITH",
    "FEEDS_INTO",
    "DEPENDS_ON",
    "COMPATIBLE_WITH",
    "QUERIES_DATABASE",
    "HAS_USAGE_SKILL",
]

SkillEdgeType = Literal[
    "HAS_PARAMETER_GUIDANCE",
    "HAS_ENVIRONMENT_SPEC",
    "HAS_FAILURE_MODE",
    "HAS_USAGE_CONSTRAINT",
    "HAS_RECOVERY_STRATEGY",
    "HAS_QUALITY_CHECKPOINT",
    "RECOVERABLE_BY",
    "SUPERSEDES_SKILL",
    "REQUIRES_SKILL",
]

ExperienceEdgeType = Literal[
    "GENERALIZED_TO",
    "CONTRADICTS",
    "REINFORCES",
    "SUMMARIZES_PATTERN",
    "GENERATED_PATCH",
    "UPDATED_LIFECYCLE_STATE",
    "DISTILLED_TO_SKILL",
    "SUPPORTS_SKILL_UPDATE",
]

HeterogeneousEdgeType = (
    TaskEdgeType
    | EvidenceEdgeType
    | WorkflowEdgeType
    | ResourceEdgeType
    | SkillEdgeType
    | ExperienceEdgeType
)

NODE_TYPES_BY_LAYER: dict[str, set[str]] = {
    "task": {
        "Task",
        "TaskCategory",
        "DataType",
        "InputFormat",
        "Species",
        "StudyDesign",
        "OutputGoal",
        "TaskIntent",
        "TaskFingerprintTemplate",
    },
    "evidence": {
        "Paper",
        "Preprint",
        "OpenAccessArticle",
        "PaperSection",
        "EvidenceSpan",
        "Protocol",
        "BenchmarkStudy",
        "DatabaseRecord",
        "EvidenceSource",
        "ExternalEvidenceSource",
        "CuratorDecision",
    },
    "workflow": {
        "WorkflowTemplate",
        "WorkflowPath",
        "WorkflowStep",
        "Method",
        "QCStep",
        "AnalysisStep",
        "ValidationStep",
        "InterpretationStep",
        "RepairAction",
        "WorkflowPatch",
    },
    "resource": {
        "Tool",
        "Software",
        "Package",
        "Database",
        "API",
        "WebService",
        "ReferenceDataset",
        "AnnotationResource",
    },
    "skill": {
        "ToolUsageSkill",
        "ParameterGuidance",
        "EnvironmentSpec",
        "FailureMode",
        "UsageConstraint",
        "RecoveryStrategy",
        "QualityCheckpoint",
    },
    "experience": {
        "WorkflowLevelInsight",
        "TaskLevelConstraint",
        "MethodComparison",
        "CrossToolPattern",
        "DomainHeuristic",
        "FailureRecord",
        "SuccessPattern",
        "GraphPatchRecord",
        "LifecycleTransitionRecord",
    },
}

EDGE_TYPES_BY_FAMILY: dict[str, set[str]] = {
    "task": {
        "BELONGS_TO",
        "ACCEPTS_DATA_TYPE",
        "REQUIRES_INPUT_FORMAT",
        "PRODUCES_OUTPUT_GOAL",
        "HAS_REQUIRED_CHECK",
        "HAS_EVIDENCE",
        "EXTRACTED_FROM",
    },
    "evidence": {
        "REPORTS_METHOD",
        "REPORTS_WORKFLOW",
        "SUPPORTS_WORKFLOW",
        "SUPPORTS_CLAIM",
        "REFUTES_CLAIM",
        "BENCHMARKS_METHOD",
        "VALIDATED_BY",
        "REPORTS_EXPERIENCE",
    },
    "workflow": {
        "HAS_STEP",
        "NEXT_STEP",
        "REQUIRES_INPUT",
        "PRODUCES_OUTPUT",
        "USES_METHOD",
        "USES_TOOL",
        "USES_DATABASE",
        "USES_REFERENCE",
        "VALIDATED_BY",
        "HAS_REPAIR_ACTION",
        "HAS_FAILURE_RISK",
    },
    "resource": {
        "IMPLEMENTS_METHOD",
        "ACCEPTS_FORMAT",
        "PRODUCES_FORMAT",
        "ALTERNATIVE_TO",
        "INCOMPATIBLE_WITH",
        "FEEDS_INTO",
        "DEPENDS_ON",
        "COMPATIBLE_WITH",
        "QUERIES_DATABASE",
        "HAS_USAGE_SKILL",
    },
    "skill": {
        "HAS_PARAMETER_GUIDANCE",
        "HAS_ENVIRONMENT_SPEC",
        "HAS_FAILURE_MODE",
        "HAS_USAGE_CONSTRAINT",
        "HAS_RECOVERY_STRATEGY",
        "HAS_QUALITY_CHECKPOINT",
        "RECOVERABLE_BY",
        "SUPERSEDES_SKILL",
        "REQUIRES_SKILL",
    },
    "experience": {
        "GENERALIZED_TO",
        "CONTRADICTS",
        "REINFORCES",
        "SUMMARIZES_PATTERN",
        "GENERATED_PATCH",
        "UPDATED_LIFECYCLE_STATE",
        "DISTILLED_TO_SKILL",
        "SUPPORTS_SKILL_UPDATE",
    },
}

ImplementationNodeType = SkillNodeType
ImplementationEdgeType = SkillEdgeType

HEALTHY_L1_STATES = {"active_hot", "active_warm"}


class OperationalProfile(LatticeBaseModel):
    usage_signal: dict[str, Any] = Field(default_factory=dict)
    success_contribution_signal: dict[str, Any] = Field(default_factory=dict)
    evidence_strength_signal: dict[str, Any] = Field(default_factory=dict)
    recency_signal: dict[str, Any] = Field(default_factory=dict)
    failure_risk_signal: dict[str, Any] = Field(default_factory=dict)
    preference_affinity_signal: dict[str, Any] = Field(default_factory=dict)
    pollution_risk_signal: dict[str, Any] = Field(default_factory=dict)
    graph_complexity_cost: dict[str, Any] = Field(default_factory=dict)
    lifecycle_state: LifecycleState
    last_compiled_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    compiled_from_graph_patch_ids: list[str] = Field(default_factory=list)


class BioEvoKGNode(LatticeBaseModel):
    node_id: str
    layer: KnowledgeLayer
    node_type: HeterogeneousNodeType
    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    attributes: dict[str, Any] = Field(default_factory=dict)
    lifecycle_state: LifecycleState
    operational_profile: OperationalProfile | None = None
    provenance: list[Provenance]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_layer_names(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if normalized.get("layer") == "implementation":
            normalized["layer"] = "skill"
        node_type_map = {
            "ToolImplementationProfile": "ToolUsageSkill",
            "AggregatedToolProfile": "ToolUsageSkill",
            "ConfigurationProfile": "ParameterGuidance",
            "ReferenceImplementationProfile": "EnvironmentSpec",
            "DatabaseImplementationProfile": "EnvironmentSpec",
            "FailureCondition": "FailureRecord",
            "Constraint": "TaskLevelConstraint",
            "RepairAction": "WorkflowLevelInsight",
            "QualitySignal": "SuccessPattern",
            "HistoricalSuccess": "SuccessPattern",
            "HistoricalFailure": "FailureRecord",
            "GraphPatch": "GraphPatchRecord",
            "LifecycleTransition": "LifecycleTransitionRecord",
        }
        node_type = normalized.get("node_type")
        if node_type in node_type_map:
            normalized["node_type"] = node_type_map[node_type]
        return normalized

    @field_validator("node_id", "canonical_name")
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not value.strip():
            msg = "node_id and canonical_name must be non-empty."
            raise ValueError(msg)
        return value

    @field_validator("provenance")
    @classmethod
    def require_provenance(cls, value: list[Provenance]) -> list[Provenance]:
        if not value:
            msg = "Bio-EvoKG nodes must have provenance."
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_layer_type_and_operational_profile(self) -> Self:
        allowed_types = NODE_TYPES_BY_LAYER[self.layer]
        if self.node_type not in allowed_types:
            msg = f"Node type {self.node_type} is not allowed in {self.layer} layer."
            raise ValueError(msg)
        if (
            self.operational_profile is not None
            and self.operational_profile.lifecycle_state != self.lifecycle_state
        ):
            msg = "Node operational_profile.lifecycle_state must match lifecycle_state."
            raise ValueError(msg)
        return self


class BioEvoKGEdge(LatticeBaseModel):
    edge_id: str
    edge_type: HeterogeneousEdgeType
    source_node_id: str
    target_node_id: str
    source_layer: KnowledgeLayer
    target_layer: KnowledgeLayer
    source_type: str
    attributes: dict[str, Any] = Field(default_factory=dict)
    lifecycle_state: LifecycleState
    operational_profile: OperationalProfile | None = None
    provenance: list[Provenance]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_edge_names(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        normalized = dict(data)
        if normalized.get("source_layer") == "implementation":
            normalized["source_layer"] = "skill"
        if normalized.get("target_layer") == "implementation":
            normalized["target_layer"] = "skill"
        edge_type_map = {
            "HAS_IMPLEMENTATION_PROFILE": "HAS_USAGE_SKILL",
            "HAS_FAILURE_CONDITION": "HAS_FAILURE_MODE",
            "HAS_CONSTRAINT": "HAS_USAGE_CONSTRAINT",
            "HAS_REPAIR_ACTION": "HAS_RECOVERY_STRATEGY",
            "HAS_QUALITY_SIGNAL": "HAS_QUALITY_CHECKPOINT",
        }
        edge_type = normalized.get("edge_type")
        if edge_type in edge_type_map:
            normalized["edge_type"] = edge_type_map[edge_type]
        return normalized

    @field_validator("edge_id", "source_node_id", "target_node_id", "source_type")
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not value.strip():
            msg = "edge_id, source_node_id, target_node_id, and source_type must be non-empty."
            raise ValueError(msg)
        return value

    @field_validator("provenance")
    @classmethod
    def require_provenance(cls, value: list[Provenance]) -> list[Provenance]:
        if not value:
            msg = "Bio-EvoKG edges must have provenance."
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_operational_profile(self) -> Self:
        if (
            self.operational_profile is not None
            and self.operational_profile.lifecycle_state != self.lifecycle_state
        ):
            msg = "Edge operational_profile.lifecycle_state must match lifecycle_state."
            raise ValueError(msg)
        return self


LAYER_ORDER = {
    "task": 1,
    "evidence": 2,
    "workflow": 3,
    "resource": 4,
    "skill": 5,
    "experience": 6,
}

L4_DATAFLOW_EDGE_TYPES = {"FEEDS_INTO", "DEPENDS_ON", "COMPATIBLE_WITH", "INCOMPATIBLE_WITH"}
L4_DATAFLOW_CONTEXT_KEYS = {"workflow_id", "workflow_temp_id", "stage_id", "stage_temp_id"}


class BioEvoKGGraphRecords(LatticeBaseModel):
    graph_tier: Literal["G0", "G1"]
    nodes: list[BioEvoKGNode] = Field(default_factory=list)
    edges: list[BioEvoKGEdge] = Field(default_factory=list)
    require_l1_operational_profile: bool = False
    require_l1_healthy_states: bool = False

    @model_validator(mode="after")
    def validate_graph_records(self) -> Self:
        nodes_by_id = {node.node_id: node for node in self.nodes}
        if len(nodes_by_id) != len(self.nodes):
            msg = "Bio-EvoKG graph records contain duplicate node_id values."
            raise ValueError(msg)

        edge_ids = {edge.edge_id for edge in self.edges}
        if len(edge_ids) != len(self.edges):
            msg = "Bio-EvoKG graph records contain duplicate edge_id values."
            raise ValueError(msg)

        for edge in self.edges:
            source = nodes_by_id.get(edge.source_node_id)
            target = nodes_by_id.get(edge.target_node_id)
            if source is None:
                msg = f"Edge {edge.edge_id} references missing source node."
                raise ValueError(msg)
            if target is None:
                msg = f"Edge {edge.edge_id} references missing target node."
                raise ValueError(msg)
            if edge.source_layer != source.layer:
                msg = f"Edge {edge.edge_id} source_layer does not match source node layer."
                raise ValueError(msg)
            if edge.target_layer != target.layer:
                msg = f"Edge {edge.edge_id} target_layer does not match target node layer."
                raise ValueError(msg)

            if not _is_allowed_main_graph_layer_relation(edge):
                msg = (
                    "Non-adjacent layer edge is not allowed in G0/G1 main graph unless "
                    "it is an L2->L6 evidence-support exception: "
                    f"{edge.edge_type} {edge.source_layer}->{edge.target_layer}"
                )
                raise ValueError(msg)
            if _is_l4_l4_edge(edge) and not _is_valid_l4_l4_dataflow_edge(edge):
                msg = (
                    "L4-L4 resource edges must be concrete dataflow/dependency/compatibility edges "
                    f"with L3 workflow or stage context: {edge.edge_type}"
                )
                raise ValueError(msg)

        if self.graph_tier == "G1" and self.require_l1_operational_profile:
            _assert_l1_operational_profiles(self.nodes, self.edges)
        if self.graph_tier == "G1" and self.require_l1_healthy_states:
            _assert_l1_healthy_states(self.nodes, self.edges)
        return self


def _is_allowed_main_graph_layer_relation(edge: BioEvoKGEdge) -> bool:
    if abs(LAYER_ORDER[edge.source_layer] - LAYER_ORDER[edge.target_layer]) <= 1:
        return True
    return (
        edge.source_layer == "evidence"
        and edge.target_layer == "experience"
        and edge.edge_type == "REPORTS_EXPERIENCE"
    )


def _is_l4_l4_edge(edge: BioEvoKGEdge) -> bool:
    return edge.source_layer == "resource" and edge.target_layer == "resource"


def _is_valid_l4_l4_dataflow_edge(edge: BioEvoKGEdge) -> bool:
    if edge.edge_type not in L4_DATAFLOW_EDGE_TYPES:
        return False
    return any(edge.attributes.get(key) for key in L4_DATAFLOW_CONTEXT_KEYS)


def _assert_l1_operational_profiles(
    nodes: list[BioEvoKGNode],
    edges: list[BioEvoKGEdge],
) -> None:
    for node in nodes:
        if node.operational_profile is None:
            msg = f"L1 node {node.node_id} is missing OperationalProfile."
            raise ValueError(msg)
    for edge in edges:
        if edge.operational_profile is None:
            msg = f"L1 edge {edge.edge_id} is missing OperationalProfile."
            raise ValueError(msg)


def _assert_l1_healthy_states(
    nodes: list[BioEvoKGNode],
    edges: list[BioEvoKGEdge],
) -> None:
    for node in nodes:
        if node.lifecycle_state not in HEALTHY_L1_STATES:
            msg = f"L1 node {node.node_id} is not in a healthy default state."
            raise ValueError(msg)
    for edge in edges:
        if edge.lifecycle_state not in HEALTHY_L1_STATES:
            msg = f"L1 edge {edge.edge_id} is not in a healthy default state."
            raise ValueError(msg)
