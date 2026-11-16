"""Tool: translate a word or short phrase between English, Russian and Kazakh (MyMemory API)."""
from __future__ import annotations

from typing import Any, Callable

from .errors import ToolError, ToolInputError, ToolUnavailableError
from .http_client import get_json
from .validation import validate_language, validate_phrase

TRANSLATE_URL = "https://api.mymemory.translated.net/get"


def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    fetch: Callable[..., Any] = get_json,
) -> dict[str, Any]:
    """Return {"translation", "source_lang", "target_lang"} or {"error", "error_type"}."""
    try:
        source = validate_language(source_lang, "source_lang")
        target = validate_language(target_lang, "target_lang")
        if source == target:
            raise ToolInputError("source_lang and target_lang must be different.")
        phrase = validate_phrase(text)
        payload = fetch(TRANSLATE_URL, params={"q": phrase, "langpair": f"{source}|{target}"})
        try:
            status = int(payload.get("responseStatus", 200))
            translation = str(payload["responseData"]["translatedText"]).strip()
            quota_finished = bool(payload.get("quotaFinished"))
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise ToolUnavailableError("The translation service returned an unexpected format.") from exc
        if quota_finished:
            raise ToolUnavailableError("The free translation quota is used up. Try again later.")
        if status != 200 or not translation:
            raise ToolUnavailableError("The translation service could not translate this text.")
        return {"translation": translation, "source_lang": source, "target_lang": target}
    except ToolError as exc:
        return {"error": str(exc), "error_type": exc.kind}
