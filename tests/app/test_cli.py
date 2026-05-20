import json

from helix.app.cli import main


def test_cli_plan_outputs_blocked_plan(capsys) -> None:
    exit_code = main(["plan", "Plan RNA-seq QC", "--session-id", "session-1"])

    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["status"] == "plan_blocked"
    assert output["task_fingerprint"]["execution_intent"] == "plan_only"
    assert output["permission_decision"]["allowed"] is False
