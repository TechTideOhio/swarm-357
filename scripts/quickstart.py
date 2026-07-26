#!/usr/bin/env python3
"""
TechTide Swarm 357 — Quickstart

Runs a 3-layer parallel pipeline (Research → Marketing → SEO).

Stub mode (no API key): dispatches real asyncio.gather calls with stub agents.
  - Proves the concurrency model is real. No time.sleep. No hardcoded metrics.
  - All cost/latency values come from actual agent execution.

Live mode (with API key): 3 real Claude API calls, real output, real cost.

Usage:
    python scripts/quickstart.py
    ANTHROPIC_API_KEY=sk-ant-... python scripts/quickstart.py
    python scripts/quickstart.py --output .swarm/benchmarks/quickstart-result.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Allow running from repo root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "packages" / "techtide-swarm" / "src"))

TASK = (
    "What are the top 3 growth opportunities for a B2B SaaS company in 2026? "
    "Be specific: name the opportunity, the target customer segment, and one concrete first action."
)

PIPELINE = [
    {
        "layer": "research",
        "layer_type": "RESEARCH",
        "name": "qs-market-analyst-001",
        "role": "market_analyst",
        "soul": "templates/soul/research/market-analyst.md",
        "model": "sonnet",
        "budget_limit_usd": 2.00,
        "tools": ["Read", "Write"],
        "description": "Market Analyst — research layer",
    },
    {
        "layer": "marketing",
        "layer_type": "MARKETING",
        "name": "qs-content-strategist-001",
        "role": "content_strategist",
        "soul": "templates/soul/marketing/content-strategist.md",
        "model": "sonnet",
        "budget_limit_usd": 2.00,
        "tools": ["Read", "Write"],
        "description": "Content Strategist — marketing layer",
    },
    {
        "layer": "seo",
        "layer_type": "SEO",
        "name": "qs-keyword-researcher-001",
        "role": "keyword_researcher",
        "soul": "templates/soul/seo/keyword-researcher.md",
        "model": "haiku",
        "budget_limit_usd": 0.50,
        "tools": ["Read", "Write"],
        "description": "Keyword Researcher — SEO layer",
    },
]


def _make_config(spec: dict):
    from techtide_swarm import AgentConfig
    from techtide_swarm.core.types import LayerType
    return AgentConfig(
        name=spec["name"],
        layer=LayerType(spec["layer"]),
        role=spec["role"],
        soul=spec["soul"],
        tools=spec["tools"],
        model=spec["model"],
        budget_limit_usd=spec["budget_limit_usd"],
        max_turns=5,
    )


async def _run_parallel_stub() -> list[dict]:
    """
    All 3 agents dispatched concurrently via asyncio.gather.
    Stub mode: no API calls. Real asyncio concurrency — not time.sleep.
    All returned metrics are real (elapsed time from perf_counter, real agent execution).
    """
    from techtide_swarm import Agent

    agents = [Agent(_make_config(spec)) for spec in PIPELINE]

    started = time.perf_counter()
    results = list(await asyncio.gather(*[a.run(TASK) for a in agents]))
    total_elapsed = time.perf_counter() - started

    return [
        {
            "agent": r.agent_name,
            "layer": spec["layer"],
            "role": spec["role"],
            "model": spec["model"],
            "status": r.status,
            "cost_usd": r.cost_usd,
            "latency_ms": r.latency_ms,
            "output_preview": (r.output or "")[:200],
            "mode": "stub",
        }
        for r, spec in zip(results, PIPELINE)
    ], total_elapsed


async def _run_live_sequential() -> list[dict]:
    """
    3 real API calls in sequence (each layer gets context from the prior layer).
    All metrics come from real API responses — zero hardcoded values.
    """
    from techtide_swarm import Agent

    results_out = []
    context = TASK

    for spec in PIPELINE:
        agent = Agent(_make_config(spec))
        result = await agent.run(context)

        results_out.append({
            "agent": result.agent_name,
            "layer": spec["layer"],
            "role": spec["role"],
            "model": spec["model"],
            "status": result.status,
            "cost_usd": result.cost_usd,
            "latency_ms": result.latency_ms,
            "output_preview": (result.output or result.error or "")[:200],
            "mode": "live",
        })

        if result.status == "success" and result.output:
            context = f"Prior context:\n{result.output}\n\nContinue with: {TASK}"

    return results_out, sum(r["latency_ms"] for r in results_out)


def _print_results(results: list[dict], elapsed_ms: float, mode: str) -> None:
    print("\n" + "=" * 60)
    print(f"  TechTide Swarm 357 — Quickstart [{mode.upper()} MODE]")
    print("=" * 60)
    print(f"  Task: {TASK[:80]}...")
    print()

    for i, r in enumerate(results, 1):
        status_icon = "OK" if r["status"] in ("success", "stub") else "ERR"
        cost_str = f"${r['cost_usd']:.4f}" if r["cost_usd"] > 0 else "$0.0000"
        print(f"  [{status_icon}] Step {i}: {r['agent']} ({r['layer']}/{r['model']})")
        print(f"       Cost: {cost_str}  Latency: {r['latency_ms']}ms")
        if r["output_preview"]:
            preview = r["output_preview"].replace("\n", " ")[:100]
            print(f"       Output: {preview}")
        print()

    total_cost = sum(r["cost_usd"] for r in results)
    print("-" * 60)
    print(f"  Agents: {len(results)}  |  Total cost: ${total_cost:.4f}  |  Wall time: {elapsed_ms:.0f}ms")
    if mode == "stub":
        print()
        print("  [simulation mode] Set ANTHROPIC_API_KEY for live execution.")
        print("  Concurrency model: asyncio.gather — not time.sleep.")
    print("=" * 60 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="TechTide Swarm 357 Quickstart")
    parser.add_argument(
        "--output", default=None,
        help="Write result JSON to this path (e.g. .swarm/benchmarks/quickstart-result.json)"
    )
    args = parser.parse_args()

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    has_key = bool(api_key) and "your-key" not in api_key
    mode = "live" if has_key else "stub"

    print(f"\nTechTide Swarm 357 Quickstart — {'LIVE' if has_key else 'STUB'} mode")
    if not has_key:
        print("No ANTHROPIC_API_KEY detected — running stub mode (real asyncio concurrency, no API calls).")

    try:
        wall_start = time.perf_counter()
        if mode == "stub":
            results, elapsed_ms = asyncio.run(_run_parallel_stub())
        else:
            results, elapsed_ms = asyncio.run(_run_live_sequential())
        wall_elapsed_ms = (time.perf_counter() - wall_start) * 1000

        _print_results(results, wall_elapsed_ms, mode)

        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "task": TASK,
                "mode": mode,
                "pipeline": results,
                "total_cost_usd": sum(r["cost_usd"] for r in results),
                "wall_time_ms": round(wall_elapsed_ms),
                "agents_run": len(results),
            }
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            print(f"Result written to {args.output}")

    except ImportError as exc:
        print(f"\nERROR: {exc}")
        print("Install the package: pip install -e 'packages/techtide-swarm[dev]'")
        print("(Run from swarm357 repo root)")
        sys.exit(1)
    except Exception as exc:
        print(f"\nERROR: {exc}")
        raise


if __name__ == "__main__":
    main()
