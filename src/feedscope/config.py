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

def get_config() -> FeedscopeConfig:
    """Get the configuration for use in commands."""
    return FeedscopeConfig.load()
