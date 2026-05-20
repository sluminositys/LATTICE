from __future__ import annotations

import argparse
import json
from typing import Any

from pydantic import BaseModel

from helix.orchestration import run_plan_only
from helix.runtime import FileAgentEventLog


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="helix")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Run the HELIX plan-only flow.")
    plan_parser.add_argument("request", help="User request to plan.")
    plan_parser.add_argument("--session-id", default=None)
    plan_parser.add_argument("--event-log", default=None, help="Optional JSONL event log path.")

    args = parser.parse_args(argv)
    if args.command == "plan":
        event_log = FileAgentEventLog(args.event_log) if args.event_log else None
        state = run_plan_only(args.request, session_id=args.session_id, event_log=event_log)
        print(json.dumps(_to_jsonable(state), ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
