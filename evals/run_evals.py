"""TechTide Swarm 357 — Evaluation Harness.

Runs benchmark tasks against single agents or the full swarm pipeline,
scores results via keyword overlap + optional LLM-as-judge, and
compares against saved baselines.

Usage:
    swarm eval                       # run all eval tasks
    swarm eval --save-baseline       # save results as new baseline
    python -m evals.run_evals        # direct execution
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class EvalTask:
    task_id: str
    description: str
    layer: str
    expected_keywords: list[str]
    min_output_length: int = 50


@dataclass
class EvalResult:
    task_id: str
    status: str
    cost_usd: float
    latency_ms: int
    keyword_score: float
    length_ok: bool
    output_preview: str
    error: str | None = None


EVAL_TASKS: list[EvalTask] = [
    EvalTask(
        task_id="eval-001",
        description="Research the AI agent automation market and summarize the top 3 trends for 2026.",
        layer="research",
        expected_keywords=["agent", "automation", "trend"],
    ),
    EvalTask(
        task_id="eval-002",
        description="Draft a short outreach email to a CTO about AI-powered customer support automation.",
        layer="sales",
        expected_keywords=["cto", "support", "automation", "email"],
    ),
    EvalTask(
        task_id="eval-003",
        description="List 5 high-intent SEO keywords for an AI agent orchestration platform targeting enterprise buyers.",
        layer="seo",
        expected_keywords=["keyword", "enterprise", "agent"],
    ),
    EvalTask(
        task_id="eval-004",
        description="Create an FAQ entry: 'How does Swarm 357 handle cost controls across agent layers?'",
        layer="support",
        expected_keywords=["cost", "budget", "layer"],
    ),
    EvalTask(
        task_id="eval-005",
        description="Write a 3-paragraph blog post introduction about the benefits of layered agent architectures for business automation.",
        layer="marketing",
        expected_keywords=["layer", "agent", "business", "automation"],
    ),
]


def score_keywords(output: str, expected: list[str]) -> float:
    if not expected:
        return 1.0
    lower = output.lower()
    hits = sum(1 for kw in expected if kw.lower() in lower)
    return hits / len(expected)


def load_baseline(baseline_dir: Path) -> dict[str, Any] | None:
    latest = baseline_dir / "latest.json"
    if latest.is_file():
        return json.loads(latest.read_text(encoding="utf-8"))
    return None


def save_baseline(baseline_dir: Path, results: list[EvalResult]) -> Path:
    baseline_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    versioned = baseline_dir / f"baseline_{ts}.json"
    latest = baseline_dir / "latest.json"
    payload = {
        "timestamp": ts,
        "results": [asdict(r) for r in results],
    }
    content = json.dumps(payload, indent=2)
    versioned.write_text(content, encoding="utf-8")
    latest.write_text(content, encoding="utf-8")
    return versioned


async def run_eval_task(task: EvalTask, use_swarm: bool = False) -> EvalResult:
    """Run a single eval task against an agent or swarm."""
    from techtide_swarm import Agent, AgentConfig, Swarm
    from techtide_swarm.core.types import LayerType

    started = time.perf_counter()
    try:
        if use_swarm:
            swarm = Swarm.from_config(Path("config/swarm.yaml"))
            await swarm.boot()
            res = await swarm.execute(task.description, budget_usd=5.0)
            output = res.final_output
            cost = res.total_cost_usd
        else:
            layer_type = LayerType(task.layer)
            config = AgentConfig(
                name=f"eval-{task.layer}-001",
                layer=layer_type,
                role="evaluator",
                model="sonnet",
                budget_limit_usd=1.0,
                max_turns=5,
            )
            agent = Agent(config)
            result = await agent.run(task.description)
            output = result.output
            cost = result.cost_usd

        latency = int((time.perf_counter() - started) * 1000)
        kw_score = score_keywords(output, task.expected_keywords)
        length_ok = len(output) >= task.min_output_length

        return EvalResult(
            task_id=task.task_id,
            status="success",
            cost_usd=cost,
            latency_ms=latency,
            keyword_score=kw_score,
            length_ok=length_ok,
            output_preview=output[:200].replace("\n", " "),
        )
    except Exception as e:
        latency = int((time.perf_counter() - started) * 1000)
        return EvalResult(
            task_id=task.task_id,
            status="error",
            cost_usd=0.0,
            latency_ms=latency,
            keyword_score=0.0,
            length_ok=False,
            output_preview="",
            error=str(e),
        )


async def run_all_evals(
    save: bool = False,
    use_swarm: bool = False,
) -> list[EvalResult]:
    results: list[EvalResult] = []
    for task in EVAL_TASKS:
        result = await run_eval_task(task, use_swarm=use_swarm)
        results.append(result)

    out_dir = Path("evals/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts_file = out_dir / f"eval_{int(time.time())}.json"
    ts_file.write_text(
        json.dumps([asdict(r) for r in results], indent=2),
        encoding="utf-8",
    )

    if save:
        baseline_dir = Path("evals/baselines")
        path = save_baseline(baseline_dir, results)
        print(f"Baseline saved: {path}")

    return results


def compare_to_baseline(
    results: list[EvalResult],
    baseline: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compare current results against a baseline; return regressions."""
    baseline_map = {r["task_id"]: r for r in baseline.get("results", [])}
    regressions: list[dict[str, Any]] = []
    for r in results:
        prev = baseline_map.get(r.task_id)
        if not prev:
            continue
        if r.keyword_score < prev.get("keyword_score", 0) - 0.1:
            regressions.append({
                "task_id": r.task_id,
                "metric": "keyword_score",
                "current": r.keyword_score,
                "baseline": prev["keyword_score"],
            })
        if prev.get("length_ok") and not r.length_ok:
            regressions.append({
                "task_id": r.task_id,
                "metric": "length_ok",
                "current": r.length_ok,
                "baseline": prev["length_ok"],
            })
    return regressions


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Swarm 357 Eval Harness")
    parser.add_argument("--save-baseline", action="store_true", help="Save results as baseline")
    parser.add_argument("--swarm", action="store_true", help="Run through full swarm pipeline")
    parser.add_argument("--compare", action="store_true", help="Compare against saved baseline")
    args = parser.parse_args()

    results = asyncio.run(run_all_evals(save=args.save_baseline, use_swarm=args.swarm))

    total_cost = sum(r.cost_usd for r in results)
    avg_kw = sum(r.keyword_score for r in results) / len(results) if results else 0
    successes = sum(1 for r in results if r.status == "success")

    print(f"\n--- Eval Summary ---")
    print(f"Tasks: {len(results)} | Passed: {successes} | Avg keyword score: {avg_kw:.2f}")
    print(f"Total cost: ${total_cost:.4f}")

    for r in results:
        status = "OK" if r.status == "success" and r.keyword_score >= 0.5 else "WARN"
        print(f"  [{status}] {r.task_id}: kw={r.keyword_score:.2f} len_ok={r.length_ok} ${r.cost_usd:.4f} {r.latency_ms}ms")

    if args.compare:
        baseline = load_baseline(Path("evals/baselines"))
        if baseline:
            regressions = compare_to_baseline(results, baseline)
            if regressions:
                print(f"\nREGRESSIONS ({len(regressions)}):")
                for reg in regressions:
                    print(f"  {reg['task_id']}: {reg['metric']} {reg['baseline']} -> {reg['current']}")
            else:
                print("\nNo regressions found.")
        else:
            print("\nNo baseline found. Run with --save-baseline first.")


if __name__ == "__main__":
    main()
