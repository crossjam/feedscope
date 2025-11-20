"""Configuration-related CLI commands."""

from pathlib import Path

import typer
from platformdirs import user_config_dir
from rich.console import Console


config_app = typer.Typer(help="Configuration commands")

console = Console(force_terminal=False, color_system=None)


@config_app.command()
def location(ctx: typer.Context) -> None:
    """Show the user configuration directory for feedscope."""

    config_dir = Path(user_config_dir("dev.pirateninja.feedscope"))
    console.print(f"Configuration directory: {config_dir}")
