import typer
from typing import Optional
from typing_extensions import Annotated
import json
import httpx

from .config import get_config
from .client import get_client
from .utils import fetch_and_display_entries

searches_app = typer.Typer(help="Manage saved searches")


@searches_app.command(name="list")
def list_searches(
    ctx: typer.Context,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List all saved searches."""
    config = get_config()
    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = "https://api.feedbin.com/v2/saved_searches.json"

    try:
        with get_client() as client:
            response = client.get(
                url,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code != 200:
                typer.secho(
                    f"Error fetching saved searches: {response.status_code}", err=True
                )
                raise typer.Exit(1)

            searches = response.json()

            if json_output:
                typer.secho(json.dumps(searches, indent=2))
            else:
                for search in searches:
                    typer.secho(
                        f"[{search['id']}] {search['name']} - Query: {search['query']}"
                    )

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@searches_app.command(name="get")
def get_search(
    ctx: typer.Context,
    search_id: Annotated[int, typer.Argument(help="Saved Search ID")],
    include_entries: Annotated[
        bool, typer.Option(help="Include full entry objects")
    ] = False,
    page: Annotated[Optional[int], typer.Option(help="Page number")] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Get results for a saved search."""
    params = {}
    if include_entries:
        params["include_entries"] = "true"
    if page:
        params["page"] = page

    fetch_and_display_entries(
        ctx,
        f"https://api.feedbin.com/v2/saved_searches/{search_id}.json",
        params,
        json_output,
    )


@searches_app.command(name="create")
def create_search(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Name of the saved search")],
    query: Annotated[str, typer.Option(help="Search query")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Create a new saved search."""
    config = get_config()
    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = "https://api.feedbin.com/v2/saved_searches.json"
    data = {"name": name, "query": query}

    try:
        with get_client() as client:
            response = client.post(
                url,
                json=data,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 201:
                typer.secho(
                    "✅ Saved search created successfully.", fg=typer.colors.GREEN
                )
                if json_output:
                    typer.secho(json.dumps(response.json(), indent=2))
            else:
                typer.secho(
                    f"Error creating saved search: {response.status_code}", err=True
                )
                if json_output:
                    typer.secho(response.text)
                raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@searches_app.command(name="update")
def update_search(
    ctx: typer.Context,
    search_id: Annotated[int, typer.Argument(help="Saved Search ID")],
    name: Annotated[Optional[str], typer.Option(help="New name")] = None,
    query: Annotated[Optional[str], typer.Option(help="New query")] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Update a saved search."""
    config = get_config()
    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = f"https://api.feedbin.com/v2/saved_searches/{search_id}.json"
    data = {}
    if name:
        data["name"] = name
    if query:
        data["query"] = query

    if not data:
        typer.secho("No updates provided.")
        return

    try:
        with get_client() as client:
            response = client.patch(
                url,
                json=data,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 200:
                typer.secho(
                    "✅ Saved search updated successfully.", fg=typer.colors.GREEN
                )
                if json_output:
                    typer.secho(json.dumps(response.json(), indent=2))
            elif response.status_code == 403:
                typer.secho("Forbidden. You may not own this saved search.", err=True)
                raise typer.Exit(1)
            else:
                typer.secho(
                    f"Error updating saved search: {response.status_code}", err=True
                )
                raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@searches_app.command(name="delete")
def delete_search(
    ctx: typer.Context,
    search_id: Annotated[int, typer.Argument(help="Saved Search ID")],
):
    """Delete a saved search."""
    config = get_config()
    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if not typer.confirm(f"Are you sure you want to delete saved search {search_id}?"):
        raise typer.Abort()

    url = f"https://api.feedbin.com/v2/saved_searches/{search_id}.json"

    try:
        with get_client() as client:
            response = client.delete(
                url,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 204:
                typer.secho(
                    "✅ Saved search deleted successfully.", fg=typer.colors.GREEN
                )
            elif response.status_code == 403:
                typer.secho("Forbidden. You may not own this saved search.", err=True)
                raise typer.Exit(1)
            else:
                typer.secho(
                    f"Error deleting saved search: {response.status_code}", err=True
                )
                raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
