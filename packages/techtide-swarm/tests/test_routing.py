# file: packages/techtide-swarm/tests/test_routing.py
# description: Structured routing decision parsing and validation
# reference: techtide_swarm.runtime.routing

from __future__ import annotations

import pytest

from techtide_swarm.runtime.routing import RoutingError, parse_routing_decision

AVAILABLE = {"market_analyst", "content_strategist", "crm_operator"}


def test_parse_routing_decision_accepts_json() -> None:
    raw = '{"roles": ["market_analyst", "crm_operator"], "rationale": "research then CRM"}'
    decision = parse_routing_decision(raw, AVAILABLE)
    assert decision.roles == ["market_analyst", "crm_operator"]
    assert "research" in decision.rationale


def test_parse_routing_decision_accepts_json_in_prose() -> None:
    raw = 'Here you go:\n{"roles": ["content_strategist"], "rationale": "copy"}\nThanks'
    decision = parse_routing_decision(raw, AVAILABLE)
    assert decision.roles == ["content_strategist"]


def test_parse_routing_decision_rejects_unknown_roles() -> None:
    raw = '{"roles": ["ghost_role", "not_real"], "rationale": "bad"}'
    with pytest.raises(RoutingError, match="no known roles"):
        parse_routing_decision(raw, AVAILABLE)


def test_parse_routing_decision_rejects_empty() -> None:
    with pytest.raises(RoutingError, match="empty"):
        parse_routing_decision("", AVAILABLE)
    with pytest.raises(RoutingError, match="empty"):
        parse_routing_decision("   \n", AVAILABLE)


def test_parse_routing_decision_rejects_empty_roles_list() -> None:
    with pytest.raises(RoutingError):
        parse_routing_decision('{"roles": [], "rationale": "none"}', AVAILABLE)
