from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from platformdirs import user_config_dir
from collections.abc import MutableMapping
from typing import cast

from pathlib import Path

import tomlkit


class AuthCredentials(BaseModel):
    """Authentication credentials."""

    email: str = ""
    password: str = ""


class ExtractCredentials(BaseModel):
    """Extraction service credentials."""

    username: str = ""
    secret: str = ""


class FeedscopeConfig(BaseSettings):
    model_config = SettingsConfigDict(
        toml_file=Path(user_config_dir("dev.pirateninja.feedscope")) / "config.toml",
    )

    auth: AuthCredentials = AuthCredentials()
    extract: ExtractCredentials = ExtractCredentials()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (TomlConfigSettingsSource(settings_cls),)

    @classmethod
    def load(cls) -> "FeedscopeConfig":
        """Load configuration from file."""
        return cls()

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

        # Update auth
        if "auth" not in doc or not isinstance(doc.get("auth"), dict):
            doc["auth"] = tomlkit.table()

        auth_table = cast(MutableMapping, doc["auth"])
        auth_table["email"] = self.auth.email
        auth_table["password"] = self.auth.password

        # Update extract
        if "extract" not in doc or not isinstance(doc.get("extract"), dict):
            doc["extract"] = tomlkit.table()

        extract_table = cast(MutableMapping, doc["extract"])
        extract_table["username"] = self.extract.username
        extract_table["secret"] = self.extract.secret

        if "email" in doc:
            del doc["email"]
        if "password" in doc:
            del doc["password"]

        # Write back to file
        config_file.write_text(tomlkit.dumps(doc))


def get_config() -> FeedscopeConfig:
    """Get the configuration for use in commands."""
    return FeedscopeConfig.load()
