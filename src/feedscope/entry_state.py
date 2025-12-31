import typer
from .state import get_state

unread_app = typer.Typer(help="Manage unread entries")
starred_app = typer.Typer(help="Manage starred entries")
updated_app = typer.Typer(help="Manage updated entries")
recently_read_app = typer.Typer(help="Manage recently read entries")

@unread_app.callback()
def unread(ctx: typer.Context):
    """Manage unread entries."""
    get_state(ctx)

@starred_app.callback()
def starred(ctx: typer.Context):
    """Manage starred entries."""
    get_state(ctx)

@updated_app.callback()
def updated(ctx: typer.Context):
    """Manage updated entries."""
    get_state(ctx)

@recently_read_app.callback()
def recently_read(ctx: typer.Context):
    """Manage recently read entries."""
    get_state(ctx)
