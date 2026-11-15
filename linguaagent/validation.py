"""Validation of user input before it reaches the model."""
from __future__ import annotations

from .errors import InvalidInputError

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
