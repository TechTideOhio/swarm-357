#!/usr/bin/env python3
"""Validate and report on config/swarm.yaml roster.

Usage:
    python scripts/generate_roster.py              # validate + print summary
    python scripts/generate_roster.py --layer seo  # filter by layer
    python scripts/generate_roster.py --fix-counts # assert exact counts
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROSTER_PATH = REPO_ROOT / "config" / "swarm.yaml"

EXPECTED_COUNTS: dict[str, int] = {
    "management": 10,
    "sales": 62,
    "support": 55,
    "marketing": 68,
    "seo": 47,
    "research": 58,
    "operations": 57,
}
EXPECTED_TOTAL = 357


def load_roster() -> list[dict]:
    if not ROSTER_PATH.is_file():
        print(f"ERROR: {ROSTER_PATH} not found", file=sys.stderr)
        sys.exit(1)
    data = yaml.safe_load(ROSTER_PATH.read_text(encoding="utf-8"))
    return data.get("agents", [])


def validate(agents: list[dict], layer_filter: str | None = None) -> bool:
    filtered = agents if layer_filter is None else [a for a in agents if a["layer"] == layer_filter]

    by_layer: dict[str, list[dict]] = {}
    for a in agents:
        by_layer.setdefault(a["layer"], []).append(a)

    # Check for duplicate names
    names = [a["name"] for a in agents]
    dupes = [n for n in set(names) if names.count(n) > 1]

    # Check soul paths exist
    missing_souls: list[str] = []
    for a in filtered:
        soul = a.get("soul", "")
        if soul and not (REPO_ROOT / soul).is_file():
            missing_souls.append(f"{a['name']} → {soul}")

    ok = True

    print(f"{'Layer':<15} {'Count':>6}  {'Expected':>8}  {'Delta':>6}  {'Models'}")
    print("-" * 65)
    for layer, expected in sorted(EXPECTED_COUNTS.items()):
        layer_agents = by_layer.get(layer, [])
        count = len(layer_agents)
        delta = count - expected
        model_summary = {}
        for a in layer_agents:
            m = a.get("model", "?")
            model_summary[m] = model_summary.get(m, 0) + 1
        model_str = "  ".join(f"{m}×{n}" for m, n in sorted(model_summary.items()))
        flag = "" if delta == 0 else f"  ← WRONG ({delta:+})"
        print(f"  {layer:<13} {count:>6}  {expected:>8}  {delta:>+6}  {model_str}{flag}")
        if delta != 0:
            ok = False

    total = len(agents)
    total_delta = total - EXPECTED_TOTAL
    print("-" * 65)
    print(f"  {'TOTAL':<13} {total:>6}  {EXPECTED_TOTAL:>8}  {total_delta:>+6}")
    if total_delta != 0:
        ok = False

    print()
    if dupes:
        print(f"DUPLICATE NAMES ({len(dupes)}):")
        for d in dupes:
            print(f"  {d}")
        ok = False
    else:
        print("No duplicate names.")

    if missing_souls:
        print(f"\nMISSING SOUL FILES ({len(missing_souls)}):")
        for m in missing_souls:
            print(f"  {m}")
        ok = False
    else:
        print("All soul file paths present.")

    # Check: no two different roles share the same soul file
    from collections import defaultdict
    role_to_soul: dict[str, str] = {}
    for a in agents:
        role = a.get("role", "")
        soul = a.get("soul", "")
        if role not in role_to_soul:
            role_to_soul[role] = soul
    soul_to_roles: dict[str, list[str]] = defaultdict(list)
    for role, soul in role_to_soul.items():
        soul_to_roles[soul].append(role)
    shared_souls = {s: r for s, r in soul_to_roles.items() if len(r) > 1}
    if shared_souls:
        print(f"\nSHARED SOUL FILES (different roles reusing same soul — each role must be unique):")
        for soul, roles in shared_souls.items():
            print(f"  {soul}: {roles}")
        ok = False
    else:
        print(f"Soul uniqueness: {len(role_to_soul)} unique roles, {len(soul_to_roles)} unique soul files. OK.")

    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate config/swarm.yaml roster")
    parser.add_argument("--layer", help="Filter output to one layer")
    parser.add_argument("--fix-counts", action="store_true", help="Exit non-zero if counts wrong")
    args = parser.parse_args()

    agents = load_roster()
    ok = validate(agents, layer_filter=args.layer)

    if args.fix_counts and not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
