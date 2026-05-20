# Task Fingerprint Prompt

Extract a HELIX `TaskFingerprint` from the user request.

Return structured fields only. If a field is ambiguous or not present, record it in `ambiguity_items` instead of guessing.

Required fields:

- task
- task_category
- data_types
- input_formats
- output_goals
- execution_intent
- environment_constraints
- preference_scope
- ambiguity_items
