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
    "implementation",
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

ImplementationNodeType = Literal[
    "ToolImplementationProfile",
    "AggregatedToolProfile",
    "ConfigurationProfile",
    "ReferenceImplementationProfile",
    "DatabaseImplementationProfile",
]

ExperienceNodeType = Literal[
    "ExecutionTrace",
    "ExecutionEvent",
    "ToolCallEvent",
    "FailureCondition",
    "Constraint",
    "RepairAction",
    "UserFeedback",
    "UserPreference",
    "LabPreference",
    "HistoricalSuccess",
    "HistoricalFailure",
    "QualitySignal",
    "GraphPatch",
    "LifecycleTransition",
]

HeterogeneousNodeType = (
    TaskNodeType
    | EvidenceNodeType
    | WorkflowNodeType
    | ResourceNodeType
    | ImplementationNodeType
    | ExperienceNodeType
)

TaskEdgeType = Literal[
    "BELONGS_TO",
    "ACCEPTS_DATA_TYPE",
    "REQUIRES_INPUT_FORMAT",
    "PRODUCES_OUTPUT_GOAL",
    "HAS_REQUIRED_CHECK",
    "HAS_EVIDENCE",
]

EvidenceEdgeType = Literal[
    "REPORTS_METHOD",
    "REPORTS_WORKFLOW",
    "SUPPORTS_WORKFLOW",
    "SUPPORTS_CLAIM",
    "REFUTES_CLAIM",
    "BENCHMARKS_METHOD",
    "VALIDATED_BY",
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
    "QUERIES_DATABASE",
    "HAS_IMPLEMENTATION_PROFILE",
]

ImplementationEdgeType = Literal[
    "HAS_FAILURE_CONDITION",
    "HAS_CONSTRAINT",
    "HAS_REPAIR_ACTION",
    "HAS_QUALITY_SIGNAL",
]

ExperienceEdgeType = Literal[
    "CALLED_TOOLCALL",
    "FAILED_WITH",
    "GENERALIZED_TO",
    "TRIGGERED_BY",
    "PREFERS",
    "AVOIDS",
    "GENERATED_PATCH",
    "UPDATED_LIFECYCLE_STATE",
]

HeterogeneousEdgeType = (
    TaskEdgeType
    | EvidenceEdgeType
    | WorkflowEdgeType
    | ResourceEdgeType
    | ImplementationEdgeType
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
    "implementation": {
        "ToolImplementationProfile",
        "AggregatedToolProfile",
        "ConfigurationProfile",
        "ReferenceImplementationProfile",
        "DatabaseImplementationProfile",
    },
    "experience": {
        "ExecutionTrace",
        "ExecutionEvent",
        "ToolCallEvent",
        "FailureCondition",
        "Constraint",
        "RepairAction",
        "UserFeedback",
        "UserPreference",
        "LabPreference",
        "HistoricalSuccess",
        "HistoricalFailure",
        "QualitySignal",
        "GraphPatch",
        "LifecycleTransition",
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
    },
    "evidence": {
        "REPORTS_METHOD",
        "REPORTS_WORKFLOW",
        "SUPPORTS_WORKFLOW",
        "SUPPORTS_CLAIM",
        "REFUTES_CLAIM",
        "BENCHMARKS_METHOD",
        "VALIDATED_BY",
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
        "QUERIES_DATABASE",
        "HAS_IMPLEMENTATION_PROFILE",
    },
    "implementation": {
        "HAS_FAILURE_CONDITION",
        "HAS_CONSTRAINT",
        "HAS_REPAIR_ACTION",
        "HAS_QUALITY_SIGNAL",
    },
    "experience": {
        "CALLED_TOOLCALL",
        "FAILED_WITH",
        "GENERALIZED_TO",
        "TRIGGERED_BY",
        "PREFERS",
        "AVOIDS",
        "GENERATED_PATCH",
        "UPDATED_LIFECYCLE_STATE",
    },
}

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
    "implementation": 5,
    "experience": 6,
}


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

            if abs(LAYER_ORDER[edge.source_layer] - LAYER_ORDER[edge.target_layer]) > 1:
                msg = (
                    "Non-adjacent layer edge is not allowed in G0/G1 main graph: "
                    f"{edge.edge_type} {edge.source_layer}->{edge.target_layer}"
                )
                raise ValueError(msg)

        if self.graph_tier == "G1" and self.require_l1_operational_profile:
            _assert_l1_operational_profiles(self.nodes, self.edges)
        if self.graph_tier == "G1" and self.require_l1_healthy_states:
            _assert_l1_healthy_states(self.nodes, self.edges)
        return self


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
