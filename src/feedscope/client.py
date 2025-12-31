import httpx
from hishel import CacheClient, FileStorage
from platformdirs import user_cache_dir
from pathlib import Path
import stamina


class FeedscopeClient(CacheClient):
    """Custom client that adds retries for safe methods."""

    def request(self, method: str, url, **kwargs) -> httpx.Response:
        # Only retry safe methods or DELETE (as per plan "GET/DELETE")
        if method.upper() in ["GET", "DELETE", "HEAD", "OPTIONS"]:
            try:
                for attempt in stamina.retry_context(
                    on=(httpx.RequestError, httpx.HTTPStatusError), attempts=3
                ):
                    with attempt:
                        response = super().request(method, url, **kwargs)
                        # Trigger retry on server errors
                        if response.status_code >= 500:
                            response.raise_for_status()
                        return response
            except httpx.HTTPStatusError as e:
                # If retries exhausted for 5xx, return the last response
                return e.response
            # RequestError will bubble up if retries exhausted

        return super().request(method, url, **kwargs)


def get_client() -> httpx.Client:
    """Get a cached httpx client with retries."""
    cache_dir = Path(user_cache_dir("dev.pirateninja.feedscope", "http-cache"))
    storage = FileStorage(base_path=cache_dir)
    return FeedscopeClient(storage=storage)
