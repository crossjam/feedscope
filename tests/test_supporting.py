import httpx
import respx
import pytest
from typer.testing import CliRunner
from feedscope import app
import json

runner = CliRunner()

def test_imports_help():
    result = runner.invoke(app, ["imports", "--help"])
    assert result.exit_code == 0
    assert "Manage imports" in result.stdout

def test_extract_help():
    result = runner.invoke(app, ["extract", "--help"])
    assert result.exit_code == 0
    assert "Extract content from a URL" in result.stdout

@respx.mock
def test_imports_create(auth_config, tmp_path):
    opml_file = tmp_path / "subscriptions.xml"
    opml_file.write_text("<opml>...</opml>")
    
    mock_post = respx.post("https://api.feedbin.com/v2/imports.json").mock(
        return_value=httpx.Response(201, json={"id": 1})
    )
    
    result = runner.invoke(app, ["imports", "create", str(opml_file)])
    assert result.exit_code == 0
    assert "Import created" in result.stdout
    assert mock_post.calls[0].request.headers["Content-Type"] == "text/xml"

@respx.mock
def test_imports_list(auth_config):
    respx.get("https://api.feedbin.com/v2/imports.json").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "complete": True, "created_at": "..."}])
    )
    result = runner.invoke(app, ["imports", "list"])
    assert result.exit_code == 0
    assert "ID: 1" in result.stdout

@respx.mock
def test_pages_save(auth_config):
    respx.post("https://api.feedbin.com/v2/pages.json").mock(
        return_value=httpx.Response(200, json={"id": 100})
    )
    result = runner.invoke(app, ["pages", "save", "--url", "http://example.com", "--title", "Example"])
    assert result.exit_code == 0
    assert "Created Entry ID: 100" in result.stdout

@respx.mock
def test_icons_list(auth_config):
    respx.get("https://api.feedbin.com/v2/icons.json").mock(
        return_value=httpx.Response(200, json=[{"host": "example.com", "url": "http://example.com/icon.png"}])
    )
    result = runner.invoke(app, ["icons", "list"])
    assert result.exit_code == 0
    assert "example.com: http://example.com/icon.png" in result.stdout

@respx.mock
def test_extract(auth_config, config_path):
    # Setup extract config manually since auth_config only sets auth
    import tomlkit
    
    doc = tomlkit.parse(config_path.read_text())
    doc["extract"] = {"username": "user", "secret": "secret"}
    config_path.write_text(tomlkit.dumps(doc))
    
    mock_get = respx.get(url__regex=r"https://extract\.feedbin\.com/parser/user/.*").mock(
        return_value=httpx.Response(200, json={"title": "Extracted", "word_count": 100, "excerpt": "..."})
    )
    
    result = runner.invoke(app, ["extract", "http://example.com"])
    assert result.exit_code == 0
    assert "Title: Extracted" in result.stdout
