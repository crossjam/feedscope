"""Configuration-related CLI commands."""

from pathlib import Path

import typer
from loguru import logger
from platformdirs import user_config_dir
from rich.console import Console

from .state import get_state


config_app = typer.Typer(help="Configuration commands")

console = Console(force_terminal=False, color_system=None)


@config_app.command()
def location(ctx: typer.Context) -> None:
    """Show the user configuration directory for feedscope."""

    state = get_state(ctx)
    config_dir = Path(user_config_dir("dev.pirateninja.feedscope"))
    logger.debug(
        "Configuration directory {} requested with log config {}",
        config_dir,
        state.log_config_path,
    )
    console.print(f"Configuration directory: {config_dir}")
