# file: scripts/check_eval_baseline.py
# description: CI gate — require separate single-agent vs swarm metrics in baseline JSON
# reference: evals/baselines/latest.json, docs/EVALS.md
"""Fail if eval baseline cannot report single-agent and swarm results separately."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _derive(data: dict) -> dict[str, dict[str, int | float]]:
    results = data.get("results") or []
    single = [r for r in results if r.get("mode") == "single"]
    swarm = [r for r in results if r.get("mode") == "swarm"]
    if not single and not swarm:
        return {}

    def pack(rows: list) -> dict[str, int | float]:
        success = sum(1 for r in rows if r.get("status") == "success")
        return {
            "total": len(rows),
            "passed": success,
            "failed": len(rows) - success,
            "pass_rate": (success / len(rows)) if rows else 0.0,
        }

    return {"single_agent": pack(single), "swarm": pack(swarm)}


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--write"]
    write_back = "--write" in sys.argv
    path = Path(args[0] if args else "evals/baselines/latest.json")
    if not path.is_file():
        print(f"SKIP: baseline missing at {path}")
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))

    summary = data.get("summary") or {}
    if "single_agent_pass" in summary and "swarm_pass" in summary:
        print("OK: summary has single_agent_pass and swarm_pass")
        return 0
    if data.get("single_agent") and data.get("swarm"):
        print("OK: separate single_agent/swarm objects present")
        return 0

    derived = _derive(data)
    if not derived:
        print(
            "FAIL: baseline must expose separate single-agent and swarm metrics "
            "(results[].mode == single|swarm, or summary.single_agent_pass + swarm_pass)"
        )
        return 1

    print(
        "OK: derived from results — "
        f"single {derived['single_agent']['passed']}/{derived['single_agent']['total']}, "
        f"swarm {derived['swarm']['passed']}/{derived['swarm']['total']}"
    )
    if write_back:
        data["summary"] = {
            "single_agent_pass": f"{derived['single_agent']['passed']}/{derived['single_agent']['total']}",
            "swarm_pass": f"{derived['swarm']['passed']}/{derived['swarm']['total']}",
            "single_agent": derived["single_agent"],
            "swarm": derived["swarm"],
            "note": "Do not aggregate swarm into a headline dominated by single-agent burns.",
        }
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"wrote summary into {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
