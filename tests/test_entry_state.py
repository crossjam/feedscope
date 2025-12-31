import httpx
import respx
import pytest
import json
from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()

def test_unread_help():
    result = runner.invoke(app, ["unread", "--help"])
    assert result.exit_code == 0
    assert "Manage unread entries" in result.stdout

@respx.mock
def test_unread_list(auth_config):
    respx.get("https://api.feedbin.com/v2/unread_entries.json").mock(
        return_value=httpx.Response(200, json=[1, 2, 3])
    )
    result = runner.invoke(app, ["unread", "list"])
    assert result.exit_code == 0
    assert "1" in result.stdout
    assert "3" in result.stdout

@respx.mock
def test_unread_mark_read(auth_config):
    mock = respx.delete("https://api.feedbin.com/v2/unread_entries.json").mock(
        return_value=httpx.Response(200, json=[1, 2])
    )
    result = runner.invoke(app, ["unread", "mark-read", "1", "2"])
    assert result.exit_code == 0
    assert "Successfully processed 2 entries" in result.stdout
    
    assert json.loads(mock.calls[0].request.content) == {"unread_entries": [1, 2]}

@respx.mock
def test_unread_mark_unread(auth_config):
    mock = respx.post("https://api.feedbin.com/v2/unread_entries.json").mock(
        return_value=httpx.Response(200, json=[1])
    )
    result = runner.invoke(app, ["unread", "mark-unread", "1"])
    assert result.exit_code == 0
    assert json.loads(mock.calls[0].request.content) == {"unread_entries": [1]}

@respx.mock
def test_starred_actions(auth_config):
    # list
    respx.get("https://api.feedbin.com/v2/starred_entries.json").mock(
        return_value=httpx.Response(200, json=[10])
    )
    result = runner.invoke(app, ["starred", "list"])
    assert result.exit_code == 0
    assert "10" in result.stdout
    
    # star
    mock_post = respx.post("https://api.feedbin.com/v2/starred_entries.json").mock(
        return_value=httpx.Response(200, json=[10])
    )
    result = runner.invoke(app, ["starred", "star", "10"])
    assert result.exit_code == 0
    assert json.loads(mock_post.calls[0].request.content) == {"starred_entries": [10]}
    
    # unstar
    mock_del = respx.delete("https://api.feedbin.com/v2/starred_entries.json").mock(
        return_value=httpx.Response(200, json=[10])
    )
    result = runner.invoke(app, ["starred", "unstar", "10"])
    assert result.exit_code == 0
    assert json.loads(mock_del.calls[0].request.content) == {"starred_entries": [10]}

@respx.mock
def test_updated_list_diff(auth_config):
    # Mock updated IDs fetch
    respx.get("https://api.feedbin.com/v2/updated_entries.json").mock(
        return_value=httpx.Response(200, json=[100, 101])
    )
    
    # Mock entries details fetch
    mock_entries = respx.get("https://api.feedbin.com/v2/entries.json").mock(
        return_value=httpx.Response(200, json=[
            {"id": 100, "title": "Updated One", "published": "...", "content_diff": "<div>diff</div>"}
        ])
    )
    
    result = runner.invoke(app, ["updated", "list", "--include-diff"])
    assert result.exit_code == 0
    assert "Updated One" in result.stdout
    
    req = mock_entries.calls[0].request
    assert req.url.params["ids"] == "100,101"
    assert req.url.params["include_content_diff"] == "true"
    assert req.url.params["include_original"] == "true"

@respx.mock
def test_recently_read(auth_config):
    respx.get("https://api.feedbin.com/v2/recently_read_entries.json").mock(
        return_value=httpx.Response(200, json=[5])
    )
    result = runner.invoke(app, ["recently-read", "list"])
    assert result.exit_code == 0
    assert "5" in result.stdout
    
    mock_post = respx.post("https://api.feedbin.com/v2/recently_read_entries.json").mock(
        return_value=httpx.Response(200, json=[6])
    )
    result = runner.invoke(app, ["recently-read", "create", "6"])
    assert result.exit_code == 0
    assert json.loads(mock_post.calls[0].request.content) == {"recently_read_entries": [6]}