import httpx
from hishel import CacheClient, FileStorage
from platformdirs import user_cache_dir
from pathlib import Path

def get_client() -> httpx.Client:
    """Get a cached httpx client."""
    cache_dir = Path(user_cache_dir("dev.pirateninja.feedscope", "http-cache"))
    storage = FileStorage(base_path=cache_dir)
    return CacheClient(storage=storage)
