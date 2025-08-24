import typer
import httpx
from typing_extensions import Annotated
from rich.prompt import Prompt
from pydantic_settings import BaseSettings, SettingsConfigDict
from platformdirs import user_config_dir
from pathlib import Path
import tomlkit

class FeedscopeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=Path(user_config_dir("dev.pirateninja.feedscope")) / "config.toml",
        toml_table_header=("auth",),
        env_prefix="FEEDSCOPE_"
    )
    
    email: str = ""
    password: str = ""
    
    @property
    def config_file_path(self) -> Path:
        """Get the path to the configuration file."""
        return Path(user_config_dir("dev.pirateninja.feedscope")) / "config.toml"
    
    def save(self) -> None:
        """Save configuration to TOML file using tomlkit."""
        config_dir = Path(user_config_dir("dev.pirateninja.feedscope"))
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = self.config_file_path
        
        # Load existing TOML or create new document
        if config_file.exists():
            doc = tomlkit.parse(config_file.read_text())
        else:
            doc = tomlkit.document()
        
        # Ensure auth section exists
        if "auth" not in doc:
            doc["auth"] = tomlkit.table()
        
        # Update values in auth section
        doc["auth"]["email"] = self.email
        doc["auth"]["password"] = self.password
        
        # Write back to file
        config_file.write_text(tomlkit.dumps(doc))
    
    @classmethod
    def load(cls) -> "FeedscopeConfig":
        """Load configuration from file."""
        return cls()

app = typer.Typer(help="Feedscope - CLI for working with Feedbin API content")

def get_config() -> FeedscopeConfig:
    """Get the configuration for use in commands."""
    return FeedscopeConfig.load()

@app.command()
def auth(
    email: Annotated[str, typer.Argument(help="Feedbin email address")],
    password: Annotated[str, typer.Option("--password", "-p", help="Feedbin password", hide_input=True)] = None
) -> None:
    """Check authentication credentials with Feedbin API."""
    
    # Load existing config
    config = get_config()
    
    # Prompt for password if not provided
    if password is None:
        password = Prompt.ask("Enter your Feedbin password", password=True)
    
    url = "https://api.feedbin.com/v2/authentication.json"
    
    try:
        response = httpx.get(url, auth=(email, password))
        
        if response.status_code == 200:
            typer.echo("✅ Authentication successful!", color=typer.colors.GREEN)
            
            # Update and save credentials to config file
            config.email = email
            config.password = password
            config.save()
            typer.echo(f"💾 Credentials saved to {config.config_file_path}", color=typer.colors.BLUE)
            
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
