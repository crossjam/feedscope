import typer
import httpx
from typing_extensions import Annotated
from rich.progress import Progress
import json

from .config import get_config
from .client import get_client

subscriptions_app = typer.Typer(help="Manage feed subscriptions", invoke_without_command=True)


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
) -> None:
    """Retrieves and lists all feed subscriptions from Feedbin."""
    config = get_config()

    if not config.email or not config.password:
        typer.echo("❌ Authentication credentials not found. Please run `feedscope auth login` first.", color=typer.colors.RED)
        raise typer.Exit(1)

    url = "https://api.feedbin.com/v2/subscriptions.json"
    all_subscriptions = []

    try:
        with get_client() as client, Progress() as progress:
            task_id = None
            while url:
                response = client.get(url, auth=(config.email, config.password))

                if response.status_code != 200:
                    if response.status_code == 401:
                        typer.echo("❌ Authentication failed. Please run `feedscope auth login` again.", color=typer.colors.RED)
                    else:
                        typer.echo(f"❌ Unexpected response: {response.status_code}", color=typer.colors.RED)
                    raise typer.Exit(1)

                if task_id is None and not jsonl:
                    total_records_str = response.headers.get("X-Feedbin-Record-Count")
                    if total_records_str:
                        total = int(total_records_str)
                        if limit:
                            total = min(total, limit)
                        task_id = progress.add_task("[cyan]Downloading...", total=total)

                page_subscriptions = response.json()
                if not page_subscriptions:
                    break

                all_subscriptions.extend(page_subscriptions)
                if task_id is not None:
                    progress.update(task_id, completed=min(len(all_subscriptions), progress.tasks[0].total))

                if limit and len(all_subscriptions) >= limit:
                    break

                # Check for next page link
                if "next" in response.links:
                    url = response.links["next"]["url"]
                else:
                    url = None

        if not all_subscriptions:
            if not jsonl:
                typer.echo("No subscriptions found.")
            return

        if limit:
            all_subscriptions = all_subscriptions[:limit]

        if jsonl:
            for sub in all_subscriptions:
                typer.echo(json.dumps(sub))
        else:
            for sub in all_subscriptions:
                typer.echo(f"[{sub['id']}] {sub['title']} - {sub['feed_url']}")

    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)
