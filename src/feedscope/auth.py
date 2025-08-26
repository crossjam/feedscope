import typer
import httpx
from typing_extensions import Annotated
from rich.prompt import Prompt
import tomlkit

from .config import get_config
from .client import get_client

auth_app = typer.Typer(help="Authentication commands")


@auth_app.command()
def login(
    email: Annotated[str, typer.Argument(help="Feedbin email address")],
    password: Annotated[str, typer.Option("--password", "-p", help="Feedbin password", hide_input=True)] = None,
) -> None:
    """Check authentication credentials with Feedbin API."""

    # Load existing config
    config = get_config()

    # Prompt for password if not provided
    if password is None:
        password = Prompt.ask("Enter your Feedbin password", password=True)

    url = "https://api.feedbin.com/v2/authentication.json"

    try:
        with get_client() as client:
            response = client.get(url, auth=(email, password))

        if response.status_code == 200:
            typer.echo("✅ Authentication successful!", color=typer.colors.GREEN)

            # Update and save credentials to config file
            config.email = email
            config.password = password
            config.save()
            typer.echo(
                f"💾 Credentials saved to {config.config_file_path}",
                color=typer.colors.BLUE,
            )

        elif response.status_code == 401:
            typer.echo(
                "❌ Authentication failed - invalid credentials", color=typer.colors.RED
            )
            raise typer.Exit(1)
        else:
            typer.echo(
                f"❌ Unexpected response: {response.status_code}", color=typer.colors.RED
            )
            raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@auth_app.command()
def status() -> None:
    """Check authentication status."""
    config = get_config()

    if not config.email or not config.password:
        typer.echo(
            "❌ No credentials stored. Please run `feedscope auth login`.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    typer.echo(
        f"ℹ️  Credentials for {config.email} found in config file.",
        color=typer.colors.BLUE,
    )
    typer.echo("Verifying credentials with Feedbin API...")

    url = "https://api.feedbin.com/v2/authentication.json"
    try:
        with get_client() as client:
            response = client.get(url, auth=(config.email, config.password))

        if response.status_code == 200:
            typer.echo("✅ Authentication successful!", color=typer.colors.GREEN)
        elif response.status_code == 401:
            typer.echo(
                "❌ Authentication failed - invalid credentials.", color=typer.colors.RED
            )
            typer.echo(
                "Please run `feedscope auth login` to update your credentials.",
                color=typer.colors.YELLOW,
            )
            raise typer.Exit(1)
        else:
            typer.echo(
                f"❌ Unexpected response: {response.status_code}", color=typer.colors.RED
            )
            raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@auth_app.command()
def remove() -> None:
    """Remove stored authentication credentials."""
    config = get_config()
    config_file = config.config_file_path

    if not config_file.exists():
        typer.echo("❌ No configuration file found", color=typer.colors.RED)
        raise typer.Exit(1)

    # Load existing TOML
    doc = tomlkit.parse(config_file.read_text())

    # Remove auth section if it exists
    if "auth" in doc:
        del doc["auth"]
        config_file.write_text(tomlkit.dumps(doc))
        typer.echo("✅ Authentication credentials removed", color=typer.colors.GREEN)
    else:
        typer.echo("❌ No authentication credentials found", color=typer.colors.RED)
        raise typer.Exit(1)
