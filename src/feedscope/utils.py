"""Utility functions for Feedscope CLI."""

import typer
import httpx
import json
from loguru import logger
from .client import get_client
from .config import get_config


def fetch_and_display_entries(
    ctx: typer.Context, url: str, params: dict, json_output: bool
):
    """
    Fetches entries from URL with params and displays them.
    Shared by entries, feed, updated commands.
    """
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    logger.debug("Fetching entries from {} with params {}", url, params)

    try:
        with get_client() as client:
            response = client.get(
                url,
                params=params,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code != 200:
                typer.secho(f"Error fetching entries: {response.status_code}", err=True)
                if response.status_code == 403:
                    typer.secho("Forbidden. Check if you have access.", err=True)
                elif response.status_code == 404:
                    typer.secho("Not found.", err=True)
                raise typer.Exit(1)

            entries = response.json()

            if json_output:
                typer.secho(json.dumps(entries, indent=2))
            else:
                for entry in entries:
                    if isinstance(entry, int):
                        # It's a list of IDs (e.g. unread, starred, updated)
                        typer.secho(entry)
                    else:
                        title = entry.get("title") or "(No Title)"
                        entry_id = entry.get("id")
                        published = entry.get("published")
                        typer.secho(f"[{entry_id}] {published} - {title}")

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
