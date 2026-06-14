import typer
from typing_extensions import Annotated
import json
import httpx

from .config import get_config
from .client import get_client

tags_app = typer.Typer(help="Manage tags")
taggings_app = typer.Typer(help="Manage taggings")


def _check_auth():
    config = get_config()
    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    return config


# Tags commands
@tags_app.command(name="rename")
def rename_tag(
    ctx: typer.Context,
    old_name: Annotated[str, typer.Option(help="Old tag name")],
    new_name: Annotated[str, typer.Option(help="New tag name")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Rename a tag."""
    config = _check_auth()
    url = "https://api.feedbin.com/v2/tags.json"
    data = {"old_name": old_name, "new_name": new_name}

    try:
        with get_client() as client:
            response = client.post(
                url,
                json=data,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 200:
                typer.secho("✅ Tag renamed successfully.", fg=typer.colors.GREEN)
                if json_output:
                    typer.secho(json.dumps(response.json(), indent=2))
            else:
                typer.secho(f"Error renaming tag: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@tags_app.command(name="delete")
def delete_tag(
    ctx: typer.Context,
    name: Annotated[str, typer.Option(help="Tag name to delete")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Delete a tag."""
    config = _check_auth()

    if not typer.confirm(f"Are you sure you want to delete tag '{name}'?"):
        raise typer.Abort()

    url = "https://api.feedbin.com/v2/tags.json"
    data = {"name": name}

    try:
        with get_client() as client:
            # DELETE with body
            response = client.request(
                "DELETE",
                url,
                json=data,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 200:
                typer.secho("✅ Tag deleted successfully.", fg=typer.colors.GREEN)
                if json_output:
                    typer.secho(json.dumps(response.json(), indent=2))
            else:
                typer.secho(f"Error deleting tag: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


# Taggings commands
@taggings_app.command(name="list")
def list_taggings(
    ctx: typer.Context,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List all taggings."""
    config = _check_auth()
    url = "https://api.feedbin.com/v2/taggings.json"

    try:
        with get_client() as client:
            response = client.get(
                url,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 200:
                taggings = response.json()
                if json_output:
                    typer.secho(json.dumps(taggings, indent=2))
                else:
                    for tagging in taggings:
                        typer.secho(
                            f"[{tagging['id']}] Feed {tagging['feed_id']} -> {tagging['name']}"
                        )
            else:
                typer.secho(f"Error fetching taggings: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@taggings_app.command(name="create")
def create_tagging(
    ctx: typer.Context,
    feed_id: Annotated[int, typer.Option(help="Feed ID")],
    name: Annotated[str, typer.Option(help="Tag name")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Create a new tagging."""
    config = _check_auth()
    url = "https://api.feedbin.com/v2/taggings.json"
    data = {"feed_id": feed_id, "name": name}

    try:
        with get_client() as client:
            response = client.post(
                url,
                json=data,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 201:
                typer.secho("✅ Tagging created successfully.", fg=typer.colors.GREEN)
                if json_output:
                    typer.secho(json.dumps(response.json(), indent=2))
            elif response.status_code == 302:
                typer.secho("ℹ️ Tagging already exists.", fg=typer.colors.YELLOW)
            else:
                typer.secho(f"Error creating tagging: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@taggings_app.command(name="delete")
def delete_tagging(
    ctx: typer.Context,
    tagging_id: Annotated[int, typer.Argument(help="Tagging ID")],
):
    """Delete a tagging."""
    config = _check_auth()

    if not typer.confirm(f"Are you sure you want to delete tagging {tagging_id}?"):
        raise typer.Abort()

    url = f"https://api.feedbin.com/v2/taggings/{tagging_id}.json"

    try:
        with get_client() as client:
            response = client.delete(
                url,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 204:
                typer.secho("✅ Tagging deleted successfully.", fg=typer.colors.GREEN)
            elif response.status_code == 403:
                typer.secho("Forbidden. You may not own this tagging.", err=True)
                raise typer.Exit(1)
            else:
                typer.secho(f"Error deleting tagging: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
