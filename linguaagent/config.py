"""Settings loaded from environment variables and an optional local .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigError

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT_SECONDS = 30.0
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def load_env_file(path: Path = ENV_FILE) -> None:
    """Read KEY=VALUE lines from `path` into os.environ (existing variables win)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    api_key: str = ""
    model: str = DEFAULT_MODEL
    timeout: float = DEFAULT_TIMEOUT_SECONDS

    def __repr__(self) -> str:  # never print the key
        return f"Settings(model={self.model!r}, timeout={self.timeout}, api_key=<hidden>)"


def get_settings() -> Settings:
    """Build Settings from the environment; raise ConfigError if the key is missing."""
    load_env_file()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and put your key there."
        )
    model = os.environ.get("MODEL_NAME", "").strip() or DEFAULT_MODEL
    return Settings(api_key=api_key, model=model)
