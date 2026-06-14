import typer
import httpx
from typing_extensions import Annotated
from rich.prompt import Prompt
import tomlkit
from loguru import logger

from .config import get_config
from .client import get_client
from .state import get_state

auth_app = typer.Typer(help="Authentication commands")


@auth_app.command()
def login(
    ctx: typer.Context,
    email: Annotated[str, typer.Argument(help="Feedbin email address")],
    password: Annotated[
        str | None, typer.Option("--password", "-p", help="Feedbin password", hide_input=True)
    ] = None,
) -> None:
    """Check authentication credentials with Feedbin API."""

    # Load existing config
    state = get_state(ctx)
    logger.debug("Starting auth login with log config {}", state.log_config_path)
    config = get_config()

    # Prompt for password if not provided
    if password is None:
        password = Prompt.ask("Enter your Feedbin password", password=True)

    url = "https://api.feedbin.com/v2/authentication.json"

    try:
        with get_client() as client:
            response = client.get(url, auth=(email, password))

        if response.status_code == 200:
            typer.secho("✅ Authentication successful!", fg=typer.colors.GREEN)

            # Update and save credentials to config file
            config.auth.email = email
            config.auth.password = password
            config.save()
            typer.secho(
                f"💾 Credentials saved to {config.config_file_path}",
                fg=typer.colors.BLUE,
            )

        elif response.status_code == 401:
            typer.secho(
                "❌ Authentication failed - invalid credentials", fg=typer.colors.RED
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"❌ Unexpected response: {response.status_code}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@auth_app.command()
def status(ctx: typer.Context) -> None:
    """Check authentication status."""
    state = get_state(ctx)
    logger.debug("Checking auth status using log config {}", state.log_config_path)
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ No credentials stored. Please run `feedscope auth login`.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    typer.secho(
        f"ℹ️  Credentials for {config.auth.email} found in config file.",
        fg=typer.colors.BLUE,
    )
    typer.secho("Verifying credentials with Feedbin API...")

    url = "https://api.feedbin.com/v2/authentication.json"
    try:
        with get_client() as client:
            response = client.get(url, auth=(config.auth.email, config.auth.password))

        if response.status_code == 200:
            typer.secho("✅ Authentication successful!", fg=typer.colors.GREEN)
        elif response.status_code == 401:
            typer.secho(
                "❌ Authentication failed - invalid credentials.",
                fg=typer.colors.RED,
            )
            typer.secho(
                "Please run `feedscope auth login` to update your credentials.",
                fg=typer.colors.YELLOW,
            )
            raise typer.Exit(1)
        else:
            typer.secho(
                f"❌ Unexpected response: {response.status_code}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@auth_app.command()
def whoami(ctx: typer.Context) -> None:
    """Show the current user from the config file."""
    state = get_state(ctx)
    logger.debug(
        "Inspecting current auth user with log config {}", state.log_config_path
    )
    config = get_config()

    if config.auth.email and config.auth.password:
        typer.secho(f"User: {config.auth.email}")
        typer.secho(f"Password: {'*' * len(config.auth.password)}")
    else:
        typer.secho("No credentials stored.", fg=typer.colors.YELLOW)
        typer.secho("Run `feedscope auth login` to store credentials.")


@auth_app.command()
def remove(ctx: typer.Context) -> None:
    """Remove stored authentication credentials."""
    state = get_state(ctx)
    logger.debug(
        "Removing stored credentials with log config {}", state.log_config_path
    )
    config = get_config()
    config_file = config.config_file_path

    if not config_file.exists():
        typer.secho("❌ No configuration file found", fg=typer.colors.RED)
        raise typer.Exit(1)

    # Load existing TOML
    doc = tomlkit.parse(config_file.read_text())

    # Remove auth section if it exists
    if "auth" in doc:
        del doc["auth"]
        config_file.write_text(tomlkit.dumps(doc))
        typer.secho("✅ Authentication credentials removed", fg=typer.colors.GREEN)
    else:
        typer.secho("❌ No authentication credentials found", fg=typer.colors.RED)
        raise typer.Exit(1)
