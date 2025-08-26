import typer

from .subscriptions import subscriptions_app
from .auth import auth_app


app = typer.Typer(help="Feedscope - CLI for working with Feedbin API content")
app.add_typer(auth_app, name="auth")
app.add_typer(subscriptions_app, name="subscriptions")



def main() -> None:
    app()
