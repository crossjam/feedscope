import typer
from typing_extensions import Annotated
import json
import httpx
from pathlib import Path
import hmac
import hashlib
import base64

from .config import get_config
from .client import get_client

imports_app = typer.Typer(help="Manage imports")
pages_app = typer.Typer(help="Manage pages")
icons_app = typer.Typer(help="Manage icons")


def _check_auth():
    config = get_config()
    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)
    return config


# Imports
@imports_app.command(name="list")
def list_imports(
    ctx: typer.Context,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List imports."""
    config = _check_auth()
    url = "https://api.feedbin.com/v2/imports.json"

    try:
        with get_client() as client:
            response = client.get(url, auth=(config.auth.email, config.auth.password))
            if response.status_code == 200:
                imports = response.json()
                if json_output:
                    typer.echo(json.dumps(imports, indent=2))
                else:
                    for imp in imports:
                        typer.echo(
                            f"ID: {imp['id']}, Complete: {imp['complete']}, Created: {imp['created_at']}"
                        )
            else:
                typer.echo(f"Error: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@imports_app.command(name="status")
def import_status(
    ctx: typer.Context,
    import_id: Annotated[int, typer.Argument(help="Import ID")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Get status of an import."""
    config = _check_auth()
    url = f"https://api.feedbin.com/v2/imports/{import_id}.json"

    try:
        with get_client() as client:
            response = client.get(url, auth=(config.auth.email, config.auth.password))
            if response.status_code == 200:
                imp = response.json()
                if json_output:
                    typer.echo(json.dumps(imp, indent=2))
                else:
                    typer.echo(
                        f"Import {imp['id']} Status: {'Complete' if imp['complete'] else 'Pending'}"
                    )
                    if "import_items" in imp:
                        for item in imp["import_items"]:
                            typer.echo(f" - {item['title']}: {item['status']}")
            else:
                typer.echo(f"Error: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@imports_app.command(name="create")
def create_import(
    ctx: typer.Context,
    file_path: Annotated[
        Path, typer.Argument(help="Path to OPML file", exists=True, readable=True)
    ],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Create a new import from OPML file."""
    config = _check_auth()
    url = "https://api.feedbin.com/v2/imports.json"

    content = file_path.read_text(encoding="utf-8")  # OPML is XML, usually text

    try:
        with get_client() as client:
            # POST body as text/xml
            response = client.post(
                url,
                content=content,
                headers={"Content-Type": "text/xml"},
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code == 201:
                imp = response.json()
                typer.echo("✅ Import created.", color=typer.colors.GREEN)
                if json_output:
                    typer.echo(json.dumps(imp, indent=2))
                else:
                    typer.echo(f"ID: {imp['id']}")
            else:
                typer.echo(f"Error: {response.status_code}", err=True)
                if json_output:
                    typer.echo(response.text)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


# Pages
@pages_app.command(name="save")
def save_page(
    ctx: typer.Context,
    url: Annotated[str, typer.Option(help="URL to save")],
    title: Annotated[str, typer.Option(help="Title of the page")] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Save a web page as an entry."""
    config = _check_auth()
    api_url = "https://api.feedbin.com/v2/pages.json"
    data = {"url": url}
    if title:
        data["title"] = title

    try:
        with get_client() as client:
            response = client.post(
                api_url, json=data, auth=(config.auth.email, config.auth.password)
            )

            if response.status_code == 200:  # Docs say 200 return entry
                entry = response.json()
                typer.echo("✅ Page saved.", color=typer.colors.GREEN)
                if json_output:
                    typer.echo(json.dumps(entry, indent=2))
                else:
                    typer.echo(f"Created Entry ID: {entry.get('id')}")
            else:
                typer.echo(f"Error: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


# Icons
@icons_app.command(name="list")
def list_icons(
    ctx: typer.Context,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """List feed icons."""
    config = _check_auth()
    url = "https://api.feedbin.com/v2/icons.json"

    try:
        with get_client() as client:
            response = client.get(url, auth=(config.auth.email, config.auth.password))
            if response.status_code == 200:
                icons = response.json()
                if json_output:
                    typer.echo(json.dumps(icons, indent=2))
                else:
                    for icon in icons:
                        typer.echo(f"{icon['host']}: {icon['url']}")
            else:
                typer.echo(f"Error: {response.status_code}", err=True)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


# Extract
def extract_command(
    ctx: typer.Context,
    url: Annotated[str, typer.Argument(help="URL to extract content from")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output raw JSON")
    ] = False,
):
    """Extract content from a URL using Feedbin's service."""
    config = get_config()
    username = config.extract.username
    secret = config.extract.secret

    if not username or not secret:
        typer.echo(
            "❌ Extraction credentials not found in config (extract.username, extract.secret).",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    # HMAC-SHA1
    digest = hashlib.sha1
    signature = hmac.new(secret.encode(), url.encode(), digest).hexdigest()

    # Base64 URL safe
    base64_url = base64.urlsafe_b64encode(url.encode()).decode().replace("\n", "")

    api_url = f"https://extract.feedbin.com/parser/{username}/{signature}"
    params = {"base64_url": base64_url}

    try:
        with get_client() as client:
            response = client.get(api_url, params=params)

            if response.status_code == 200:
                data = response.json()
                if json_output:
                    typer.echo(json.dumps(data, indent=2))
                else:
                    typer.echo(f"Title: {data.get('title')}")
                    typer.echo(f"Word Count: {data.get('word_count')}")
                    typer.echo(f"Excerpt: {data.get('excerpt')}")
            else:
                typer.echo(f"Error extracting: {response.status_code}", err=True)
                if json_output:
                    typer.echo(response.text)
                raise typer.Exit(1)
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)
