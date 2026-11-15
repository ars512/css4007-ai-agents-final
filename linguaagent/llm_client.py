"""Thin wrapper around the OpenAI Chat Completions API with clear error handling."""
from __future__ import annotations

from typing import Any

import openai
from openai import OpenAI

from .config import Settings
from .errors import LLMError

SYSTEM_PROMPT = (
    "You are LinguaAgent, a friendly assistant that helps people learn English, "
    "Russian and Kazakh vocabulary. Answer briefly and clearly. "
    "If you are not sure about a word's meaning or a translation, say so instead of guessing."
)


class LLMClient:
    """Sends chat messages to the model and returns the text of the reply."""

    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self.settings = settings
        # `client` can be injected in tests so no network or key is needed.
        self._client = client or OpenAI(
            api_key=settings.api_key, timeout=settings.timeout, max_retries=2
        )

    def chat(self, messages: list[dict[str, Any]]) -> str:
        """Return the assistant's text. Raise LLMError for any provider failure."""
        try:
            response = self._client.chat.completions.create(
                model=self.settings.model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, *messages],
            )
        except openai.AuthenticationError as exc:
            raise LLMError("The API key was rejected. Check OPENAI_API_KEY in .env.") from exc
        except openai.RateLimitError as exc:
            raise LLMError("Rate limit or quota reached. Try again later or check billing.") from exc
        except openai.APITimeoutError as exc:
            raise LLMError("The model did not answer in time. Try again.") from exc
        except openai.APIConnectionError as exc:
            raise LLMError("Could not reach the OpenAI API. Check your internet connection.") from exc
        except openai.APIError as exc:
            raise LLMError(f"The OpenAI API returned an error: {exc.__class__.__name__}.") from exc

        try:
            text = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise LLMError("The model returned an unexpected response format.") from exc
        if not text or not text.strip():
            raise LLMError("The model returned an empty answer.")
        return text.strip()
