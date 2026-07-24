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
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
ROSTER_PATH = REPO_ROOT / "config" / "swarm.yaml"
COMPACT_PATH = REPO_ROOT / "config" / "swarm-compact.yaml"

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


def expand_compact_roster(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Mirror Swarm._expand_compact_roster() — keep in sync with techtide_swarm.swarm.Swarm."""
    layers = raw.get("layers", {})
    agents: list[dict[str, Any]] = []
    for layer_name, layer_cfg in layers.items():
        default_soul = layer_cfg.get("soul", "")
        soul_overrides = layer_cfg.get("soul_overrides", {})
        for role_name, role_cfg in layer_cfg.get("roles", {}).items():
            count = int(role_cfg.get("count", 1))
            soul = soul_overrides.get(role_name, default_soul)
            for i in range(1, count + 1):
                agents.append({
                    "name": f"{layer_name}-{role_name.replace('_', '-')}-{i:03d}",
                    "layer": layer_name,
                    "role": role_name,
                    "soul": soul,
                    "model": role_cfg.get("model", "sonnet"),
                    "budget_usd": role_cfg.get("budget_usd", 1.0),
                    "tools": role_cfg.get("tools", ["Read", "Write"]),
                })
    return agents


def load_compact_roster() -> list[dict]:
    """Load config/swarm-compact.yaml and return expanded flat agents list."""
    if not COMPACT_PATH.is_file():
        print(f"ERROR: {COMPACT_PATH} not found", file=sys.stderr)
        sys.exit(1)
    raw = yaml.safe_load(COMPACT_PATH.read_text(encoding="utf-8")) or {}
    return expand_compact_roster(raw)


def validate(
    agents: list[dict],
    layer_filter: str | None = None,
    *,
    check_role_soul_uniqueness: bool = True,
) -> bool:
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
    if check_role_soul_uniqueness:
        if shared_souls:
            print(
                "\nSHARED SOUL FILES (different roles reusing same soul — "
                "each role must be unique in flat roster):"
            )
            for soul, roles in shared_souls.items():
                print(f"  {soul}: {roles}")
            ok = False
        else:
            print(
                f"Soul uniqueness: {len(role_to_soul)} unique roles, "
                f"{len(soul_to_roles)} unique soul files. OK."
            )
    else:
        print("(Compact mode: skipped per-role soul uniqueness — instances may share soul files.)")

    return ok


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate swarm roster (flat or compact)")
    parser.add_argument("--layer", help="Filter output to one layer")
    parser.add_argument("--fix-counts", action="store_true", help="Exit non-zero if counts wrong")
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Validate config/swarm-compact.yaml expanded roster (Docker/API default)",
    )
    args = parser.parse_args()

    if args.compact:
        agents = load_compact_roster()
        ok = validate(
            agents,
            layer_filter=args.layer,
            check_role_soul_uniqueness=False,
        )
    else:
        agents = load_roster()
        ok = validate(
            agents,
            layer_filter=args.layer,
            check_role_soul_uniqueness=True,
        )

    if args.fix_counts and not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
