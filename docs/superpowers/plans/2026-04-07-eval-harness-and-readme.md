# Eval Harness + Viral README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a publishable LLM-as-judge eval harness with 20 YAML tasks across 7 layers, save a real baseline, then rewrite README.md using viral patterns from Cline/CrewAI/LangGraph/Mastra — under 300 lines, every claim verifiable by running a command.

**Architecture:** Eval tasks live as YAML files in `evals/tasks/`. `evals/judge.py` scores rubric dimensions via a Haiku API call with rule-based fallback when no key is present. `evals/runner.py` orchestrates all tasks, calls the judge, and writes `evals/baselines/v0.1.0.json` + a Markdown report. The CLI `swarm eval` command gets `--tasks <layer>`, `--save-baseline`, and `--compare` flags. A CI workflow runs 2 stub tasks on every PR. The README is rewritten last, after real benchmark numbers exist.

**Tech Stack:** Python 3.10+, PyYAML, anthropic SDK (already dep), pytest-asyncio, GitHub Actions YAML, Mermaid diagrams in Markdown.

---

## File Map

| Status | Path | Responsibility |
|--------|------|----------------|
| Create | `evals/tasks/*.yaml` (20 files) | One task per file — id, layer, task prompt, rubric |
| Create | `evals/judge.py` | `score_rubric(output, rubric)` — Haiku call + rule-based fallback |
| Create | `evals/runner.py` | Load tasks, run agents, call judge, emit JSON + Markdown |
| Modify | `packages/techtide-swarm/src/techtide_swarm/cli.py` | Extend `cmd_eval()` with --tasks, --save-baseline, --compare |
| Create | `evals/baselines/v0.1.0.json` | Baseline produced by `swarm eval --save-baseline` |
| Create | `.github/workflows/smoke-eval.yml` | CI: 2-task stub eval on every PR |
| Modify | `README.md` | Rewrite to viral structure, <300 lines, benchmark table |
| Create | `LICENSE` | Apache-2.0 text (currently missing from repo) |

Existing `evals/run_evals.py` is NOT modified.

---

## Task 1: 20 YAML Eval Task Files

**Files:** Create `evals/tasks/` (20 `.yaml` files)

```yaml
# Schema (every task file follows this exactly)
id: eval-research-001
layer: research
task: "Research the global AI agent market size for 2026..."
expected_output_format: structured_briefing
min_output_length: 150
rubric:
  - name: factual_accuracy
    weight: 0.30
    criteria: "Contains at least one specific dollar figure or percentage"
  - name: structure
    weight: 0.20
    criteria: "Output has at least 2 clearly labeled sections or numbered points"
  - name: completeness
    weight: 0.30
    criteria: "Addresses all 3 requested items: market size, growth drivers, vendors"
  - name: relevance
    weight: 0.20
    criteria: "Output is about AI agents specifically, not general AI"
```

- [ ] **Step 1: Create `evals/tasks/` and all 20 YAML files**

```bash
mkdir -p evals/tasks
```

Create these 20 files. Full YAML content for each:

**research layer (3 files):**

`evals/tasks/eval-research-001.yaml` u2014 global AI agent market size 2026, structured briefing, rubric: factual_accuracy(0.30)/structure(0.20)/completeness(0.30)/relevance(0.20)

`evals/tasks/eval-research-002.yaml` u2014 top 5 open-source agent frameworks by GitHub stars 2025, ranked list format, rubric: factual_accuracy(0.35)/structure(0.25)/completeness(0.25)/recency(0.15)

`evals/tasks/eval-research-003.yaml` u2014 competitive landscape for AI-powered BPA 2026, 5 competitors, competitive_analysis format, rubric: factual_accuracy(0.30)/structure(0.20)/completeness(0.30)/depth(0.20)

**sales layer (3 files):**

`evals/tasks/eval-sales-001.yaml` u2014 cold outreach email to CTO at 500-person B2B SaaS, email format, rubric: structure(0.30)/personalization(0.25)/clarity(0.25)/cta(0.20)

`evals/tasks/eval-sales-002.yaml` u2014 5-question discovery call script for VP Operations, numbered_questions format, rubric: structure(0.25)/relevance(0.35)/qualification(0.25)/open_ended(0.15)

`evals/tasks/eval-sales-003.yaml` u2014 3-slide pitch deck outline for Series B startup, slide_outline format, rubric: structure(0.35)/relevance(0.30)/specificity(0.20)/audience_fit(0.15)

**marketing layer (3 files):**

`evals/tasks/eval-marketing-001.yaml` u2014 3-paragraph blog intro under 200 words, blog_intro format, rubric: tone(0.30)/structure(0.25)/hook(0.25)/relevance(0.20)

`evals/tasks/eval-marketing-002.yaml` u2014 5 Twitter/X post variants for launch, social_posts format, rubric: variety(0.30)/length(0.20)/engagement(0.30)/product_mention(0.20)

`evals/tasks/eval-marketing-003.yaml` u2014 product positioning statement using For/Who/Is/That/Unlike template, positioning_statement format, rubric: format_compliance(0.40)/specificity(0.30)/differentiation(0.30)

**seo layer (2 files):**

`evals/tasks/eval-seo-001.yaml` u2014 10 high-intent keywords for enterprise AI agent platform as table, keyword_table format, rubric: quantity(0.25)/intent_classification(0.25)/enterprise_relevance(0.30)/format(0.20)

`evals/tasks/eval-seo-002.yaml` u2014 meta description + title tag under character limits, meta_tags format, rubric: length_compliance(0.40)/keyword_inclusion(0.30)/cta_presence(0.30)

**support layer (3 files):**

`evals/tasks/eval-support-001.yaml` u2014 FAQ entry on cost controls, faq_entry format, rubric: accuracy(0.35)/clarity(0.35)/completeness(0.30)

`evals/tasks/eval-support-002.yaml` u2014 Tier 1 support response for ImportError, support_response format, rubric: diagnosis(0.30)/actionable_steps(0.35)/escalation(0.20)/tone(0.15)

`evals/tasks/eval-support-003.yaml` u2014 CSAT survey 5 questions after first swarm run, survey format, rubric: quantity(0.25)/variety(0.30)/relevance(0.30)/structure(0.15)

**operations layer (2 files):**

`evals/tasks/eval-operations-001.yaml` u2014 project kickoff checklist for 50-person company, checklist format, rubric: completeness(0.35)/structure(0.25)/actionability(0.25)/specificity(0.15)

`evals/tasks/eval-operations-002.yaml` u2014 runbook entry for zero successful runs alert, runbook format, rubric: structure(0.30)/actionability(0.35)/escalation(0.20)/rollback(0.15)

**management layer (3 files):**

`evals/tasks/eval-management-001.yaml` u2014 Conductor routing plan for LinkedIn campaign to CTOs, routing_plan format, rubric: layer_identification(0.35)/sequencing(0.25)/deliverables(0.30)/coherence(0.10)

`evals/tasks/eval-management-002.yaml` u2014 Cost Controller decision at $18.50/$20.00 budget, cost_decision format, rubric: decision_quality(0.35)/prioritization(0.30)/completeness(0.25)/specificity(0.10)

`evals/tasks/eval-management-003.yaml` u2014 5-item daily digest for human operator, digest format, rubric: structure(0.30)/completeness(0.35)/actionability(0.25)/brevity(0.10)

For each file the full YAML content follows this template exactly (using the description above to fill `task` and `rubric` fields):

```yaml
id: eval-<layer>-00N
layer: <layer>
task: "<full task prompt>"
expected_output_format: <format>
min_output_length: <integer>
rubric:
  - name: <dimension>
    weight: <float>
    criteria: "<plain-English criteria>"
```

- [ ] **Step 2: Verify 20 files exist**

```bash
ls evals/tasks/*.yaml | wc -l
```
Expected: `20`

- [ ] **Step 3: Commit**

```bash
git add evals/tasks/
git commit -m "feat(evals): add 20 YAML task files across 7 layers"
```

---

## Task 2: `evals/judge.py` u2014 LLM-as-Judge Scorer

**Files:**
- Create: `evals/judge.py`
- Create: `packages/techtide-swarm/tests/test_judge.py`

Scores rubric dimensions 0u20131 via Haiku when `ANTHROPIC_API_KEY` is set; rule-based fallback otherwise.

- [ ] **Step 1: Write failing tests at `packages/techtide-swarm/tests/test_judge.py`**

```python
"""Tests for evals/judge.py."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "evals"))
from judge import DimensionScore, RubricDimension, score_rubric_rule_based, aggregate_score


def _dim(name: str, weight: float, criteria: str) -> RubricDimension:
    return RubricDimension(name=name, weight=weight, criteria=criteria)


def test_dimension_score_fields() -> None:
    ds = DimensionScore(name="structure", score=0.8, weight=0.3, reasoning="has sections")
    assert ds.name == "structure"
    assert ds.score == 0.8


def test_rule_based_keyword_hit() -> None:
    dim = _dim("structure", 0.5, "Output has at least 2 clearly labeled sections")
    output = "Section 1: intro\nSection 2: analysis\nSection 3: conclusion"
    scores = score_rubric_rule_based(output, [dim])
    assert scores[0].score >= 0.5


def test_rule_based_keyword_miss() -> None:
    dim = _dim("numbers", 0.5, "Contains at least one specific dollar figure")
    output = "The market is big and growing fast."
    scores = score_rubric_rule_based(output, [dim])
    assert scores[0].score == 0.0


def test_rule_based_multiple_dimensions() -> None:
    dims = [
        _dim("structure", 0.3, "Has numbered points"),
        _dim("accuracy", 0.4, "Contains dollar figures or percentages"),
        _dim("cta", 0.3, "Ends with a call to action"),
    ]
    output = "1. Point one\n2. Point two\nMarket is $5B.\nSchedule a demo today."
    scores = score_rubric_rule_based(output, dims)
    assert len(scores) == 3
    assert all(0.0 <= s.score <= 1.0 for s in scores)


def test_aggregate_score() -> None:
    scores = [
        DimensionScore(name="a", score=1.0, weight=0.5, reasoning="good"),
        DimensionScore(name="b", score=0.5, weight=0.5, reasoning="ok"),
    ]
    total = aggregate_score(scores)
    assert total == pytest.approx(0.75)
```

- [ ] **Step 2: Run tests u2014 expect FAIL (ModuleNotFoundError)**

```bash
cd packages/techtide-swarm && python -m pytest tests/test_judge.py -v
```
Expected: `ModuleNotFoundError: No module named 'judge'`

- [ ] **Step 3: Create `evals/judge.py`**

```python
"""LLM-as-judge scorer for Swarm 357 eval tasks.

Live mode (ANTHROPIC_API_KEY set): calls claude-haiku-4-5-20251001.
Stub/CI mode: rule-based fallback using keyword + regex heuristics.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass


@dataclass
class RubricDimension:
    name: str
    weight: float
    criteria: str


@dataclass
class DimensionScore:
    name: str
    score: float
    weight: float
    reasoning: str


_NUMERIC_PATTERN = re.compile(r"\$[\d,.]+|\d+%|\d+\.\d+")
_CTA_WORDS = {"schedule", "book", "demo", "call", "reply", "contact", "start", "try", "sign"}
_STRUCTURE_WORDS = {"section", "point", "step", "item", "entry"}


def _keyword_hit(text: str, criteria: str) -> float:
    lower_text = text.lower()
    lower_criteria = criteria.lower()

    if any(w in lower_criteria for w in ("dollar", "figure", "percentage", "number", "metric", "stat")):
        return 1.0 if _NUMERIC_PATTERN.search(text) else 0.0

    if any(w in lower_criteria for w in ("call to action", "cta", "action")):
        words = set(lower_text.split())
        return 1.0 if _CTA_WORDS & words else 0.0

    if any(w in lower_criteria for w in ("section", "list", "numbered", "structured", "table", "format")):
        has_structure = (
            bool(re.search(r"^\d+\.", lower_text, re.MULTILINE))
            or bool(re.search(r"^[-*]", lower_text, re.MULTILINE))
            or bool(re.search(r"\|.*\|", lower_text))
            or any(w in lower_text for w in _STRUCTURE_WORDS)
        )
        return 1.0 if has_structure else 0.0

    criteria_words = [
        w for w in re.findall(r"[a-z]{4,}", lower_criteria)
        if w not in {"that", "with", "have", "from", "this", "each", "least", "more", "than", "about"}
    ]
    if not criteria_words:
        return min(1.0, len(text) / 200)

    hits = sum(1 for w in criteria_words if w in lower_text)
    return hits / len(criteria_words)


def score_rubric_rule_based(
    output: str,
    rubric: list[RubricDimension],
) -> list[DimensionScore]:
    """Score rubric dimensions using heuristics only. No API calls."""
    results: list[DimensionScore] = []
    for dim in rubric:
        score = _keyword_hit(output, dim.criteria)
        results.append(DimensionScore(
            name=dim.name,
            score=round(score, 3),
            weight=dim.weight,
            reasoning=f"[rule-based] score={score:.2f} for '{dim.name}'",
        ))
    return results


_JUDGE_SYSTEM = (
    "You are an expert evaluator for AI agent outputs.\n"
    "Given a rubric dimension and agent output, respond with JSON only: "
    '{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}\n'
    "Be strict. 1.0 = fully meets criteria. 0.5 = partially met."
)


def _score_dimension_llm(output: str, dim: RubricDimension) -> DimensionScore:
    """Score one dimension with a Haiku API call."""
    import json
    import anthropic

    client = anthropic.Anthropic()
    model = os.getenv("SWARM_MODEL_HAIKU", "claude-haiku-4-5-20251001")
    user_msg = (
        f"Rubric dimension: {dim.name}\nCriteria: {dim.criteria}\n\n"
        f"Agent output (first 2000 chars):\n---\n{output[:2000]}\n---\n\n"
        'Respond with JSON only: {"score": <0.0-1.0>, "reasoning": "<one sentence>"}'
    )
    resp = client.messages.create(
        model=model,
        max_tokens=150,
        system=_JUDGE_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = resp.content[0].text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    parsed = json.loads(text)
    return DimensionScore(
        name=dim.name,
        score=round(float(parsed["score"]), 3),
        weight=dim.weight,
        reasoning=parsed.get("reasoning", ""),
    )


def score_rubric(
    output: str,
    rubric: list[RubricDimension],
    *,
    force_rule_based: bool = False,
) -> list[DimensionScore]:
    """Score all rubric dimensions. Uses Haiku when API key is present."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    use_llm = bool(api_key) and not force_rule_based
    if not use_llm:
        return score_rubric_rule_based(output, rubric)
    results: list[DimensionScore] = []
    for dim in rubric:
        try:
            results.append(_score_dimension_llm(output, dim))
        except Exception as exc:
            fallback = score_rubric_rule_based(output, [dim])[0]
            fallback.reasoning = f"[llm-fallback: {exc}] " + fallback.reasoning
            results.append(fallback)
    return results


def aggregate_score(scores: list[DimensionScore]) -> float:
    """Weighted average of dimension scores."""
    if not scores:
        return 0.0
    total_weight = sum(s.weight for s in scores)
    if total_weight == 0:
        return 0.0
    return sum(s.score * s.weight for s in scores) / total_weight
```

- [ ] **Step 4: Run tests u2014 expect PASS**

```bash
cd packages/techtide-swarm && python -m pytest tests/test_judge.py -v
```
Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add evals/judge.py packages/techtide-swarm/tests/test_judge.py
git commit -m "feat(evals): add judge.py LLM-as-judge with rule-based fallback"
```


---

## Task 3: evals/runner.py - Orchestrator

Dataclasses: RubricDimSpec, EvalTaskSpec, TaskResult (same fields as in Task 2 tests).
Functions: load_tasks, filter_tasks, build_markdown_report, run_all, save_results, save_baseline, load_baseline, compare_to_baseline, main.

- [ ] Step 1: Write tests/test_runner.py (5 tests: load returns 20, fields valid, filter by layer, filter None=all, report has table)
- [ ] Step 2: Run - expect ModuleNotFoundError: runner
- [ ] Step 3: Implement evals/runner.py with all functions. _run_task converts RubricDimSpec->RubricDimension for score_rubric(). Stub mode: pop API key, model=haiku, force_rule_based=True.
- [ ] Step 4: Run - expect 5 passed

---

## Task 4: Wire swarm eval CLI

**File:** packages/techtide-swarm/src/techtide_swarm/cli.py

- [ ] Step 1: grep -n cmd_eval to find its location
- [ ] Step 2: Add missing flags to eval subparser: --tasks (default empty), --save-baseline (store_true), --compare (store_true), --stub (store_true), --version (default v0.1.0)
- [ ] Step 3: Replace cmd_eval() body to call runner module (import from evals.runner, resolve evals_dir, asyncio.run, save results, handle baseline/compare flags)
- [ ] Step 4: swarm eval --stub --tasks research --version smoke-test -> 3 tasks, no crash
- [ ] Step 5: python -m pytest tests/ -v --timeout=30 -> all pass

---

## Task 5: Run Live Eval and Save Baseline

Prerequisite: ANTHROPIC_API_KEY set.

- [ ] Step 1: echo  | head -c 20 -> sk-ant-...
- [ ] Step 2: swarm eval --save-baseline --version v0.1.0 -> 20 tasks, baseline written
- [ ] Step 3: head -40 evals/results/run_*.md -> 20 rows with real scores

---

## Task 6: CI Smoke Eval

**File:** .github/workflows/smoke-eval.yml

Trigger: pull_request on paths evals/**, packages/techtide-swarm/src/**, .github/workflows/smoke-eval.yml
Steps: checkout, setup-python 3.11, pip install packages/techtide-swarm[dev] pyyaml, run python -m evals.runner --tasks research,sales --stub, assert no errors via evals/check_results.py.

- [ ] Step 1: Create .github/workflows/smoke-eval.yml with above structure
- [ ] Step 2: Create evals/check_results.py (reads latest run JSON, sys.exit(1) if any status==error)
- [ ] Step 3: python -m evals.runner --tasks research,sales --stub -> 5 tasks all success

---

## Task 7: Apache-2.0 LICENSE

- [ ] curl -s https://www.apache.org/licenses/LICENSE-2.0.txt > LICENSE && echo Copyright 2026 TechTide AI >> LICENSE

---

## Task 8: Rewrite README.md

Prerequisite: Task 5 complete.

- [ ] Step 1: Create evals/extract_numbers.py to read v0.1.0.json and print per-layer averages. Run it and record output.
- [ ] Step 2: Write README.md (full replacement, under 300 lines) with these sections: (1) centered header with badges, (2) 357-agent tagline, (3) 3-sentence What is this with pip install, (4) 4-line quickstart, (5) mermaid architecture, (6) comparison table vs LangGraph/CrewAI/OpenAI Agents SDK, (7) benchmark table with REAL numbers, (8) feature maturity from STATUS.md, (9) live demo curl, (10) contributing 3-liner, (11) license
- [ ] Step 3: Replace placeholder values with real numbers
- [ ] Step 4: wc -l README.md -> must be <= 300

---

## Task 9: Final Verification

- [ ] python -m pytest tests/ -v -> all pass
- [ ] ls evals/tasks/*.yaml | wc -l -> 20
- [ ] python3 evals/extract_numbers.py -> 7 layers shown
- [ ] wc -l README.md -> <= 300
- [ ] swarm eval --stub --tasks management -> 3 tasks, no crash

---

## Self-Review

Spec coverage:
- 20 YAML tasks across 7 layers -> Task 1
- evals/judge.py LLM-as-judge + rule-based fallback -> Task 2
- evals/runner.py JSON + Markdown output -> Task 3
- swarm eval --tasks --save-baseline --compare -> Task 4
- Live run saves evals/baselines/v0.1.0.json -> Task 5
- CI smoke eval stub mode (2 layers) -> Task 6
- Apache-2.0 LICENSE -> Task 7
- README under 300 lines, real numbers, viral structure -> Task 8

Type consistency: RubricDimSpec (runner.py, YAML loading) and RubricDimension (judge.py, scoring) are distinct dataclasses. runner._run_task() converts RubricDimSpec->RubricDimension explicitly before calling score_rubric(). Consistent across Tasks 2, 3, 4.

Placeholder scan: README benchmark table uses placeholder text in Task 8 Step 2, replaced by real data in Step 3. No other TBDs.

GIF: Manual step. Requires asciinema/agg or equivalent terminal recorder. Noted in Task 8. Cannot be automated.
