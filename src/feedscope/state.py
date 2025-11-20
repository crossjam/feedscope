"""Shared state for the CLI application."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer


@dataclass
class AppState:
    """Application-level context passed to subcommands."""

    log_config_path: Path | None = None
    log_config_data: dict[str, Any] | None = None


def get_state(ctx: typer.Context) -> AppState:
    """Retrieve the shared application state from a Typer context."""

    return ctx.ensure_object(AppState)
