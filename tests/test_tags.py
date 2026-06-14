import httpx
import respx
from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()


def test_tags_help():
    result = runner.invoke(app, ["tags", "--help"])
    assert result.exit_code == 0
    assert "Manage tags" in result.stdout


@respx.mock
def test_tags_rename(auth_config):
    respx.post("https://api.feedbin.com/v2/tags.json").mock(
        return_value=httpx.Response(200, json=[])
    )
    result = runner.invoke(
        app, ["tags", "rename", "--old-name", "Old", "--new-name", "New"]
    )
    assert result.exit_code == 0


@respx.mock
def test_tags_delete(auth_config):
    respx.request("DELETE", "https://api.feedbin.com/v2/tags.json").mock(
        return_value=httpx.Response(200, json=[])
    )
    result = runner.invoke(app, ["tags", "delete", "--name", "Tag"], input="y\n")
    assert result.exit_code == 0


@respx.mock
def test_taggings_crud(auth_config):
    # List
    respx.get("https://api.feedbin.com/v2/taggings.json").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "feed_id": 10, "name": "Tag"}])
    )
    result = runner.invoke(app, ["taggings", "list"])
    assert result.exit_code == 0
    assert "Tag" in result.stdout

    # Create
    respx.post("https://api.feedbin.com/v2/taggings.json").mock(
        return_value=httpx.Response(201, json={"id": 2})
    )
    result = runner.invoke(
        app, ["taggings", "create", "--feed-id", "10", "--name", "NewTag"]
    )
    assert result.exit_code == 0

    # Delete
    respx.delete("https://api.feedbin.com/v2/taggings/2.json").mock(
        return_value=httpx.Response(204)
    )
    result = runner.invoke(app, ["taggings", "delete", "2"], input="y\n")
    assert result.exit_code == 0
