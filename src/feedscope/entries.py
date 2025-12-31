import typer
from .state import get_state

entries_app = typer.Typer(help="Retrieve and manage entries")

@entries_app.callback()
def entries(ctx: typer.Context):
    """
    Commands for retrieving and inspecting entries.
    """
    get_state(ctx)
