"""Minimal JSON-over-HTTP GET helper (standard library only) with mapped errors."""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from .errors import NotFoundError, ToolUnavailableError

USER_AGENT = "LinguaAgent/0.1 (student course project)"
DEFAULT_TIMEOUT = 10.0


def get_json(
    url: str,
    params: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> Any:
    """GET `url` and return the parsed JSON.

    404 becomes NotFoundError; every other failure (HTTP error, network, timeout,
    invalid JSON) becomes ToolUnavailableError. `opener` is injectable for tests.
    """
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener(request, timeout=timeout) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise NotFoundError("The service has no data for this request.") from exc
        raise ToolUnavailableError(f"The service returned HTTP {exc.code}.") from exc
    except (socket.timeout, TimeoutError) as exc:
        raise ToolUnavailableError("The service did not answer in time.") from exc
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, (socket.timeout, TimeoutError)):
            raise ToolUnavailableError("The service did not answer in time.") from exc
        raise ToolUnavailableError("Could not reach the service (network problem).") from exc
    except OSError as exc:
        raise ToolUnavailableError("Could not reach the service (network problem).") from exc
    try:
        return json.loads(body)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ToolUnavailableError("The service returned invalid data.") from exc
