from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()

def test_unread_help():
    result = runner.invoke(app, ["unread", "--help"])
    assert result.exit_code == 0
    assert "Manage unread entries" in result.stdout

def test_starred_help():
    result = runner.invoke(app, ["starred", "--help"])
    assert result.exit_code == 0
    assert "Manage starred entries" in result.stdout
