"""Tests for validation, configuration and the LLM wrapper. No network or API key needed."""
from types import SimpleNamespace

import httpx2 as httpx
import openai
import pytest

from linguaagent import config
from linguaagent.cli import ask
from linguaagent.config import Settings, get_settings
from linguaagent.errors import ConfigError, InvalidInputError, LLMError
from linguaagent.llm_client import SYSTEM_PROMPT, LLMClient
from linguaagent.validation import MAX_MESSAGE_LENGTH, validate_user_message

SETTINGS = Settings(api_key="test-key", model="test-model")


class FakeOpenAI:
    """Mimics client.chat.completions.create; returns a reply or raises an error."""

    def __init__(self, reply=None, error=None):
        self.calls = []
        self._reply, self._error = reply, error
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error:
            raise self._error
        message = SimpleNamespace(content=self._reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _request():
    return httpx.Request("POST", "https://api.openai.com/v1/chat/completions")


def _status_error(cls, status):
    return cls("boom", response=httpx.Response(status, request=_request()), body=None)


def test_valid_message_is_trimmed():
    assert validate_user_message("  hello  ") == "hello"


@pytest.mark.parametrize("bad", ["", "   ", None, 42, "x" * (MAX_MESSAGE_LENGTH + 1)])
def test_invalid_message_is_rejected(bad):
    with pytest.raises(InvalidInputError):
        validate_user_message(bad)


def test_chat_sends_system_prompt_model_and_user_message():
    fake = FakeOpenAI(reply="  book = книга  ")
    answer = LLMClient(SETTINGS, client=fake).chat([{"role": "user", "content": "book?"}])
    assert answer == "book = книга"
    call = fake.calls[0]
    assert call["model"] == "test-model"
    assert call["messages"][0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert call["messages"][1] == {"role": "user", "content": "book?"}


def test_ask_rejects_empty_input_without_calling_the_model():
    fake = FakeOpenAI(reply="unused")
    with pytest.raises(InvalidInputError):
        ask(LLMClient(SETTINGS, client=fake), "   ")
    assert fake.calls == []


@pytest.mark.parametrize(
    "error, fragment",
    [
        (_status_error(openai.AuthenticationError, 401), "API key"),
        (_status_error(openai.RateLimitError, 429), "Rate limit"),
        (openai.APITimeoutError(request=_request()), "in time"),
        (openai.APIConnectionError(request=_request()), "internet"),
        (_status_error(openai.InternalServerError, 500), "error"),
    ],
)
def test_provider_failures_become_llm_error(error, fragment):
    client = LLMClient(SETTINGS, client=FakeOpenAI(error=error))
    with pytest.raises(LLMError, match=fragment):
        client.chat([{"role": "user", "content": "hi"}])


@pytest.mark.parametrize("reply", [None, "", "   "])
def test_empty_model_answer_is_an_error(reply):
    client = LLMClient(SETTINGS, client=FakeOpenAI(reply=reply))
    with pytest.raises(LLMError, match="empty"):
        client.chat([{"role": "user", "content": "hi"}])


def test_missing_api_key_raises_config_error(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(config, "ENV_FILE", tmp_path / "missing.env")
    monkeypatch.setattr(config, "load_env_file", lambda *a, **k: None)
    with pytest.raises(ConfigError):
        get_settings()


def test_settings_repr_hides_the_key():
    assert "test-key" not in repr(SETTINGS)
