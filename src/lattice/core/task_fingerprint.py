from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from lattice.schemas import TaskFingerprint


class TaskFingerprinter:
    """Conservative task fingerprint boundary.

    The first implementation does not infer bioinformatics semantics. It creates a valid
    `TaskFingerprint`, preserves the original request, and records unknown fields as ambiguity.
    """

    def __init__(self, prompt_path: str | Path = "config/prompts/task_fingerprint.md") -> None:
        self.prompt_path = Path(prompt_path)

    def fingerprint(self, request: str, *, user_id: str = "local") -> TaskFingerprint:
        normalized_request = request.strip()
        return TaskFingerprint(
            fingerprint_id=f"tf-{uuid4()}",
            user_id=user_id,
            task=normalized_request,
            task_category="unclassified",
            execution_intent="plan_only",
            ambiguity_items=[
                "task_category",
                "data_types",
                "input_formats",
                "output_goals",
            ],
        )
