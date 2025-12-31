from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()

def test_searches_help():
    result = runner.invoke(app, ["saved-search", "--help"])
    assert result.exit_code == 0
    assert "Manage saved searches" in result.stdout
