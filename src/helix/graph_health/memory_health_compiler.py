from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Literal

from pydantic import Field

from helix.graph import GraphTierPolicy
from helix.schemas import GraphPatch, HelixBaseModel


class MemoryHealthCompileReport(HelixBaseModel):
    report_id: str
    status: Literal["completed", "skipped"]
    compiled_patch_ids: list[str] = Field(default_factory=list)
    materialized_l1: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MemoryHealthCompiler:
    def __init__(self, graph_tier_policy: GraphTierPolicy | None = None) -> None:
        self.graph_tier_policy = graph_tier_policy or GraphTierPolicy()

    def compile(self, patches: Iterable[GraphPatch]) -> MemoryHealthCompileReport:
        patch_list = list(patches)
        if not patch_list:
            return MemoryHealthCompileReport(
                report_id="mhc-skipped-no-patches",
                status="skipped",
            )

        for patch in patch_list:
            self.graph_tier_policy.assert_patch_targets_l0(patch)

        return MemoryHealthCompileReport(
            report_id="mhc-completed",
            status="completed",
            compiled_patch_ids=[patch.patch_id for patch in patch_list],
            materialized_l1=True,
        )
