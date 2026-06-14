import typer
from typing import Optional
from typing_extensions import Annotated
from datetime import datetime
import json
import httpx

from .config import get_config
from .client import get_client
from .utils import fetch_and_display_entries

entries_app = typer.Typer(help="Retrieve and manage entries")


def _build_entry_params(
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    since: Optional[datetime] = None,
    read: Optional[bool] = None,
    starred: Optional[bool] = None,
    mode: Optional[str] = None,
    include_original: bool = False,
    include_enclosure: bool = False,
    include_content_diff: bool = False,
) -> dict:
    params = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if since is not None:
        params["since"] = since.isoformat()
    if read is not None:
        params["read"] = str(read).lower()
    if starred is not None:
        params["starred"] = str(starred).lower()
    if mode is not None:
        params["mode"] = mode
    if include_original:
        params["include_original"] = "true"
    if include_enclosure:
        params["include_enclosure"] = "true"
    if include_content_diff:
        params["include_content_diff"] = "true"
    return params


@entries_app.command(name="list")
def list_entries(
    ctx: typer.Context,
    page: Annotated[Optional[int], typer.Option(help="Page number")] = None,
    per_page: Annotated[
        Optional[int], typer.Option(help="Number of entries per page")
    ] = None,
    since: Annotated[
        Optional[datetime],
        typer.Option(help="Get entries created after this timestamp"),
    ] = None,
    read: Annotated[Optional[bool], typer.Option(help="Filter by read status")] = None,
    starred: Annotated[
        Optional[bool], typer.Option(help="Filter by starred status")
    ] = None,
    mode: Annotated[Optional[str], typer.Option(help="Mode (e.g. extended)")] = None,
    include_original: Annotated[
        bool, typer.Option(help="Include original entry data")
    ] = False,
    include_enclosure: Annotated[
        bool, typer.Option(help="Include enclosure data")
    ] = False,
    include_content_diff: Annotated[
        bool, typer.Option(help="Include content diff")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List entries."""
    params = _build_entry_params(
        page,
        per_page,
        since,
        read,
        starred,
        mode,
        include_original,
        include_enclosure,
        include_content_diff,
    )
    fetch_and_display_entries(
        ctx, "https://api.feedbin.com/v2/entries.json", params, json_output
    )


@entries_app.command(name="feed")
def feed_entries(
    ctx: typer.Context,
    feed_id: Annotated[int, typer.Argument(help="Feed ID")],
    page: Annotated[Optional[int], typer.Option(help="Page number")] = None,
    per_page: Annotated[
        Optional[int], typer.Option(help="Number of entries per page")
    ] = None,
    since: Annotated[
        Optional[datetime],
        typer.Option(help="Get entries created after this timestamp"),
    ] = None,
    read: Annotated[Optional[bool], typer.Option(help="Filter by read status")] = None,
    starred: Annotated[
        Optional[bool], typer.Option(help="Filter by starred status")
    ] = None,
    mode: Annotated[Optional[str], typer.Option(help="Mode (e.g. extended)")] = None,
    include_original: Annotated[
        bool, typer.Option(help="Include original entry data")
    ] = False,
    include_enclosure: Annotated[
        bool, typer.Option(help="Include enclosure data")
    ] = False,
    include_content_diff: Annotated[
        bool, typer.Option(help="Include content diff")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List entries for a specific feed."""
    params = _build_entry_params(
        page,
        per_page,
        since,
        read,
        starred,
        mode,
        include_original,
        include_enclosure,
        include_content_diff,
    )
    fetch_and_display_entries(
        ctx,
        f"https://api.feedbin.com/v2/feeds/{feed_id}/entries.json",
        params,
        json_output,
    )


@entries_app.command(name="show")
def show_entry(
    ctx: typer.Context,
    entry_id: Annotated[int, typer.Argument(help="Entry ID")],
    mode: Annotated[Optional[str], typer.Option(help="Mode (e.g. extended)")] = None,
    include_original: Annotated[
        bool, typer.Option(help="Include original entry data")
    ] = False,
    include_enclosure: Annotated[
        bool, typer.Option(help="Include enclosure data")
    ] = False,
    include_content_diff: Annotated[
        bool, typer.Option(help="Include content diff")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Show a single entry."""
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = f"https://api.feedbin.com/v2/entries/{entry_id}.json"
    params = {}
    if mode is not None:
        params["mode"] = mode
    if include_original:
        params["include_original"] = "true"
    if include_enclosure:
        params["include_enclosure"] = "true"
    if include_content_diff:
        params["include_content_diff"] = "true"

    try:
        with get_client() as client:
            response = client.get(
                url,
                params=params,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code != 200:
                typer.secho(f"Error fetching entry: {response.status_code}", err=True)
                if response.status_code == 404:
                    typer.secho("Entry not found.", err=True)
                elif response.status_code == 403:
                    typer.secho(
                        "Forbidden. You may not have access to this entry.", err=True
                    )
                raise typer.Exit(1)

            entry = response.json()
            if json_output:
                typer.secho(json.dumps(entry, indent=2))
            else:
                typer.secho(f"Title: {entry.get('title')}")
                typer.secho(f"ID: {entry.get('id')}")
                typer.secho(f"Published: {entry.get('published')}")
                typer.secho(f"URL: {entry.get('url')}")
                if mode == "extended":
                    typer.secho(f"Author: {entry.get('author')}")
                    typer.secho(f"Summary: {entry.get('summary')}")

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
