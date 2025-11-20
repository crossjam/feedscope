"""Basic CLI operation tests for feedscope."""
from pathlib import Path
import json
import os

import pytest
from platformdirs import user_config_dir
from typer.testing import CliRunner

# Ensure configuration writes are isolated to a test-specific directory
TEST_CONFIG_HOME = Path(__file__).parent / "_config_home"
TEST_CONFIG_HOME.mkdir(parents=True, exist_ok=True)
os.environ["XDG_CONFIG_HOME"] = str(TEST_CONFIG_HOME)

from feedscope import app


CONFIG_FILE = Path(user_config_dir("dev.pirateninja.feedscope")) / "config.toml"


@pytest.fixture(autouse=True)
def clean_config_file() -> None:
    """Ensure the config file is removed before and after each test."""

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()

    yield

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()


runner = CliRunner()


def test_root_help_shows_subcommands() -> None:
    """Root help should list available subcommands."""
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Feedscope - CLI for working with Feedbin API content" in result.stdout
    assert "auth" in result.stdout
    assert "subscriptions" in result.stdout


def test_auth_status_without_credentials() -> None:
    """Status should warn and exit when no credentials are present."""
    result = runner.invoke(app, ["auth", "status"])

    assert result.exit_code == 1
    assert "No credentials stored" in result.stdout
    assert "feedscope auth login" in result.stdout


def test_auth_whoami_without_credentials() -> None:
    """Whoami should return a friendly message when nothing is configured."""
    result = runner.invoke(app, ["auth", "whoami"])

    assert result.exit_code == 0
    assert "No credentials stored." in result.stdout
    assert "Run `feedscope auth login`" in result.stdout


def test_log_config_initializes_loguru(tmp_path: Path) -> None:
    """Providing a log config file should configure loguru before commands run."""

    log_file = tmp_path / "cli.log"
    config_file = tmp_path / "logging.json"

    config_file.write_text(
        json.dumps(
            {
                "handlers": [
                    {
                        "sink": str(log_file),
                        "format": "{message}",
                        "level": "DEBUG",
                    }
                ]
            }
        )
    )

    result = runner.invoke(app, ["--log-config", str(config_file), "auth", "whoami"])

    assert result.exit_code == 0
    assert log_file.exists()
    log_contents = log_file.read_text()
    assert "Logging configured from" in log_contents
    assert str(config_file) in log_contents


def test_log_config_supports_toml(tmp_path: Path) -> None:
    """Loguru configuration should load from TOML files."""

    log_file = tmp_path / "cli.log"
    config_file = tmp_path / "logging.toml"

    config_file.write_text(
        "\n".join(
            [
                "handlers = [",
                f"  {{ sink = \"{log_file}\", format = \"{{message}}\", level = \"DEBUG\" }}",
                "]",
                "",
            ]
        )
    )

    result = runner.invoke(app, ["--log-config", str(config_file), "auth", "whoami"])

    assert result.exit_code == 0
    assert log_file.exists()
    log_contents = log_file.read_text()
    assert "Logging configured from" in log_contents
    assert str(config_file) in log_contents
