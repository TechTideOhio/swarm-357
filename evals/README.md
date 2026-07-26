# Evals

Budgeted quality harness for Swarm 357.

## Layout

| Path | Purpose |
|------|---------|
| `tasks.yaml` | 25-task catalog (20 single, 5 swarm) |
| `run_evals.py` | Runner: keyword + LLM judge, `$5` cap, checkpoint/resume |
| `baselines/` | Versioned baselines + `latest.json` |
| `results/` | Per-run JSON/Markdown reports + `checkpoint_live.json` |

## Catalog by layer

| Layer | Single | Swarm |
|-------|-------:|------:|
| research | 3 | 0 |
| sales | 3 | 1 |
| support | 3 | 1 |
| marketing | 3 | 1 |
| seo | 3 | 0 |
| operations | 3 | 1 |
| management | 2 | 1 |
| **Total** | **20** | **5** |

## Quick run

```bash
# From the repository root
python -u evals/run_evals.py --budget 5.0 --resume --save-baseline --compare
```

Flags: `--swarm`, `--swarm-only`, `--repeats N`, `--budget`, `--resume`, `--save-baseline`, `--compare`.

Environment: see [docs/EVALS.md](../docs/EVALS.md). Writes are sandboxed under a temp `SWARM_WRITE_SAFE_ROOT` set by the harness.

## Regenerating docs charts

```bash
python scripts/render_eval_assets.py
```

Emits `docs/assets/eval-results.svg` and `docs/assets/eval-results.snippet.md` from `baselines/latest.json`.
