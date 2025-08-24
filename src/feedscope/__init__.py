import typer
import httpx
from typing_extensions import Annotated
from rich.prompt import Prompt
from pydantic_settings import BaseSettings, SettingsConfigDict
from platformdirs import user_config_dir
from pathlib import Path

class FeedscopeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=Path(user_config_dir("dev.pirateninja.feedscope")) / "config.toml",
        env_prefix="FEEDSCOPE_"
    )
    
    email: str = ""
    password: str = ""
    
    def save(self) -> None:
        """Save configuration to TOML file."""
        config_dir = Path(user_config_dir("dev.pirateninja.feedscope"))
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.toml"
        
        # Write TOML content manually since pydantic-settings doesn't have a built-in save method
        toml_content = f"""email = "{self.email}"
password = "{self.password}"
"""
        config_file.write_text(toml_content)

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
            
            # Save credentials to config file
            config = FeedscopeConfig(email=email, password=password)
            config.save()
            typer.echo(f"💾 Credentials saved to config file", color=typer.colors.BLUE)
            
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
