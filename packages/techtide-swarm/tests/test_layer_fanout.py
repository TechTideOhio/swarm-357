# file: packages/techtide-swarm/tests/test_layer_fanout.py
# description: Layer fan-out bounds — one_per_role vs full_fanout
# reference: techtide_swarm.swarm

from __future__ import annotations

import textwrap
from pathlib import Path

from techtide_swarm.swarm import Swarm


def _compact_with_duplicates(tmp_path: Path) -> Path:
    compact = textwrap.dedent("""\
        swarm:
          version: "2.0"
          layer_budgets:
            research: {daily_limit_usd: 100.0, model_preference: sonnet}
        layers:
          research:
            roles:
              market_analyst: {count: 5, model: sonnet, budget_usd: 1.0, tools: [Read]}
              synthesizer: {count: 3, model: sonnet, budget_usd: 1.0, tools: [Read]}
            soul: templates/soul/research/market-analyst.md
    """)
    cfg = tmp_path / "compact.yaml"
    cfg.write_text(compact, encoding="utf-8")
    return cfg


def test_one_per_role_bounds_agent_count(tmp_path: Path) -> None:
    swarm = Swarm(_compact_with_duplicates(tmp_path))
    bounded = swarm._agents_for_layer("research", one_per_role=True, full_fanout=False)
    roles = [c.role for c in bounded]
    assert len(bounded) == 2
    assert set(roles) == {"market_analyst", "synthesizer"}
    assert len(roles) == len(set(roles))


def test_full_fanout_increases_agent_count(tmp_path: Path) -> None:
    swarm = Swarm(_compact_with_duplicates(tmp_path))
    bounded = swarm._agents_for_layer("research", one_per_role=True, full_fanout=False)
    full = swarm._agents_for_layer("research", one_per_role=False, full_fanout=True)
    assert len(full) > len(bounded)
    assert len(full) == 8  # 5 + 3 from compact counts
