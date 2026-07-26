# file: packages/techtide-swarm/tests/conftest.py
# description: Shared pytest fixtures for unit tests (explicit stub allow-list)
# reference: techtide_swarm.agent, techtide_swarm.http_security

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _allow_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests may use Agent stub mode without live credentials.

    Fail-closed credential / auth tests must ``monkeypatch.delenv("SWARM_ALLOW_STUB")``.
    Production auth signals are cleared so local fail-open stays the default.
    """
    monkeypatch.setenv("SWARM_ALLOW_STUB", "1")
    monkeypatch.delenv("SWARM_ENV", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("SWARM_REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    # Avoid accidental live LLM calls from developer shells
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    # server.py setdefault(SWARM_SERVER_MODE) must not leak into unit tool tests
    monkeypatch.delenv("SWARM_SERVER_MODE", raising=False)
    monkeypatch.delenv("SWARM_WORKSPACE_ROOT", raising=False)
    monkeypatch.delenv("SWARM_WRITE_SAFE_ROOT", raising=False)
    monkeypatch.delenv("SWARM_CONFINEMENT", raising=False)
    # Default product confine is CWD; unit tests use tmp_path outside CWD.
    # Confinement tests must monkeypatch.delenv("SWARM_UNSAFE_FS").
    monkeypatch.setenv("SWARM_UNSAFE_FS", "1")
