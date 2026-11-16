"""Tools: save and list flashcards, stored in a local JSON file."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import ToolError, ToolInputError, ToolUnavailableError
from .validation import validate_example, validate_limit, validate_phrase

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "flashcards.json"


class FlashcardStore:
    """A small persistent list of cards: {"id", "word", "translation", "example", "created_at"}."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path or os.environ.get("FLASHCARDS_PATH") or DEFAULT_PATH)

    def _load(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ToolUnavailableError("The flashcard file is unreadable or corrupted.") from exc
        if not isinstance(data, list):
            raise ToolUnavailableError("The flashcard file has an unexpected format.")
        return data

    def _write(self, cards: list[dict[str, Any]]) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.path)
        except OSError as exc:
            raise ToolUnavailableError("Could not write the flashcard file.") from exc

    def save(self, word: str, translation: str, example: str = "") -> dict[str, Any]:
        word = validate_phrase(word, "word")
        translation = validate_phrase(translation, "translation")
        example = validate_example(example)
        cards = self._load()
        if any(str(c.get("word", "")).lower() == word.lower() for c in cards):
            raise ToolInputError(f"A flashcard for '{word}' already exists.")
        card = {
            "id": max((c.get("id", 0) for c in cards), default=0) + 1,
            "word": word,
            "translation": translation,
            "example": example,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self._write([*cards, card])
        return card

    def list(self, limit: int = 10) -> dict[str, Any]:
        limit = validate_limit(limit)
        cards = self._load()
        return {"cards": cards[-limit:][::-1], "total": len(cards)}


def save_flashcard(
    word: str, translation: str, example: str = "", store: FlashcardStore | None = None
) -> dict[str, Any]:
    """Return {"saved": True, "card_id", "card"} or {"error", "error_type"}. Never raises."""
    try:
        card = (store or FlashcardStore()).save(word, translation, example)
        return {"saved": True, "card_id": card["id"], "card": card}
    except ToolError as exc:
        return {"error": str(exc), "error_type": exc.kind}


def list_flashcards(limit: int = 10, store: FlashcardStore | None = None) -> dict[str, Any]:
    """Return {"cards": [...newest first], "total"} or {"error", "error_type"}."""
    try:
        return (store or FlashcardStore()).list(limit)
    except ToolError as exc:
        return {"error": str(exc), "error_type": exc.kind}
