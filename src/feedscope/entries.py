import typer
from typing import Optional
from typing_extensions import Annotated
from datetime import datetime
import json
from loguru import logger
import httpx

from .state import get_state
from .config import get_config
from .client import get_client

entries_app = typer.Typer(help="Retrieve and manage entries")

def _fetch_entries(
    ctx: typer.Context,
    url: str,
    page: Optional[int],
    per_page: Optional[int],
    since: Optional[datetime],
    read: Optional[bool],
    starred: Optional[bool],
    mode: Optional[str],
    include_original: bool,
    include_enclosure: bool,
    include_content_diff: bool,
    json_output: bool,
):
    state = get_state(ctx)
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    params = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if since is not None:
        # Format as ISO 8601 string
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

    logger.debug("Fetching entries from {} with params {}", url, params)

    try:
        with get_client() as client:
            response = client.get(
                url,
                params=params,
                auth=(config.auth.email, config.auth.password),
            )
            
            if response.status_code != 200:
                typer.echo(f"Error fetching entries: {response.status_code}", err=True)
                if response.status_code == 403:
                    typer.echo("Forbidden. Check if you have access.", err=True)
                elif response.status_code == 404:
                    typer.echo("Not found.", err=True)
                raise typer.Exit(1)

            entries = response.json()
            
            if json_output:
                typer.echo(json.dumps(entries, indent=2))
            else:
                for entry in entries:
                    title = entry.get("title") or "(No Title)"
                    entry_id = entry.get("id")
                    published = entry.get("published")
                    typer.echo(f"[{entry_id}] {published} - {title}")

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@entries_app.command(name="list")
def list_entries(
    ctx: typer.Context,
    page: Annotated[Optional[int], typer.Option(help="Page number")] = None,
    per_page: Annotated[Optional[int], typer.Option(help="Number of entries per page")] = None,
    since: Annotated[Optional[datetime], typer.Option(help="Get entries created after this timestamp")] = None,
    read: Annotated[Optional[bool], typer.Option(help="Filter by read status")] = None,
    starred: Annotated[Optional[bool], typer.Option(help="Filter by starred status")] = None,
    mode: Annotated[Optional[str], typer.Option(help="Mode (e.g. extended)")] = None,
    include_original: Annotated[bool, typer.Option(help="Include original entry data")] = False,
    include_enclosure: Annotated[bool, typer.Option(help="Include enclosure data")] = False,
    include_content_diff: Annotated[bool, typer.Option(help="Include content diff")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
):
    """List entries."""
    _fetch_entries(
        ctx,
        "https://api.feedbin.com/v2/entries.json",
        page, per_page, since, read, starred, mode,
        include_original, include_enclosure, include_content_diff,
        json_output
    )

@entries_app.command(name="feed")
def feed_entries(
    ctx: typer.Context,
    feed_id: Annotated[int, typer.Argument(help="Feed ID")],
    page: Annotated[Optional[int], typer.Option(help="Page number")] = None,
    per_page: Annotated[Optional[int], typer.Option(help="Number of entries per page")] = None,
    since: Annotated[Optional[datetime], typer.Option(help="Get entries created after this timestamp")] = None,
    read: Annotated[Optional[bool], typer.Option(help="Filter by read status")] = None,
    starred: Annotated[Optional[bool], typer.Option(help="Filter by starred status")] = None,
    mode: Annotated[Optional[str], typer.Option(help="Mode (e.g. extended)")] = None,
    include_original: Annotated[bool, typer.Option(help="Include original entry data")] = False,
    include_enclosure: Annotated[bool, typer.Option(help="Include enclosure data")] = False,
    include_content_diff: Annotated[bool, typer.Option(help="Include content diff")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False,
):
    """List entries for a specific feed."""
    _fetch_entries(
        ctx,
        f"https://api.feedbin.com/v2/feeds/{feed_id}/entries.json",
        page, per_page, since, read, starred, mode,
        include_original, include_enclosure, include_content_diff,
        json_output
    )

@entries_app.command(name="show")
def show_entry(
    ctx: typer.Context,
    entry_id: Annotated[int, typer.Argument(help="Entry ID")],
    mode: Annotated[Optional[str], typer.Option(help="Mode (e.g. extended)")] = None,
    include_original: Annotated[bool, typer.Option(help="Include original entry data")] = False,
    include_enclosure: Annotated[bool, typer.Option(help="Include enclosure data")] = False,
    include_content_diff: Annotated[bool, typer.Option(help="Include content diff")] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output raw JSON")] = False, # Usually show is JSON?
):
    """Show a single entry."""
    # show command doesn't support pagination or filters like read/starred/since
    # but supports mode and include_*
    
    state = get_state(ctx)
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
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
                typer.echo(f"Error fetching entry: {response.status_code}", err=True)
                if response.status_code == 404:
                    typer.echo("Entry not found.", err=True)
                elif response.status_code == 403:
                    typer.echo("Forbidden. You may not have access to this entry.", err=True)
                raise typer.Exit(1)
                
            entry = response.json()
            if json_output:
                typer.echo(json.dumps(entry, indent=2))
            else:
                # Basic pretty print
                typer.echo(f"Title: {entry.get('title')}")
                typer.echo(f"ID: {entry.get('id')}")
                typer.echo(f"Published: {entry.get('published')}")
                typer.echo(f"URL: {entry.get('url')}")
                if mode == "extended":
                    typer.echo(f"Author: {entry.get('author')}")
                    typer.echo(f"Summary: {entry.get('summary')}")
                
                # We could print content but it's HTML, maybe truncated?
                # User likely wants JSON or use jq.
                
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)