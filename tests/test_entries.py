import httpx
import respx
import pytest
from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()

def test_entries_help():
    result = runner.invoke(app, ["entries", "--help"])
    assert result.exit_code == 0
    assert "Retrieve and manage entries" in result.stdout

@respx.mock
def test_entries_list(auth_config):
    respx.get("https://api.feedbin.com/v2/entries.json").mock(
        return_value=httpx.Response(200, json=[
            {"id": 1, "title": "Test Entry", "published": "2025-01-01T00:00:00.000000Z"}
        ])
    )
    
    result = runner.invoke(app, ["entries", "list"])
    assert result.exit_code == 0
    assert "[1] 2025-01-01T00:00:00.000000Z - Test Entry" in result.stdout

@respx.mock
def test_entries_list_filters(auth_config):
    mock = respx.get("https://api.feedbin.com/v2/entries.json").mock(
        return_value=httpx.Response(200, json=[])
    )
    
    result = runner.invoke(app, [
        "entries", "list", 
        "--no-read", 
        "--starred",
        "--since", "2025-01-01T00:00:00",
        "--include-enclosure"
    ])
    assert result.exit_code == 0
    
    request = mock.calls[0].request
    assert request.url.params["read"] == "false"
    assert request.url.params["starred"] == "true"
    assert "since" in request.url.params 
    assert request.url.params["include_enclosure"] == "true"

@respx.mock
def test_entries_show(auth_config):
    respx.get("https://api.feedbin.com/v2/entries/1.json").mock(
        return_value=httpx.Response(200, json={
            "id": 1, 
            "title": "Test Entry", 
            "published": "2025-01-01T00:00:00.000000Z",
            "url": "http://example.com"
        })
    )
    
    result = runner.invoke(app, ["entries", "show", "1"])
    assert result.exit_code == 0
    assert "Test Entry" in result.stdout
    assert "http://example.com" in result.stdout

@respx.mock
def test_entries_feed(auth_config):
    respx.get("https://api.feedbin.com/v2/feeds/123/entries.json").mock(
        return_value=httpx.Response(200, json=[
            {"id": 1, "title": "Feed Entry", "published": "2025-01-01T00:00:00.000000Z"}
        ])
    )
    
    result = runner.invoke(app, ["entries", "feed", "123"])
    assert result.exit_code == 0
    assert "Feed Entry" in result.stdout
