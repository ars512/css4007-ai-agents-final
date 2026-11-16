"""Validation of user input before it reaches the model."""
from __future__ import annotations

from .errors import InvalidInputError, ToolInputError

MAX_MESSAGE_LENGTH = 1000


def validate_user_message(message: object) -> str:
    """Return the cleaned message or raise InvalidInputError."""
    if not isinstance(message, str):
        raise InvalidInputError("Message must be text.")
    cleaned = message.strip()
    if not cleaned:
        raise InvalidInputError("Message is empty. Type a question about a word or a language.")
    if len(cleaned) > MAX_MESSAGE_LENGTH:
        raise InvalidInputError(
            f"Message is too long ({len(cleaned)} characters, the limit is {MAX_MESSAGE_LENGTH})."
        )
    return cleaned


# ---- tool argument validation (used by the tools and, later, by the agent) ----

SUPPORTED_LANGUAGES = ("en", "ru", "kk")
MAX_WORD_LENGTH = 40
MAX_PHRASE_LENGTH = 200
MAX_EXAMPLE_LENGTH = 300
MAX_LIST_LIMIT = 50


def _text(value: object, name: str, max_length: int, required: bool = True) -> str:
    if not isinstance(value, str):
        raise ToolInputError(f"{name} must be text.")
    cleaned = " ".join(value.split())
    if not cleaned:
        if required:
            raise ToolInputError(f"{name} must not be empty.")
        return ""
    if len(cleaned) > max_length:
        raise ToolInputError(f"{name} is too long ({len(cleaned)} > {max_length} characters).")
    return cleaned


def validate_language(value: object, name: str = "lang") -> str:
    code = value.strip().lower() if isinstance(value, str) else value
    if code not in SUPPORTED_LANGUAGES:
        raise ToolInputError(
            f"{name} must be one of {', '.join(SUPPORTED_LANGUAGES)} (got {value!r})."
        )
    return code


def validate_word(value: object, name: str = "word") -> str:
    """A single word: letters, hyphens and apostrophes, 1-40 characters."""
    word = _text(value, name, MAX_WORD_LENGTH)
    if not all(ch.isalpha() or ch in "-'’" for ch in word):
        raise ToolInputError(f"{name} must be a single word (letters, '-' and apostrophe only).")
    return word


def validate_phrase(value: object, name: str = "text") -> str:
    """A word or short phrase of up to 200 characters."""
    return _text(value, name, MAX_PHRASE_LENGTH)


def validate_example(value: object) -> str:
    """Optional example sentence (may be empty)."""
    return _text(value, "example", MAX_EXAMPLE_LENGTH, required=False)


def validate_limit(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ToolInputError("limit must be an integer.")
    if not 1 <= value <= MAX_LIST_LIMIT:
        raise ToolInputError(f"limit must be between 1 and {MAX_LIST_LIMIT}.")
    return value
