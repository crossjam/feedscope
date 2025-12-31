import typer
from .state import get_state

tags_app = typer.Typer(help="Manage tags")
taggings_app = typer.Typer(help="Manage taggings")

@tags_app.callback()
def tags(ctx: typer.Context):
    """Manage tags."""
    get_state(ctx)

@taggings_app.callback()
def taggings(ctx: typer.Context):
    """Manage taggings."""
    get_state(ctx)
