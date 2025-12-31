from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()

def test_tags_help():
    result = runner.invoke(app, ["tags", "--help"])
    assert result.exit_code == 0
    assert "Manage tags" in result.stdout
