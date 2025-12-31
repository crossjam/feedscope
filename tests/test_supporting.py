from typer.testing import CliRunner
from feedscope import app

runner = CliRunner()

def test_imports_help():
    result = runner.invoke(app, ["imports", "--help"])
    assert result.exit_code == 0
    assert "Manage imports" in result.stdout

def test_extract_help():
    result = runner.invoke(app, ["extract", "--help"])
    assert result.exit_code == 0
    assert "Extract content from a URL" in result.stdout
