from pathlib import Path
import tomllib

import typer
from loguru import logger
from loguru_config import LoguruConfig
from typing_extensions import Annotated

from .auth import auth_app
from .subscriptions import subscriptions_app


def configure_logging(config_file: Path | None) -> None:
    """Configure loguru from a config file if provided."""

    if config_file is None:
        return

    try:
        if config_file.suffix.lower() == ".toml":
            with config_file.open("rb") as handle:
                config_data = tomllib.load(handle)
            LoguruConfig.load(config_data)
        else:
            LoguruConfig.load(str(config_file))
        logger.debug("Logging configured from {}", config_file)
    except Exception as exc:  # pragma: no cover - defensive catch for CLI UX
        typer.echo(
            f"❌ Failed to configure logging from {config_file}: {exc}",
            err=True,
        )
        raise typer.Exit(1) from exc


app = typer.Typer(help="Feedscope - CLI for working with Feedbin API content")
app.add_typer(auth_app, name="auth")
app.add_typer(subscriptions_app, name="subscriptions")


@app.callback()
def root(
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
    configure_logging(log_config)


def main() -> None:
    app()
