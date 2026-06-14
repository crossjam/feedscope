import typer
import httpx
from typing_extensions import Annotated
import json
from loguru import logger

from .config import get_config
from .client import get_client
from .state import get_state

subscriptions_app = typer.Typer(
    help="Manage feed subscriptions", invoke_without_command=True
)


@subscriptions_app.callback()
def subscriptions(ctx: typer.Context):
    """
    Manage feed subscriptions.
    """
    get_state(ctx)
    if ctx.invoked_subcommand is None:
        typer.secho(ctx.get_help())
        raise typer.Exit()


@subscriptions_app.command(name="list", help="List all feed subscriptions.")
def list_subscriptions(
    ctx: typer.Context,
    limit: Annotated[
        int | None,
        typer.Option(
            "--limit",
            "-l",
            help="Limit the number of subscriptions returned.",
            min=1,
        ),
    ] = None,
    extended: Annotated[
        bool,
        typer.Option(
            "--extended",
            "-e",
            help="Include extended metadata for the feed.",
        ),
    ] = False,
    jsonl: Annotated[
        bool,
        typer.Option(
            "--jsonl",
            help="Output the subscriptions in JSONL format.",
        ),
    ] = False,
) -> None:
    """Retrieves and lists all feed subscriptions from Feedbin."""
    state = get_state(ctx)
    logger.debug("Listing subscriptions with log config {}", state.log_config_path)
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
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
            typer.secho(f"Retrieving: {response.request.url}", err=True)
            if response.status_code != 200:
                if response.status_code == 401:
                    typer.secho(
                        "❌ Authentication failed. Please run `feedscope auth login` again.",
                        fg=typer.colors.RED,
                    )
                else:
                    typer.secho(
                        f"❌ Unexpected response: {response.status_code}",
                        fg=typer.colors.RED,
                    )
                raise typer.Exit(1)

            all_subscriptions = response.json()

        if not all_subscriptions:
            if not jsonl:
                typer.secho("No subscriptions found.")
            return

        if limit:
            all_subscriptions = all_subscriptions[:limit]

        if jsonl:
            for sub in all_subscriptions:
                typer.secho(json.dumps(sub))
        elif extended:
            for sub in all_subscriptions:
                typer.secho(json.dumps(sub, indent=2))
        else:
            for sub in all_subscriptions:
                typer.secho(f"[{sub['id']}] {sub['title']} - {sub['feed_url']}")

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@subscriptions_app.command(name="get", help="Get one or more subscriptions by ID.")
def get_subscriptions(
    ctx: typer.Context,
    subscription_ids: Annotated[
        list[int], typer.Argument(help="The IDs of the subscriptions to get.")
    ],
    extended: Annotated[
        bool,
        typer.Option(
            "--extended",
            "-e",
            help="Include extended metadata for the feed.",
        ),
    ] = False,
) -> None:
    """Retrieves one or more feed subscriptions from Feedbin."""
    state = get_state(ctx)
    logger.debug("Fetching subscriptions with log config {}", state.log_config_path)
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    try:
        with get_client() as client:
            for subscription_id in subscription_ids:
                url = f"https://api.feedbin.com/v2/subscriptions/{subscription_id}.json"
                if extended:
                    url += "?mode=extended"

                response = client.get(
                    url,
                    auth=(config.auth.email, config.auth.password),
                )
                typer.secho(f"Retrieving: {response.request.url}", err=True)

                if response.status_code != 200:
                    if response.status_code == 401:
                        typer.secho(
                            "❌ Authentication failed. Please run `feedscope auth login` again.",
                            fg=typer.colors.RED,
                        )
                        raise typer.Exit(1)
                    elif response.status_code == 403:
                        typer.secho(
                            f"⚠️ Forbidden: You may not own subscription with ID {subscription_id}. Skipping.",
                            fg=typer.colors.YELLOW,
                            err=True,
                        )
                    else:
                        typer.secho(
                            f"⚠️ Unexpected response for subscription ID {subscription_id}: {response.status_code}. Skipping.",
                            fg=typer.colors.YELLOW,
                            err=True,
                        )
                    continue

                subscription = response.json()
                typer.secho(json.dumps(subscription, indent=2))

    except httpx.RequestError as e:
        typer.secho(f"❌ Network error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


@subscriptions_app.command(name="create", help="Create a new subscription.")
def create_subscription(
    ctx: typer.Context,
    feed_url: Annotated[
        str, typer.Argument(help="The URL of the feed to subscribe to.")
    ],
) -> None:
    """Creates a new feed subscription in Feedbin."""
    state = get_state(ctx)
    logger.debug("Creating subscription with log config {}", state.log_config_path)
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
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
                typer.secho(status_message, fg=typer.colors.GREEN)
                typer.secho(json.dumps(response.json(), indent=2))
            elif response.status_code == 300:
                typer.secho(
                    "⚠️ Multiple feeds found. Please use the exact feed_url from the options below:",
                    fg=typer.colors.YELLOW,
                )
                typer.secho(json.dumps(response.json(), indent=2))
            elif response.status_code == 404:
                typer.secho(
                    f"❌ No feed found at the specified URL: {feed_url}",
                    fg=typer.colors.RED,
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


@subscriptions_app.command(name="update", help="Update a subscription's title.")
def update_subscription(
    ctx: typer.Context,
    subscription_id: Annotated[
        int, typer.Argument(help="The ID of the subscription to update.")
    ],
    title: Annotated[str, typer.Argument(help="The new title for the subscription.")],
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output the updated subscription as JSON.",
        ),
    ] = False,
) -> None:
    """Updates a subscription's title in Feedbin."""
    state = get_state(ctx)
    logger.debug("Updating subscription with log config {}", state.log_config_path)
    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
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
                if not json_output:
                    typer.secho("✅ Subscription updated successfully.")
                typer.secho(json.dumps(response.json(), indent=2))
            elif response.status_code == 403:
                typer.secho(
                    f"❌ Forbidden: You may not own the subscription with ID {subscription_id}.",
                    fg=typer.colors.RED,
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


@subscriptions_app.command(name="delete", help="Delete a subscription.")
def delete_subscription(
    ctx: typer.Context,
    subscription_id: Annotated[
        int, typer.Argument(help="The ID of the subscription to delete.")
    ],
) -> None:
    """Deletes a feed subscription from Feedbin."""
    state = get_state(ctx)
    logger.debug("Deleting subscription with log config {}", state.log_config_path)
    if not typer.confirm(
        f"Are you sure you want to delete subscription {subscription_id}?"
    ):
        raise typer.Abort()

    config = get_config()

    if not config.auth.email or not config.auth.password:
        typer.secho(
            "❌ Authentication credentials not found. Please run `feedscope auth login` first.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    url = f"https://api.feedbin.com/v2/subscriptions/{subscription_id}.json"

    try:
        with get_client() as client:
            response = client.delete(
                url, auth=(config.auth.email, config.auth.password)
            )

            if response.status_code == 204:
                typer.secho(
                    f"✅ Subscription {subscription_id} deleted successfully.",
                    fg=typer.colors.GREEN,
                )
            elif response.status_code == 403:
                typer.secho(
                    f"❌ Forbidden: You may not own the subscription with ID {subscription_id}.",
                    fg=typer.colors.RED,
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
