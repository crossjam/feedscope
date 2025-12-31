import typer
from .state import get_state

searches_app = typer.Typer(help="Manage saved searches")

@searches_app.callback()
def searches(ctx: typer.Context):
    """
    Commands for managing saved searches.
    """
    get_state(ctx)
