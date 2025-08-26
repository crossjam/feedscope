import typer
import httpx

from .config import get_config
from .client import get_client

subscriptions_app = typer.Typer(help="Manage feed subscriptions")

@subscriptions_app.command(name="list", help="List all feed subscriptions.")
def list_subscriptions() -> None:
    """Retrieves and lists all feed subscriptions from Feedbin."""
    config = get_config()

    if not config.email or not config.password:
        typer.echo("❌ Authentication credentials not found. Please run `feedscope auth login` first.", color=typer.colors.RED)
        raise typer.Exit(1)

    url = "https://api.feedbin.com/v2/subscriptions.json"

    try:
        with get_client() as client:
            response = client.get(url, auth=(config.email, config.password))

        if response.status_code == 200:
            subscriptions = response.json()
            if not subscriptions:
                typer.echo("No subscriptions found.")
                return

            for sub in subscriptions:
                typer.echo(f"[{sub['id']}] {sub['title']} - {sub['feed_url']}")

        elif response.status_code == 401:
            typer.echo("❌ Authentication failed. Please run `feedscope auth login` again.", color=typer.colors.RED)
            raise typer.Exit(1)
        else:
            typer.echo(f"❌ Unexpected response: {response.status_code}", color=typer.colors.RED)
            raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)
