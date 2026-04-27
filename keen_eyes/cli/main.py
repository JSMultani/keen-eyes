from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from keen_eyes.orchestrator import Orchestrator, RequirementsPlanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="keen-eyes")
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan", help="Parse a task and produce a validation plan.")
    plan.add_argument("--task", required=True)
    run = sub.add_parser("run", help="Run the Keen Eyes pipeline.")
    run.add_argument("--task", required=True)
    run.add_argument("--project", required=True)
    run.add_argument("--out", default="runs/local")
    run.add_argument("--run-id", default="local-run")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "plan":
        plan = RequirementsPlanner().plan(Path(args.task))
        print(json.dumps(asdict(plan), indent=2))
        return 0 if plan.ready else 2
    if args.command == "run":
        report = Orchestrator().run(Path(args.task), Path(args.project), Path(args.out), args.run_id)
        print(json.dumps({"run_id": report.run_id, "passed": report.passed, "out": args.out}, indent=2))
        return 0 if report.passed else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

