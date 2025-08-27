import typer
import httpx
from typing_extensions import Annotated
import json

from .config import get_config
from .client import get_client

subscriptions_app = typer.Typer(
    help="Manage feed subscriptions", invoke_without_command=True
)


@subscriptions_app.callback()
def subscriptions(ctx: typer.Context):
    """
    Manage feed subscriptions.
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@subscriptions_app.command(name="list", help="List all feed subscriptions.")
def list_subscriptions(
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-l",
            help="Limit the number of subscriptions returned.",
            min=1,
        ),
    ] = None,
    jsonl: Annotated[
        bool,
        typer.Option(
            "--jsonl",
            help="Output the subscriptions in JSONL format.",
            is_flag=True,
        ),
    ] = False,
    extended: Annotated[
        bool,
        typer.Option(
            "--extended",
            "-e",
            help="Include extended metadata for the feed.",
            is_flag=True,
        ),
    ] = False,
) -> None:
    """Retrieves and lists all feed subscriptions from Feedbin."""
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = "https://api.feedbin.com/v2/subscriptions.json"
    if extended:
        url += "?mode=extended"

    try:
        with get_client() as client:
            response = client.get(
                url,
                auth=(config.auth.email, config.auth.password),
            )
            if response.status_code != 200:
                if response.status_code == 401:
                    typer.echo(
                        "❌ Authentication failed. Please run `feedscope auth login` again.",
                        color=typer.colors.RED,
                    )
                else:
                    typer.echo(
                        f"❌ Unexpected response: {response.status_code}",
                        color=typer.colors.RED,
                    )
                raise typer.Exit(1)

            all_subscriptions = response.json()

        if not all_subscriptions:
            if not jsonl:
                typer.echo("No subscriptions found.")
            return

        if limit:
            all_subscriptions = all_subscriptions[:limit]

        if jsonl:
            for sub in all_subscriptions:
                typer.echo(json.dumps(sub))
        elif extended:
            for sub in all_subscriptions:
                typer.echo(json.dumps(sub, indent=2))
        else:
            for sub in all_subscriptions:
                typer.echo(f"[{sub['id']}] {sub['title']} - {sub['feed_url']}")

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@subscriptions_app.command(name="get", help="Get a single subscription by ID.")
def get_subscription(
    subscription_id: Annotated[
        int, typer.Argument(help="The ID of the subscription to get.")
    ],
    extended: Annotated[
        bool,
        typer.Option(
            "--extended",
            "-e",
            help="Include extended metadata for the feed.",
            is_flag=True,
        ),
    ] = False,
) -> None:
    """Retrieves a single feed subscription from Feedbin."""
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = f"https://api.feedbin.com/v2/subscriptions/{subscription_id}.json"
    if extended:
        url += "?mode=extended"

    try:
        with get_client() as client:
            response = client.get(
                url,
                auth=(config.auth.email, config.auth.password),
            )

            if response.status_code != 200:
                if response.status_code == 401:
                    typer.echo(
                        "❌ Authentication failed. Please run `feedscope auth login` again.",
                        color=typer.colors.RED,
                    )
                elif response.status_code == 403:
                    typer.echo(
                        f"❌ Forbidden: You may not own the subscription with ID {subscription_id}.",
                        color=typer.colors.RED,
                    )
                else:
                    typer.echo(
                        f"❌ Unexpected response: {response.status_code}",
                        color=typer.colors.RED,
                    )
                raise typer.Exit(1)

            subscription = response.json()
            typer.echo(json.dumps(subscription, indent=2))

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)
