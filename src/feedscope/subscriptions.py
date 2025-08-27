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
            typer.echo(f"Retrieving: {response.request.url}", err=True)
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
            typer.echo(f"Retrieving: {response.request.url}", err=True)

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


@subscriptions_app.command(name="create", help="Create a new subscription.")
def create_subscription(
    feed_url: Annotated[str, typer.Argument(help="The URL of the feed to subscribe to.")]
) -> None:
    """Creates a new feed subscription in Feedbin."""
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = "https://api.feedbin.com/v2/subscriptions.json"
    data = {"feed_url": feed_url}

    try:
        with get_client() as client:
            response = client.post(
                url, json=data, auth=(config.auth.email, config.auth.password)
            )

            if response.status_code in [201, 302]:
                status_message = (
                    "✅ Subscription created successfully."
                    if response.status_code == 201
                    else "ℹ️ Subscription already exists."
                )
                typer.echo(status_message, color=typer.colors.GREEN)
                typer.echo(json.dumps(response.json(), indent=2))
            elif response.status_code == 300:
                typer.echo(
                    "⚠️ Multiple feeds found. Please use the exact feed_url from the options below:",
                    color=typer.colors.YELLOW,
                )
                typer.echo(json.dumps(response.json(), indent=2))
            elif response.status_code == 404:
                typer.echo(
                    f"❌ No feed found at the specified URL: {feed_url}",
                    color=typer.colors.RED,
                )
                raise typer.Exit(1)
            else:
                typer.echo(
                    f"❌ Unexpected response: {response.status_code}",
                    color=typer.colors.RED,
                )
                raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@subscriptions_app.command(name="update", help="Update a subscription's title.")
def update_subscription(
    subscription_id: Annotated[
        int, typer.Argument(help="The ID of the subscription to update.")
    ],
    title: Annotated[
        str,
        typer.Option(
            "--title", "-t", help="The new title for the subscription.", prompt=True
        ),
    ],
) -> None:
    """Updates a subscription's title in Feedbin."""
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = f"https://api.feedbin.com/v2/subscriptions/{subscription_id}.json"
    data = {"title": title}

    try:
        with get_client() as client:
            response = client.patch(
                url, json=data, auth=(config.auth.email, config.auth.password)
            )

            if response.status_code == 200:
                typer.echo("✅ Subscription updated successfully.")
                typer.echo(json.dumps(response.json(), indent=2))
            elif response.status_code == 403:
                typer.echo(
                    f"❌ Forbidden: You may not own the subscription with ID {subscription_id}.",
                    color=typer.colors.RED,
                )
                raise typer.Exit(1)
            else:
                typer.echo(
                    f"❌ Unexpected response: {response.status_code}",
                    color=typer.colors.RED,
                )
                raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)


@subscriptions_app.command(name="delete", help="Delete a subscription.")
def delete_subscription(
    subscription_id: Annotated[
        int, typer.Argument(help="The ID of the subscription to delete.")
    ]
) -> None:
    """Deletes a feed subscription from Feedbin."""
    if not typer.confirm(
        f"Are you sure you want to delete subscription {subscription_id}?"
    ):
        raise typer.Abort()

    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.echo(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            color=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = f"https://api.feedbin.com/v2/subscriptions/{subscription_id}.json"

    try:
        with get_client() as client:
            response = client.delete(
                url, auth=(config.auth.email, config.auth.password)
            )

            if response.status_code == 204:
                typer.echo(
                    f"✅ Subscription {subscription_id} deleted successfully.",
                    color=typer.colors.GREEN,
                )
            elif response.status_code == 403:
                typer.echo(
                    f"❌ Forbidden: You may not own the subscription with ID {subscription_id}.",
                    color=typer.colors.RED,
                )
                raise typer.Exit(1)
            else:
                typer.echo(
                    f"❌ Unexpected response: {response.status_code}",
                    color=typer.colors.RED,
                )
                raise typer.Exit(1)

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)
