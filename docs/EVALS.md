# Eval harness

> **Hosted docs:** https://swarm357fe.up.railway.app/docs/evals/methodology

Swarm 357 ships a budgeted evaluation suite under [`evals/`](../evals/). Numbers in this document are generated from [`evals/baselines/latest.json`](../evals/baselines/latest.json) via [`scripts/render_eval_assets.py`](../scripts/render_eval_assets.py) - do not hand-edit metrics.

## Methodology

| Gate | Rule |
|------|------|
| Keyword score | Fraction of expected keywords found in output (case-insensitive) |
| Length gate | Output must meet `min_output_length` from the task catalog |
| LLM judge | Optional Haiku rubric score when `SWARM_EVAL_LLM_JUDGE=1` |
| Combined score | `0.55 * keyword + 0.45 * llm_judge` (keyword-only if judge skipped) |
| Pass | `status=success` and combined ≥ 0.5 and length OK |
| Budget | Hard cap (default `$5.00` via `SWARM_EVAL_BUDGET_USD`) |
| Checkpoint | `evals/results/checkpoint_live.json` — resume with `--resume` |
| Regression | `--compare` flags ≥ 0.15 combined-score drops vs baseline |

## Catalog

25 tasks in [`evals/tasks.yaml`](../evals/tasks.yaml): **20 single-agent**, **5 swarm**. Layers: research, sales, support, marketing, SEO, operations, management.

Burn passes (`{task_id}-burnN`) consume remaining budget with tool-enabled single-agent repeats. That is why a baseline can report ~150 executions from a 25-task catalog.

## Current baseline

![Eval results by layer](assets/eval-results.png)

<!-- include generated snippet -->

| Metric | Value |
|--------|------:|
| Executions | 154 |
| Passed gates | 145 |
| Avg combined score | 0.923 |
| Spend | $4.9915 / $5.00 |
| Provider | `openrouter` |
| Agent model | `anthropic/claude-sonnet-4` |
| Judge model | `anthropic/claude-3-haiku` |
| Single-agent pass | 142/142 |
| Swarm pass | 4/12 |

### Honest caveats

- **Swarm timeouts:** 8 of 12 swarm executions hit 150–180s wall-clock timeouts on OpenRouter. Single-agent + tools is the production demo path.
- **Tools on:** Eval agents use `Read`/`Write` with `SWARM_WRITE_SAFE_ROOT` sandboxing.
- **Regenerate:** `python scripts/render_eval_assets.py` after a new baseline.

## Reproduce

```bash
pip install -e "packages/techtide-swarm[dev]"
export OPENROUTER_API_KEY=...          # or ANTHROPIC_API_KEY
export ANTHROPIC_BASE_URL=https://openrouter.ai/api
export SWARM_MODEL_SONNET=anthropic/claude-sonnet-4
export SWARM_EVAL_JUDGE_MODEL=anthropic/claude-3-haiku
export SWARM_EVAL_LLM_JUDGE=1
export SWARM_EVAL_BUDGET_USD=5.0
python -u evals/run_evals.py --budget 5.0 --save-baseline --compare
# or
swarm eval --save-baseline --compare
```

See also [`evals/README.md`](../evals/README.md).
