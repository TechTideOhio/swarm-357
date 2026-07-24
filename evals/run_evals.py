# file: evals/run_evals.py
# description: Swarm 357 evaluation harness with rubric LLM-judge, budget cap, and baselines.
# reference: evals/tasks.yaml, techtide_swarm.llm, techtide_swarm.agent, techtide_swarm.swarm

"""TechTide Swarm 357 — Evaluation Harness.

Runs benchmark tasks against single agents or the full swarm pipeline,
scores via keyword overlap + rubric LLM-as-judge, enforces a spend cap,
and compares against saved baselines.

Usage:
    python evals/run_evals.py --save-baseline
    python evals/run_evals.py --budget 5.0 --save-baseline
    swarm eval --save-baseline
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parent.parent
TASKS_PATH = Path(__file__).resolve().parent / "tasks.yaml"
DEFAULT_BUDGET_USD = 5.0


@dataclass
class EvalTask:
    task_id: str
    description: str
    layer: str
    expected_keywords: list[str]
    min_output_length: int = 50
    mode: str = "single"  # single | swarm
    budget_usd: float = 1.0
    rubric: str = ""


@dataclass
class EvalResult:
    task_id: str
    status: str
    cost_usd: float
    latency_ms: int
    keyword_score: float
    length_ok: bool
    output_preview: str
    mode: str = "single"
    layer: str = ""
    error: str | None = None
    llm_judge_score: float | None = None
    combined_score: float | None = None
    judge_notes: str | None = None
    agent_cost_usd: float = 0.0
    judge_cost_usd: float = 0.0


@dataclass
class BudgetTracker:
    """Hard spend ceiling across agent runs + LLM judge calls."""

    limit_usd: float
    spent_usd: float = 0.0
    events: list[dict[str, Any]] = field(default_factory=list)

    def remaining(self) -> float:
        return max(0.0, self.limit_usd - self.spent_usd)

    def can_afford(self, estimate: float) -> bool:
        return self.remaining() >= max(0.0, estimate)

    def record(self, amount: float, *, kind: str, task_id: str) -> None:
        amt = max(0.0, float(amount))
        self.spent_usd += amt
        self.events.append(
            {
                "kind": kind,
                "task_id": task_id,
                "amount_usd": round(amt, 6),
                "spent_usd": round(self.spent_usd, 6),
            }
        )


def _repo_config_path() -> Path:
    env = os.getenv("SWARM_CONFIG_PATH", "").strip()
    if env:
        return Path(env)
    compact = ROOT / "config" / "swarm-compact.yaml"
    if compact.is_file():
        return compact
    return ROOT / "config" / "swarm.yaml"


def load_tasks(path: Path = TASKS_PATH) -> list[EvalTask]:
    """Load eval tasks from YAML (preferred) or fall back to built-ins."""
    if path.is_file() and yaml is not None:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        tasks: list[EvalTask] = []
        for item in raw.get("tasks", []):
            tasks.append(
                EvalTask(
                    task_id=str(item["id"]),
                    description=str(item["description"]).strip(),
                    layer=str(item.get("layer", "research")),
                    expected_keywords=[str(k) for k in item.get("keywords", [])],
                    min_output_length=int(item.get("min_output_length", 50)),
                    mode=str(item.get("mode", "single")),
                    budget_usd=float(item.get("budget_usd", 1.0)),
                    rubric=str(item.get("rubric", "")).strip(),
                )
            )
        if tasks:
            return tasks
    return _builtin_tasks()


def _builtin_tasks() -> list[EvalTask]:
    """Minimal fallback if tasks.yaml is missing."""
    return [
        EvalTask(
            task_id="eval-001",
            description="Research the AI agent automation market and summarize the top 3 trends for 2026.",
            layer="research",
            expected_keywords=["agent", "automation", "trend"],
            min_output_length=200,
            rubric="Name three trends with brief explanations.",
        ),
        EvalTask(
            task_id="eval-002",
            description="Draft a short outreach email to a CTO about AI-powered customer support automation.",
            layer="sales",
            expected_keywords=["cto", "support", "automation"],
            min_output_length=150,
        ),
    ]


# Back-compat for CLI imports
EVAL_TASKS: list[EvalTask] = load_tasks()


async def maybe_llm_judge(
    task: EvalTask,
    output: str,
    budget: BudgetTracker,
) -> tuple[float | None, float, str | None]:
    """Rubric quality score via OpenRouter/Anthropic. Returns (score, cost, notes)."""
    enabled = os.getenv("SWARM_EVAL_LLM_JUDGE", "1").lower() in ("1", "true", "yes")
    if not enabled:
        return None, 0.0, None
    if not budget.can_afford(0.002):
        return None, 0.0, "judge skipped: budget exhausted"

    try:
        from techtide_swarm.llm import create_async_client, model_id, resolve_api_key

        if not resolve_api_key():
            return None, 0.0, "judge skipped: no API key"

        client = create_async_client()
        model = os.getenv("SWARM_EVAL_JUDGE_MODEL") or model_id("haiku")
        rubric = task.rubric or "Rate overall task completion quality and usefulness."
        msg = await client.messages.create(
            model=model,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "You are a strict eval judge. Score how well OUTPUT meets TASK "
                        "using RUBRIC. Reply JSON only:\n"
                        '{"score": <0.0-1.0>, "notes": "<one short sentence>"}\n\n'
                        f"TASK:\n{task.description[:2500]}\n\n"
                        f"RUBRIC:\n{rubric[:1500]}\n\n"
                        f"OUTPUT:\n{output[:7000]}"
                    ),
                }
            ],
        )
        text = ""
        for block in msg.content:
            if getattr(block, "type", None) == "text":
                text += getattr(block, "text", "")
        judge_cost = _estimate_message_cost(msg, model)
        budget.record(judge_cost, kind="judge", task_id=task.task_id)

        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            return None, judge_cost, "judge parse failed"
        data = json.loads(text[start : end + 1])
        score = max(0.0, min(1.0, float(data.get("score", 0.0))))
        notes = str(data.get("notes", ""))[:240] or None
        return score, judge_cost, notes
    except Exception as exc:  # noqa: BLE001 — judge must not fail the suite
        return None, 0.0, f"judge error: {type(exc).__name__}"


def _estimate_message_cost(message: Any, model_name: str) -> float:
    usage = getattr(message, "usage", None)
    if usage is None:
        return 0.001
    # Prefer OpenRouter-reported cost when present
    reported = getattr(usage, "cost", None)
    if reported is not None:
        try:
            return max(0.0, float(reported))
        except (TypeError, ValueError):
            pass
    inp = float(getattr(usage, "input_tokens", 0) or 0)
    out = float(getattr(usage, "output_tokens", 0) or 0)
    lower = model_name.lower()
    if "opus" in lower:
        rate_in, rate_out = 15.0 / 1e6, 75.0 / 1e6
    elif "sonnet" in lower and "haiku" not in lower:
        rate_in, rate_out = 3.0 / 1e6, 15.0 / 1e6
    else:
        rate_in, rate_out = 0.25 / 1e6, 1.25 / 1e6  # haiku-class / cheap
    return inp * rate_in + out * rate_out


def score_keywords(output: str, expected: list[str]) -> float:
    if not expected:
        return 1.0
    # Coerce both sides — agent output or YAML keywords can be non-str
    lower = str(output or "").lower()
    hits = sum(1 for kw in expected if str(kw).lower() in lower)
    return hits / len(expected)


def load_baseline(baseline_dir: Path) -> dict[str, Any] | None:
    latest = baseline_dir / "latest.json"
    if latest.is_file():
        return json.loads(latest.read_text(encoding="utf-8"))
    return None


def save_baseline(
    baseline_dir: Path,
    results: list[EvalResult],
    *,
    meta: dict[str, Any] | None = None,
) -> Path:
    baseline_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    versioned = baseline_dir / f"baseline_{ts}.json"
    latest = baseline_dir / "latest.json"
    payload = {
        "timestamp": ts,
        "meta": meta or {},
        "results": [asdict(r) for r in results],
    }
    content = json.dumps(payload, indent=2)
    versioned.write_text(content, encoding="utf-8")
    latest.write_text(content, encoding="utf-8")
    return versioned


async def run_eval_task(
    task: EvalTask,
    budget: BudgetTracker,
    *,
    force_mode: str | None = None,
) -> EvalResult:
    """Run a single eval task against an agent or swarm."""
    mode = force_mode or task.mode
    started = time.perf_counter()
    agent_cost = 0.0
    timeout_s = float(os.getenv("SWARM_EVAL_TASK_TIMEOUT_S", "240" if mode == "swarm" else "120"))

    # Reserve a little for the judge
    if mode == "swarm":
        if not budget.can_afford(0.05):
            return EvalResult(
                task_id=task.task_id,
                status="skipped",
                cost_usd=0.0,
                latency_ms=0,
                keyword_score=0.0,
                length_ok=False,
                output_preview="",
                mode=mode,
                layer=task.layer,
                error="skipped: budget exhausted",
            )
    elif not budget.can_afford(0.01):
        return EvalResult(
            task_id=task.task_id,
            status="skipped",
            cost_usd=0.0,
            latency_ms=0,
            keyword_score=0.0,
            length_ok=False,
            output_preview="",
            mode=mode,
            layer=task.layer,
            error="skipped: budget exhausted",
        )

    try:
        output, agent_cost = await asyncio.wait_for(
            _execute_task_body(task, budget, mode=mode),
            timeout=timeout_s,
        )
        budget.record(agent_cost, kind=mode, task_id=task.task_id)
        latency = int((time.perf_counter() - started) * 1000)
        output_text = str(output or "")
        kw_score = score_keywords(output_text, task.expected_keywords)
        length_ok = len(output_text) >= task.min_output_length
        llm_j, judge_cost, notes = await maybe_llm_judge(task, output_text, budget)
        combined = (0.55 * kw_score + 0.45 * llm_j) if llm_j is not None else kw_score
        total = agent_cost + judge_cost

        return EvalResult(
            task_id=task.task_id,
            status="success",
            cost_usd=total,
            latency_ms=latency,
            keyword_score=kw_score,
            length_ok=length_ok,
            output_preview=output_text[:240].replace("\n", " "),
            mode=mode,
            layer=task.layer,
            llm_judge_score=llm_j,
            combined_score=combined,
            judge_notes=notes,
            agent_cost_usd=agent_cost,
            judge_cost_usd=judge_cost,
        )
    except TimeoutError:
        latency = int((time.perf_counter() - started) * 1000)
        return EvalResult(
            task_id=task.task_id,
            status="error",
            cost_usd=agent_cost,
            latency_ms=latency,
            keyword_score=0.0,
            length_ok=False,
            output_preview="",
            mode=mode,
            layer=task.layer,
            error=f"timeout after {timeout_s:.0f}s",
            agent_cost_usd=agent_cost,
        )
    except Exception as e:  # noqa: BLE001 — capture per-task failures
        latency = int((time.perf_counter() - started) * 1000)
        return EvalResult(
            task_id=task.task_id,
            status="error",
            cost_usd=agent_cost,
            latency_ms=latency,
            keyword_score=0.0,
            length_ok=False,
            output_preview="",
            mode=mode,
            layer=task.layer,
            error=str(e)[:500],
            agent_cost_usd=agent_cost,
        )


async def _execute_task_body(
    task: EvalTask,
    budget: BudgetTracker,
    *,
    mode: str,
) -> tuple[str, float]:
    from techtide_swarm import Agent, AgentConfig, Swarm
    from techtide_swarm.core.types import LayerType

    if mode == "swarm":
        swarm = Swarm.from_config(_repo_config_path())
        await swarm.boot()
        run_budget = min(task.budget_usd, max(0.1, budget.remaining() - 0.02))
        res = await swarm.execute(task.description, budget_usd=run_budget)
        return str(res.final_output or ""), float(res.total_cost_usd)

    layer_type = LayerType(task.layer)
    # Platform evals exercise real tools (Read/Write). Writes are sandboxed via
    # SWARM_WRITE_SAFE_ROOT set by the harness entrypoint.
    config = AgentConfig(
        name=f"eval-{task.layer}-001",
        layer=layer_type,
        role="evaluator",
        model="sonnet",
        tools=["Read", "Write"],
        budget_limit_usd=min(1.0, max(0.05, budget.remaining() - 0.01)),
        max_turns=4,
    )
    agent = Agent(config)
    result = await agent.run(task.description)
    return str(result.output or ""), float(result.cost_usd)


def _checkpoint_path() -> Path:
    return ROOT / "evals" / "results" / "checkpoint_live.json"


def _write_checkpoint(results: list[EvalResult], budget: BudgetTracker, limit: float) -> None:
    path = _checkpoint_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "meta": {
            "budget_limit_usd": limit,
            "budget_spent_usd": round(budget.spent_usd, 6),
            "budget_remaining_usd": round(budget.remaining(), 6),
            "task_count": len(results),
            "spend_events": budget.events,
            "model_sonnet": os.getenv("SWARM_MODEL_SONNET", ""),
        },
        "results": [asdict(r) for r in results],
    }
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def _upsert_result(results: list[EvalResult], result: EvalResult) -> None:
    for i, existing in enumerate(results):
        if existing.task_id == result.task_id:
            results[i] = result
            return
    results.append(result)


def _load_checkpoint() -> tuple[list[EvalResult], BudgetTracker, float] | None:
    path = _checkpoint_path()
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data.get("meta", {})
    limit = float(meta.get("budget_limit_usd", DEFAULT_BUDGET_USD))
    budget = BudgetTracker(limit_usd=limit, spent_usd=float(meta.get("budget_spent_usd", 0.0)))
    budget.events = list(meta.get("spend_events", []))
    results = [EvalResult(**r) for r in data.get("results", [])]
    return results, budget, limit


async def run_all_evals(
    save: bool = False,
    use_swarm: bool = False,
    budget_usd: float | None = None,
    repeats: int = 1,
    resume: bool = False,
    swarm_only: bool = False,
) -> list[EvalResult]:
    """Run the catalog under a hard spend cap (default $5)."""
    global EVAL_TASKS
    EVAL_TASKS = load_tasks()

    limit = float(budget_usd if budget_usd is not None else os.getenv("SWARM_EVAL_BUDGET_USD", DEFAULT_BUDGET_USD))
    results: list[EvalResult] = []
    budget = BudgetTracker(limit_usd=limit)
    done_ids: set[str] = set()

    if resume:
        loaded = _load_checkpoint()
        if loaded:
            results, budget, prev_limit = loaded
            if budget_usd is None:
                limit = prev_limit
                budget.limit_usd = prev_limit
            # Keep successes/skips as done; re-run prior errors after harness fixes
            failed_ids = {r.task_id for r in results if r.status == "error"}
            done_ids = {r.task_id for r in results if r.status != "error"}
            print(
                f"Resuming checkpoint: {len(results)} tasks, "
                f"${budget.spent_usd:.4f}/${budget.limit_usd:.2f} spent"
                + (f", re-running {len(failed_ids)} failures" if failed_ids else "")
            )

    singles = [t for t in EVAL_TASKS if t.mode != "swarm"]
    swarms = [t for t in EVAL_TASKS if t.mode == "swarm"]

    # Phase 1 — single-agent suite (optionally repeated for variance)
    if not swarm_only:
        for round_i in range(max(1, repeats)):
            for task in singles:
                if budget.remaining() < 0.02:
                    break
                t = task
                if round_i > 0:
                    t = EvalTask(
                        task_id=f"{task.task_id}-r{round_i + 1}",
                        description=task.description,
                        layer=task.layer,
                        expected_keywords=task.expected_keywords,
                        min_output_length=task.min_output_length,
                        mode="single",
                        budget_usd=task.budget_usd,
                        rubric=task.rubric,
                    )
                if t.task_id in done_ids:
                    continue
                result = await run_eval_task(t, budget, force_mode="single")
                _upsert_result(results, result)
                done_ids.add(t.task_id)
                _print_progress(result, budget)
                _write_checkpoint(results, budget, limit)

    # Phase 2 — swarm pipeline tasks
    swarm_tasks = EVAL_TASKS if use_swarm else swarms
    for task in swarm_tasks:
        if budget.remaining() < 0.08:
            break
        if not use_swarm and task.mode != "swarm":
            continue
        prev = next((r for r in results if r.task_id == task.task_id), None)
        run_task = task
        if prev is not None:
            if prev.status == "success":
                continue
            run_task = EvalTask(
                task_id=f"{task.task_id}-retry",
                description=task.description,
                layer=task.layer,
                expected_keywords=task.expected_keywords,
                min_output_length=task.min_output_length,
                mode="swarm",
                budget_usd=task.budget_usd,
                rubric=task.rubric,
            )
            if run_task.task_id in done_ids:
                continue
        result = await run_eval_task(run_task, budget, force_mode="swarm")
        _upsert_result(results, result)
        done_ids.add(run_task.task_id)
        _print_progress(result, budget)
        _write_checkpoint(results, budget, limit)

    # Phase 3 — burn remaining budget on single-agent repeats (reliable spend)
    # Swarm stress passes often hit wall-clock timeouts on OpenRouter; singles
    # still exercise rubrics + LLM judge and consume the allocated eval budget.
    pass_n = 2
    while budget.remaining() >= 0.03 and singles and pass_n <= 40:
        pending = [
            task
            for task in singles
            if f"{task.task_id}-burn{pass_n}" not in done_ids
        ]
        if not pending:
            # This burn pass already finished in a prior resume — try the next.
            pass_n += 1
            continue
        for task in pending:
            if budget.remaining() < 0.03:
                break
            clone_id = f"{task.task_id}-burn{pass_n}"
            clone = EvalTask(
                task_id=clone_id,
                description=task.description,
                layer=task.layer,
                expected_keywords=[str(k) for k in task.expected_keywords],
                min_output_length=task.min_output_length,
                mode="single",
                budget_usd=min(0.5, budget.remaining() - 0.01),
                rubric=task.rubric,
            )
            result = await run_eval_task(clone, budget, force_mode="single")
            _upsert_result(results, result)
            done_ids.add(clone_id)
            _print_progress(result, budget)
            _write_checkpoint(results, budget, limit)
        pass_n += 1

    out_dir = ROOT / "evals" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    provider = "openrouter" if (
        os.getenv("OPENROUTER_API_KEY")
        or "openrouter" in os.getenv("ANTHROPIC_BASE_URL", "").lower()
    ) else "anthropic"
    meta = {
        "budget_limit_usd": limit,
        "budget_spent_usd": round(budget.spent_usd, 6),
        "budget_remaining_usd": round(budget.remaining(), 6),
        "task_count": len(results),
        "passed": sum(
            1
            for r in results
            if r.status == "success" and (r.combined_score or r.keyword_score) >= 0.5 and r.length_ok
        ),
        "provider": provider,
        "model_sonnet": os.getenv("SWARM_MODEL_SONNET", ""),
        "judge_enabled": os.getenv("SWARM_EVAL_LLM_JUDGE", "1"),
        "spend_events": budget.events,
    }
    payload = {"meta": meta, "results": [asdict(r) for r in results]}
    ts_file = out_dir / f"eval_{ts}.json"
    ts_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    _write_markdown_report(out_dir / f"eval_{ts}.md", results, meta)
    _write_checkpoint(results, budget, limit)

    if save:
        path = save_baseline(ROOT / "evals" / "baselines", results, meta=meta)
        print(f"Baseline saved: {path}")

    print(f"Results written: {ts_file}")
    return results


def _print_progress(result: EvalResult, budget: BudgetTracker) -> None:
    metric = result.combined_score if result.combined_score is not None else result.keyword_score
    flag = "OK" if result.status == "success" and metric >= 0.5 else result.status.upper()[:4]
    print(
        f"  [{flag}] {result.task_id} mode={result.mode} "
        f"kw={result.keyword_score:.2f}"
        f"{'' if result.llm_judge_score is None else f' llm={result.llm_judge_score:.2f}'} "
        f"${result.cost_usd:.4f} | spent ${budget.spent_usd:.4f}/${budget.limit_usd:.2f}",
        flush=True,
    )


def _write_markdown_report(path: Path, results: list[EvalResult], meta: dict[str, Any]) -> None:
    lines = [
        "# Swarm 357 Eval Report",
        "",
        f"- Budget: ${meta.get('budget_spent_usd', 0):.4f} / ${meta.get('budget_limit_usd', 0):.2f}",
        f"- Tasks: {meta.get('task_count', 0)} · Passed: {meta.get('passed', 0)}",
        f"- Provider: {meta.get('provider')} · Model: `{meta.get('model_sonnet') or 'default'}`",
        "",
        "| Task | Mode | Layer | KW | LLM | Combined | Len | Cost | Status |",
        "|---|---|---|---:|---:|---:|---|---:|---|",
    ]
    for r in results:
        llm = f"{r.llm_judge_score:.2f}" if r.llm_judge_score is not None else "—"
        comb = f"{(r.combined_score if r.combined_score is not None else r.keyword_score):.2f}"
        lines.append(
            f"| {r.task_id} | {r.mode} | {r.layer} | {r.keyword_score:.2f} | {llm} | "
            f"{comb} | {'OK' if r.length_ok else 'SHORT'} | ${r.cost_usd:.4f} | {r.status} |"
        )
    fails = [r for r in results if r.status != "success" or (r.combined_score or r.keyword_score) < 0.5]
    if fails:
        lines += ["", "## Failures / weak scores", ""]
        for r in fails:
            lines.append(f"- **{r.task_id}**: {r.error or r.judge_notes or r.output_preview[:120]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written: {path}")


def compare_to_baseline(
    results: list[EvalResult],
    baseline: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compare current results against a baseline; return regressions."""
    baseline_map = {r["task_id"]: r for r in baseline.get("results", [])}
    regressions: list[dict[str, Any]] = []
    for r in results:
        # Compare base ids (strip -rN / -stressN suffixes)
        base_id = re.sub(r"-(r\d+|stress\d+)$", "", r.task_id)
        prev = baseline_map.get(r.task_id) or baseline_map.get(base_id)
        if not prev:
            continue
        prev_score = prev.get("combined_score", prev.get("keyword_score", 0)) or 0
        cur_score = r.combined_score if r.combined_score is not None else r.keyword_score
        if cur_score < float(prev_score) - 0.15:
            regressions.append(
                {
                    "task_id": r.task_id,
                    "metric": "combined_score",
                    "current": cur_score,
                    "baseline": prev_score,
                }
            )
        if prev.get("length_ok") and not r.length_ok:
            regressions.append(
                {
                    "task_id": r.task_id,
                    "metric": "length_ok",
                    "current": r.length_ok,
                    "baseline": prev["length_ok"],
                }
            )
    return regressions


def main() -> None:
    import argparse
    import tempfile

    parser = argparse.ArgumentParser(description="Swarm 357 Eval Harness")
    parser.add_argument("--save-baseline", action="store_true", help="Save results as baseline")
    parser.add_argument("--swarm", action="store_true", help="Force catalog through swarm pipeline")
    parser.add_argument("--compare", action="store_true", help="Compare against saved baseline")
    parser.add_argument("--budget", type=float, default=None, help="Hard spend cap USD (default 5.0)")
    parser.add_argument("--repeats", type=int, default=1, help="Repeat single-agent suite N times")
    parser.add_argument("--resume", action="store_true", help="Resume from evals/results/checkpoint_live.json")
    parser.add_argument("--swarm-only", action="store_true", help="Skip single-agent phase")
    args = parser.parse_args()

    # Enable judge by default for proper evals
    os.environ.setdefault("SWARM_EVAL_LLM_JUDGE", "1")
    # Sandbox Write tool during evals (platform-safe demo path)
    if not os.getenv("SWARM_WRITE_SAFE_ROOT"):
        safe = Path(tempfile.mkdtemp(prefix="swarm357-eval-writes-"))
        os.environ["SWARM_WRITE_SAFE_ROOT"] = str(safe)
        print(f"SWARM_WRITE_SAFE_ROOT={safe}")
    # Tools ON for platform fidelity (unset any prior disable flag)
    os.environ.pop("SWARM_EVAL_DISABLE_TOOLS", None)

    results = asyncio.run(
        run_all_evals(
            save=args.save_baseline,
            use_swarm=args.swarm,
            budget_usd=args.budget,
            repeats=args.repeats,
            resume=args.resume,
            swarm_only=args.swarm_only,
        )
    )

    total_cost = sum(r.cost_usd for r in results)
    successes = sum(1 for r in results if r.status == "success")
    passed = sum(
        1
        for r in results
        if r.status == "success" and (r.combined_score or r.keyword_score) >= 0.5 and r.length_ok
    )
    use_llm = any(r.llm_judge_score is not None for r in results)
    scored = [r for r in results if r.status == "success"]
    avg_metric = (
        sum((r.combined_score or r.keyword_score) for r in scored) / len(scored) if scored else 0.0
    )

    print("\n--- Eval Summary ---")
    print(
        f"Tasks: {len(results)} | Success: {successes} | Passed gates: {passed} | "
        f"Avg {'combined' if use_llm else 'keyword'} score: {avg_metric:.2f}"
    )
    print(f"Total cost: ${total_cost:.4f}")

    for r in results:
        metric = r.combined_score if r.combined_score is not None else r.keyword_score
        status = "OK" if r.status == "success" and metric >= 0.5 and r.length_ok else "WARN"
        llm_part = f" llm={r.llm_judge_score:.2f}" if r.llm_judge_score is not None else ""
        print(
            f"  [{status}] {r.task_id}: kw={r.keyword_score:.2f}{llm_part} "
            f"score={metric:.2f} len_ok={r.length_ok} ${r.cost_usd:.4f} {r.latency_ms}ms"
        )

    if args.compare:
        baseline = load_baseline(ROOT / "evals" / "baselines")
        if baseline:
            regressions = compare_to_baseline(results, baseline)
            if regressions:
                print(f"\nREGRESSIONS ({len(regressions)}):")
                for reg in regressions:
                    print(
                        f"  {reg['task_id']}: {reg['metric']} {reg['baseline']} -> {reg['current']}"
                    )
            else:
                print("\nNo regressions found.")
        else:
            print("\nNo baseline found. Run with --save-baseline first.")


if __name__ == "__main__":
    main()
