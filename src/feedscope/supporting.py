import typer
from .state import get_state

imports_app = typer.Typer(help="Manage imports")
pages_app = typer.Typer(help="Manage pages")
icons_app = typer.Typer(help="Manage icons")

@imports_app.callback()
def imports(ctx: typer.Context):
    """Manage imports."""
    get_state(ctx)

@pages_app.callback()
def pages(ctx: typer.Context):
    """Manage pages."""
    get_state(ctx)

@icons_app.callback()
def icons(ctx: typer.Context):
    """Manage icons."""
    get_state(ctx)

def extract_command(ctx: typer.Context):
    """Extract content from a URL."""
    get_state(ctx)
    # This is a placeholder. Real implementation later.
