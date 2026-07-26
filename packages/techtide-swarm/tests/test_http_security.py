# file: packages/techtide-swarm/tests/test_http_security.py
# description: Production auth fail-closed and constant-time key rejection
# reference: techtide_swarm.http_security

from __future__ import annotations

import pytest
from fastapi import HTTPException

from techtide_swarm.http_security import require_swarm_write_key


def test_production_fail_closed_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SWARM_ALLOW_STUB", raising=False)
    monkeypatch.delenv("SWARM_API_KEY", raising=False)
    monkeypatch.setenv("SWARM_ENV", "production")
    monkeypatch.delenv("SWARM_REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)

    with pytest.raises(HTTPException) as exc_info:
        require_swarm_write_key(x_swarm_api_key=None)
    assert exc_info.value.status_code == 503
    assert "SWARM_API_KEY" in exc_info.value.detail


def test_require_auth_fail_closed_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SWARM_ALLOW_STUB", raising=False)
    monkeypatch.delenv("SWARM_API_KEY", raising=False)
    monkeypatch.delenv("SWARM_ENV", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)
    monkeypatch.setenv("SWARM_REQUIRE_AUTH", "1")

    with pytest.raises(HTTPException) as exc_info:
        require_swarm_write_key(x_swarm_api_key="anything")
    assert exc_info.value.status_code == 503


def test_non_production_fail_open_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SWARM_API_KEY", raising=False)
    monkeypatch.delenv("SWARM_ENV", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("SWARM_REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)

    assert require_swarm_write_key(x_swarm_api_key=None) is True


def test_bad_key_returns_401_constant_time_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SWARM_API_KEY", "correct-secret-key-value")
    monkeypatch.delenv("SWARM_ENV", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("SWARM_REQUIRE_AUTH", raising=False)
    monkeypatch.delenv("RAILWAY_ENVIRONMENT", raising=False)

    with pytest.raises(HTTPException) as exc_info:
        require_swarm_write_key(x_swarm_api_key="wrong-key")
    assert exc_info.value.status_code == 401

    with pytest.raises(HTTPException) as exc_info2:
        require_swarm_write_key(x_swarm_api_key=None)
    assert exc_info2.value.status_code == 401

    assert require_swarm_write_key(x_swarm_api_key="correct-secret-key-value") is True
