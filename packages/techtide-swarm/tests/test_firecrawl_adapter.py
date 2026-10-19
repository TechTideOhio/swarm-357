from unittest.mock import patch

import pytest

firecrawl = pytest.importorskip("firecrawl")
from firecrawl.v2.types import Document, SearchData

from techtide_swarm.tools.web_scrape import _MAX_CHARS, _scrape_firecrawl
from techtide_swarm.tools.web_search import _search_firecrawl


def test_search_uses_sdk_models_and_limits_results(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    response = SearchData(web=[
        {"title": "First", "url": "https://example.com", "description": "Found"},
        {"title": "Second", "url": "https://example.org", "description": "Other"},
    ])
    with patch("firecrawl.v2.methods.search.search", return_value=response) as search:
        result = _search_firecrawl("query", 1)
    assert "First" in result and "Found" in result and "Second" not in result
    assert search.call_args.args[1].query == "query"
    assert search.call_args.args[1].limit == 1


def test_search_empty_result(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    with patch("firecrawl.v2.methods.search.search", return_value=SearchData(web=[])):
        assert _search_firecrawl("query", 5) == "No results found."


def test_scrape_returns_markdown_not_model_representation(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    with patch("firecrawl.v2.methods.scrape.scrape", return_value=Document(markdown="# Hello")):
        assert _scrape_firecrawl("https://example.com") == "# Hello"


def test_scrape_bounds_output_and_handles_empty_document(monkeypatch):
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    with patch("firecrawl.v2.methods.scrape.scrape", return_value=Document(markdown="x" * (_MAX_CHARS + 1))):
        assert len(_scrape_firecrawl("https://example.com")) == _MAX_CHARS
    with patch("firecrawl.v2.methods.scrape.scrape", return_value=Document()):
        assert _scrape_firecrawl("https://example.com") == ""


def test_exa_uses_current_search_signature(monkeypatch):
    from types import SimpleNamespace
    from exa_py import Exa
    from techtide_swarm.tools.web_search import _search_exa

    monkeypatch.setenv("EXA_API_KEY", "test-key")
    response = SimpleNamespace(results=[SimpleNamespace(title="Title", url="https://example.com", text="Body")])
    with patch.object(Exa, "search", autospec=True, return_value=response) as search:
        assert "Body" in _search_exa("query", 3)
    assert search.call_args.kwargs == {"num_results": 3, "contents": {"text": {"max_characters": 1500}}}
