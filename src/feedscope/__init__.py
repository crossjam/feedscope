import typer
import httpx
from typing_extensions import Annotated
from rich.prompt import Prompt

app = typer.Typer(help="Feedscope - CLI for working with Feedbin API content")

@app.command()
def auth(
    email: Annotated[str, typer.Option("--email", "-e", help="Feedbin email address")],
    password: Annotated[str, typer.Option("--password", "-p", help="Feedbin password", hide_input=True)] = None
) -> None:
    """Check authentication credentials with Feedbin API."""
    
    # Prompt for password if not provided
    if password is None:
        password = Prompt.ask("Enter your Feedbin password", password=True)
    
    url = "https://api.feedbin.com/v2/authentication.json"
    
    try:
        response = httpx.get(url, auth=(email, password))
        
        if response.status_code == 200:
            typer.echo("✅ Authentication successful!", color=typer.colors.GREEN)
        elif response.status_code == 401:
            typer.echo("❌ Authentication failed - invalid credentials", color=typer.colors.RED)
            raise typer.Exit(1)
        else:
            typer.echo(f"❌ Unexpected response: {response.status_code}", color=typer.colors.RED)
            raise typer.Exit(1)
            
    except httpx.RequestError as e:
        typer.echo(f"❌ Network error: {e}", color=typer.colors.RED)
        raise typer.Exit(1)

def main() -> None:
    app()
