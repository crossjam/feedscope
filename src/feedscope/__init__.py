import json
from pathlib import Path
import tomllib

import typer
from loguru import logger
from loguru_config import LoguruConfig
from typing_extensions import Annotated

from .auth import auth_app
from .config_cli import config_app
from .state import AppState
from .subscriptions import subscriptions_app


def configure_logging(config_file: Path | None) -> AppState:
    """Configure loguru from a config file if provided."""

    if config_file is None:
        return AppState()

    try:
        if config_file.suffix.lower() == ".toml":
            with config_file.open("rb") as handle:
                config_data = tomllib.load(handle)
        else:
            with config_file.open("r", encoding="utf-8") as handle:
                config_data = json.load(handle)

        LoguruConfig.load(config_data)
        logger.debug("Logging configured from {}", config_file)
        return AppState(log_config_path=config_file, log_config_data=config_data)
    except Exception as exc:  # pragma: no cover - defensive catch for CLI UX
        typer.echo(
            f"❌ Failed to configure logging from {config_file}: {exc}",
            err=True,
        )
        raise typer.Exit(1) from exc


app = typer.Typer(help="Feedscope - CLI for working with Feedbin API content")
app.add_typer(auth_app, name="auth")
app.add_typer(config_app, name="config")
app.add_typer(subscriptions_app, name="subscriptions")


@app.callback()
def root(
    ctx: typer.Context,
    log_config: Annotated[
        Path | None,
        typer.Option(
            "--log-config",
            help="Path to a Loguru configuration file",
            exists=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ] = None,
) -> None:
    ctx.obj = configure_logging(log_config)


def main() -> None:
    app()
