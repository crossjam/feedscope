import httpx
import respx
from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()


def test_searches_help():
    result = runner.invoke(app, ["saved-search", "--help"])
    assert result.exit_code == 0
    assert "Manage saved searches" in result.stdout


@respx.mock
def test_searches_list(auth_config):
    respx.get("https://api.feedbin.com/v2/saved_searches.json").mock(
        return_value=httpx.Response(
            200, json=[{"id": 1, "name": "Test Search", "query": "test"}]
        )
    )
    result = runner.invoke(app, ["saved-search", "list"])
    assert result.exit_code == 0
    assert "Test Search" in result.stdout


@respx.mock
def test_searches_get(auth_config):
    # IDs only
    respx.get("https://api.feedbin.com/v2/saved_searches/1.json").mock(
        return_value=httpx.Response(200, json=[10, 11])
    )
    result = runner.invoke(app, ["saved-search", "get", "1"])
    assert result.exit_code == 0
    assert "10" in result.stdout

    # Entries
    mock_entries = respx.get("https://api.feedbin.com/v2/saved_searches/1.json").mock(
        return_value=httpx.Response(
            200, json=[{"id": 10, "title": "Entry 10", "published": "..."}]
        )
    )
    result = runner.invoke(app, ["saved-search", "get", "1", "--include-entries"])
    assert result.exit_code == 0
    assert "Entry 10" in result.stdout
    assert mock_entries.calls[1].request.url.params["include_entries"] == "true"


@respx.mock
def test_searches_crud(auth_config):
    # Create
    respx.post("https://api.feedbin.com/v2/saved_searches.json").mock(
        return_value=httpx.Response(201, json={"id": 2, "name": "New", "query": "new"})
    )
    result = runner.invoke(
        app, ["saved-search", "create", "--name", "New", "--query", "new"]
    )
    assert result.exit_code == 0

    # Update
    respx.patch("https://api.feedbin.com/v2/saved_searches/2.json").mock(
        return_value=httpx.Response(200, json={"id": 2, "name": "Updated"})
    )
    result = runner.invoke(app, ["saved-search", "update", "2", "--name", "Updated"])
    assert result.exit_code == 0

    # Delete
    respx.delete("https://api.feedbin.com/v2/saved_searches/2.json").mock(
        return_value=httpx.Response(204)
    )
    result = runner.invoke(app, ["saved-search", "delete", "2"], input="y\n")
    assert result.exit_code == 0
