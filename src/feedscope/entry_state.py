import typer
from typing import List, Optional
from typing_extensions import Annotated
import json
import httpx
from datetime import datetime

from .config import get_config
from .client import get_client
from .utils import fetch_and_display_entries

unread_app = typer.Typer(help="Manage unread entries")
starred_app = typer.Typer(help="Manage starred entries")
updated_app = typer.Typer(help="Manage updated entries")
recently_read_app = typer.Typer(help="Manage recently read entries")


def _manage_entries_state(
    ctx: typer.Context,
    endpoint: str,
    method: str,
    entry_ids: List[int],
    key: str,
    json_output: bool = False,
):
    config = get_config()
    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    if not entry_ids:
        typer.echo("No entry IDs provided.", err=True)
        return

    if len(entry_ids) > 1000:
        typer.echo("❌ Limit of 1,000 entry_ids per request.", color=typer.colors.RED)
        raise typer.Exit(1)

    url = f"https://api.feedbin.com/v2/{endpoint}.json"
    data = {key: entry_ids}

    try:
        with get_client() as client:
            response = client.request(
                method,
                url,
                json=data,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 200:
                result = response.json()
                if json_output:
                    typer.echo(json.dumps(result, indent=2))
                else:
                    typer.echo(f"Successfully processed {len(result)} entries.")
            else:
                typer.echo(f"Error: {response.status_code}", err=True)
                raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


# Unread
@unread_app.command(name="list")
def list_unread(
    ctx: typer.Context,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List unread entry IDs."""
    fetch_and_display_entries(
        ctx, "https://api.feedbin.com/v2/unread_entries.json", {}, json_output
    )


@unread_app.command(name="mark-read")
def mark_read(
    ctx: typer.Context,
    entry_ids: Annotated[List[int], typer.Argument(help="Entry IDs to mark as read")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Mark entries as read (remove from unread)."""
    _manage_entries_state(
        ctx, "unread_entries", "DELETE", entry_ids, "unread_entries", json_output
    )


@unread_app.command(name="mark-unread")
def mark_unread(
    ctx: typer.Context,
    entry_ids: Annotated[List[int], typer.Argument(help="Entry IDs to mark as unread")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Mark entries as unread."""
    _manage_entries_state(
        ctx, "unread_entries", "POST", entry_ids, "unread_entries", json_output
    )


# Starred
@starred_app.command(name="list")
def list_starred(
    ctx: typer.Context,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List starred entry IDs."""
    fetch_and_display_entries(
        ctx, "https://api.feedbin.com/v2/starred_entries.json", {}, json_output
    )


@starred_app.command(name="star")
def star_entries(
    ctx: typer.Context,
    entry_ids: Annotated[List[int], typer.Argument(help="Entry IDs to star")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Star entries."""
    _manage_entries_state(
        ctx, "starred_entries", "POST", entry_ids, "starred_entries", json_output
    )


@starred_app.command(name="unstar")
def unstar_entries(
    ctx: typer.Context,
    entry_ids: Annotated[List[int], typer.Argument(help="Entry IDs to unstar")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Unstar entries."""
    _manage_entries_state(
        ctx, "starred_entries", "DELETE", entry_ids, "starred_entries", json_output
    )


# Updated
@updated_app.command(name="list")
def list_updated(
    ctx: typer.Context,
    since: Annotated[
        Optional[datetime],
        typer.Option(help="Get entries updated after this timestamp"),
    ] = None,
    include_diff: Annotated[
        bool, typer.Option(help="Fetch details including content diff")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List updated entry IDs."""
    if include_diff:
        config = get_config()
        if not config.auth.email or not config.auth.password:
            typer.echo(
                "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
                color=typer.colors.RED,
            )
            raise typer.Exit(1)

        params = {}
        if since:
            params["since"] = since.isoformat()

        try:
            with get_client() as client:
                response = client.get(
                    "https://api.feedbin.com/v2/updated_entries.json",
                    params=params,
                    auth=(config.auth.email, config.auth.password),
                )
                if response.status_code != 200:
                    typer.echo(
                        f"Error fetching updated IDs: {response.status_code}", err=True
                    )
                    raise typer.Exit(1)
                ids = response.json()

            if not ids:
                typer.echo("No updated entries.")
                return

            batch_ids = ids[:100]
            ids_str = ",".join(map(str, batch_ids))

            entries_params = {
                "ids": ids_str,
                "include_content_diff": "true",
                "include_original": "true",
            }

            fetch_and_display_entries(
                ctx,
                "https://api.feedbin.com/v2/entries.json",
                entries_params,
                json_output,
            )

            if len(ids) > 100:
                typer.echo(
                    f"Warning: Only showing first 100 of {len(ids)} updated entries.",
                    err=True,
                )

        except httpx.RequestError as e:
            typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
            raise typer.Exit(1)

    else:
        params = {}
        if since:
            params["since"] = since.isoformat()

        fetch_and_display_entries(
            ctx, "https://api.feedbin.com/v2/updated_entries.json", params, json_output
        )


@updated_app.command(name="mark-read")
def mark_updated_read(
    ctx: typer.Context,
    entry_ids: Annotated[List[int], typer.Argument(help="Entry IDs to mark as read")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Mark updated entries as read."""
    _manage_entries_state(
        ctx, "updated_entries", "DELETE", entry_ids, "updated_entries", json_output
    )


# Recently Read
@recently_read_app.command(name="list")
def list_recently_read(
    ctx: typer.Context,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List recently read entry IDs."""
    fetch_and_display_entries(
        ctx, "https://api.feedbin.com/v2/recently_read_entries.json", {}, json_output
    )


@recently_read_app.command(name="create")
def create_recently_read(
    ctx: typer.Context,
    entry_ids: Annotated[
        List[int], typer.Argument(help="Entry IDs to add to recently read")
    ],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Add entries to recently read."""
    _manage_entries_state(
        ctx,
        "recently_read_entries",
        "POST",
        entry_ids,
        "recently_read_entries",
        json_output,
    )
