# Design and Brand

The Swarm 357 design system lives with the product surface it describes, in the landing repository.

**Canonical reference:** `DESIGN.md` at the root of [TechTideOhio/swarm-357-site](https://github.com/TechTideOhio/swarm-357-site)

**Reader-friendly summary:** [swarm357fe.up.railway.app/docs/resources/design](https://swarm357fe.up.railway.app/docs/resources/design)

## Why the split

This repository ships the Python package, the Rust Memvid bridge, the roster, and the documentation source. It has no UI. Putting tokens, class tiers, and interaction rules here would mean maintaining a copy that drifts from the code that implements it.

What lives where:

| Concern | Repository |
|---------|------------|
| Color, typography, spacing, motion, interaction states | [swarm-357-site](https://github.com/TechTideOhio/swarm-357-site) |
| Component class tiers and enforcement scripts | [swarm-357-site](https://github.com/TechTideOhio/swarm-357-site) |
| Diagram and logo sources | This repository, `docs/assets/` |
| Product positioning and maturity language | This repository, [README.md](../README.md) and [STATUS.md](../STATUS.md) |

## Brand assets

Sources are authored here and mirrored into the site's `public/assets/`. Regenerate them here rather than editing the copies.

| Asset | File |
|-------|------|
| Banner | `docs/assets/banner.svg` |
| Logo mark | `docs/assets/logo-mark.svg` |
| Logo wordmark | `docs/assets/logo-wordmark.svg` |
| Architecture diagram | `docs/assets/architecture.svg` |
| Request lifecycle diagram | `docs/assets/request-lifecycle.svg` |
| Eval results chart | `docs/assets/eval-results.svg` |

Eval charts are generated, not drawn. Run `python scripts/render_eval_assets.py` after a new baseline lands in `evals/baselines/latest.json`. Never hand-edit the numbers in a chart or in prose.

## Copy standards that apply to this repository

The landing site enforces these in CI, and documentation here is synced into the site, so the same rules apply to Markdown in this repository.

- No em dashes or en dashes in public-facing documentation. Use a comma, a period, a colon, or a hyphen.
- Maturity words are reserved. Stable, Beta, Experimental, and Not implemented mean what [STATUS.md](../STATUS.md) says they mean.
- Claims that can be measured should link to the check that measures them, such as [docs/VERIFY.md](VERIFY.md) or [docs/EVALS.md](EVALS.md).
- Link to repository roots rather than to files on a branch. Deep links rot.

Soul templates under `templates/soul/` are agent persona prompts rather than public copy, so the dash rule does not apply to them.
