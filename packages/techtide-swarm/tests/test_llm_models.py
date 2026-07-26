# file: packages/techtide-swarm/tests/test_llm_models.py
# description: OpenRouter model mapping must not silently downgrade opus/sonnet
# reference: techtide_swarm.llm

from __future__ import annotations

import pytest

from techtide_swarm.llm import cheap_openrouter_mode, model_id


@pytest.fixture()
def openrouter_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-key")
    monkeypatch.delenv("SWARM_OPENROUTER_CHEAP", raising=False)
    monkeypatch.delenv("SWARM_MODEL_OPUS", raising=False)
    monkeypatch.delenv("SWARM_MODEL_SONNET", raising=False)
    monkeypatch.delenv("SWARM_MODEL_HAIKU", raising=False)


def test_openrouter_does_not_map_opus_sonnet_to_haiku(openrouter_env: None) -> None:
    assert cheap_openrouter_mode() is False
    opus = model_id("opus")
    sonnet = model_id("sonnet")
    haiku = model_id("haiku")
    assert "opus" in opus.lower()
    assert "sonnet" in sonnet.lower()
    assert "haiku" in haiku.lower()
    assert opus != haiku
    assert sonnet != haiku


def test_openrouter_cheap_flag_maps_to_haiku(
    openrouter_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SWARM_OPENROUTER_CHEAP", "1")
    assert cheap_openrouter_mode() is True
    assert model_id("opus") == "anthropic/claude-3-haiku"
    assert model_id("sonnet") == "anthropic/claude-3-haiku"
    assert model_id("haiku") == "anthropic/claude-3-haiku"


def test_anthropic_defaults_keep_tiers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    monkeypatch.delenv("SWARM_OPENROUTER_CHEAP", raising=False)
    monkeypatch.delenv("SWARM_MODEL_OPUS", raising=False)
    monkeypatch.delenv("SWARM_MODEL_SONNET", raising=False)
    monkeypatch.delenv("SWARM_MODEL_HAIKU", raising=False)

    assert "opus" in model_id("opus")
    assert "sonnet" in model_id("sonnet")
    assert "haiku" in model_id("haiku")
