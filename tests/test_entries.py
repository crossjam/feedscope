from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()

def test_entries_help():
    result = runner.invoke(app, ["entries", "--help"])
    assert result.exit_code == 0
    assert "Retrieve and manage entries" in result.stdout
