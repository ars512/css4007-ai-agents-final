"""Tool: look up an English word in the Free Dictionary API."""
from __future__ import annotations

from typing import Any, Callable

from .errors import NotFoundError, ToolError, ToolUnavailableError
from .http_client import get_json
from .validation import validate_language, validate_word

DICTIONARY_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/"
MAX_MEANINGS = 5


def _parse_meanings(payload: Any) -> list[dict[str, str]]:
    meanings: list[dict[str, str]] = []
    try:
        for entry in payload:
            for meaning in entry["meanings"]:
                for item in meaning["definitions"][:2]:
                    meanings.append(
                        {
                            "part_of_speech": str(meaning.get("partOfSpeech", "")),
                            "definition": str(item["definition"]),
                            "example": str(item.get("example", "")),
                        }
                    )
                    if len(meanings) >= MAX_MEANINGS:
                        return meanings
    except (KeyError, TypeError, IndexError, AttributeError) as exc:
        raise ToolUnavailableError("The dictionary returned data in an unexpected format.") from exc
    return meanings


def lookup_word(word: str, lang: str = "en", fetch: Callable[..., Any] = get_json) -> dict[str, Any]:
    """Return {"word", "meanings": [...]} or {"error", "error_type"}. Never raises."""
    try:
        lang = validate_language(lang)
        if lang != "en":
            raise NotFoundError("Dictionary lookup supports English words only; use translate_text.")
        word = validate_word(word).lower()
        try:
            payload = fetch(DICTIONARY_URL + word)
        except NotFoundError:
            raise NotFoundError(f"The word '{word}' was not found in the dictionary.") from None
        meanings = _parse_meanings(payload)
        if not meanings:
            raise NotFoundError(f"No definitions found for '{word}'.")
        return {"word": word, "meanings": meanings}
    except ToolError as exc:
        return {"error": str(exc), "error_type": exc.kind}
