import os
from pathlib import Path
import pytest
from platformdirs import user_config_dir

# Ensure configuration writes are isolated to a test-specific directory
TEST_CONFIG_HOME = Path(__file__).parent / "_config_home"
TEST_CONFIG_HOME.mkdir(parents=True, exist_ok=True)
os.environ["XDG_CONFIG_HOME"] = str(TEST_CONFIG_HOME)

CONFIG_FILE = Path(user_config_dir("dev.pirateninja.feedscope")) / "config.toml"

@pytest.fixture(autouse=True)
def clean_config_file() -> None:
    """Ensure the config file is removed before and after each test."""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    yield
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()

@pytest.fixture
def config_path():
    return CONFIG_FILE

@pytest.fixture
def auth_config(clean_config_file):
    """Setup auth config."""
    # Write a dummy config
    import tomlkit
    doc = tomlkit.document()
    doc["auth"] = {"email": "test@example.com", "password": "password"}
    
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w") as f:
        f.write(tomlkit.dumps(doc))
    return doc
