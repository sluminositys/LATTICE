from __future__ import annotations

from helix.schemas import GraphContextSufficiencyReport, RuntimeGraphContext


class GraphContextSufficiencyChecker:
    def check(self, context: RuntimeGraphContext) -> GraphContextSufficiencyReport:
        return context.sufficiency_report

    def requires_controlled_recall(self, context: RuntimeGraphContext) -> bool:
        report = self.check(context)
        return report.status == "insufficient" and report.controlled_recall_required
