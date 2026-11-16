"""Tests for the Week 12 core functions. All HTTP is mocked; no network or key is needed."""
import io
import json
import socket
import urllib.error

import pytest

from linguaagent.dictionary import lookup_word
from linguaagent.errors import NotFoundError, ToolInputError, ToolUnavailableError
from linguaagent.flashcards import FlashcardStore, list_flashcards, save_flashcard
from linguaagent.http_client import get_json
from linguaagent.translation import translate_text
from linguaagent.validation import (
    validate_language,
    validate_limit,
    validate_phrase,
    validate_word,
)

DICT_PAYLOAD = [
    {
        "word": "resilient",
        "meanings": [
            {
                "partOfSpeech": "adjective",
                "definitions": [
                    {"definition": "Returning quickly to shape.", "example": "A resilient material."},
                    {"definition": "Recovering quickly from trouble."},
                    {"definition": "third definition is dropped"},
                ],
            }
        ],
    }
]


def fetch_returning(payload):
    return lambda *args, **kwargs: payload


def fetch_raising(error):
    def fetch(*args, **kwargs):
        raise error

    return fetch


# ---------- argument validation ----------


@pytest.mark.parametrize("bad", ["", "  ", "two words", "abc123", "x" * 41, None, 5])
def test_validate_word_rejects_bad_values(bad):
    with pytest.raises(ToolInputError):
        validate_word(bad)


def test_validate_word_accepts_hyphen_apostrophe_and_cyrillic():
    assert validate_word("well-known") == "well-known"
    assert validate_word("don't") == "don't"
    assert validate_word("книга") == "книга"


def test_validate_language_and_limit_and_phrase():
    assert validate_language(" RU ") == "ru"
    for bad in ("de", "", None):
        with pytest.raises(ToolInputError):
            validate_language(bad)
    assert validate_limit(5) == 5
    for bad in (0, 51, "3", True, 2.5):
        with pytest.raises(ToolInputError):
            validate_limit(bad)
    assert validate_phrase("  hello   world ") == "hello world"
    with pytest.raises(ToolInputError):
        validate_phrase("x" * 201)


# ---------- lookup_word ----------


def test_lookup_word_returns_structured_meanings():
    result = lookup_word("Resilient", fetch=fetch_returning(DICT_PAYLOAD))
    assert result["word"] == "resilient"
    assert [m["definition"] for m in result["meanings"]][:2] == [
        "Returning quickly to shape.",
        "Recovering quickly from trouble.",
    ]
    assert result["meanings"][0] == {
        "part_of_speech": "adjective",
        "definition": "Returning quickly to shape.",
        "example": "A resilient material.",
    }
    assert len(result["meanings"]) == 2  # at most two definitions per part of speech


def test_lookup_word_unknown_word_is_not_found_without_inventing_data():
    result = lookup_word("xqzvbn", fetch=fetch_raising(NotFoundError("404")))
    assert result["error_type"] == "not_found"
    assert "xqzvbn" in result["error"]
    assert "meanings" not in result


def test_lookup_word_invalid_argument_never_calls_the_service():
    calls = []
    result = lookup_word("12 3", fetch=lambda *a, **k: calls.append(1))
    assert result["error_type"] == "invalid_input"
    assert calls == []


def test_lookup_word_non_english_is_rejected_politely():
    result = lookup_word("книга", lang="ru", fetch=fetch_returning(DICT_PAYLOAD))
    assert result["error_type"] == "not_found"
    assert "translate_text" in result["error"]


def test_lookup_word_service_failure_and_bad_format():
    down = lookup_word("book", fetch=fetch_raising(ToolUnavailableError("down")))
    assert down == {"error": "down", "error_type": "unavailable"}
    bad = lookup_word("book", fetch=fetch_returning({"unexpected": True}))
    assert bad["error_type"] == "unavailable"


# ---------- translate_text ----------


def mymemory(text, status=200, quota=False):
    return {"responseData": {"translatedText": text}, "responseStatus": status, "quotaFinished": quota}


def test_translate_text_success_and_request_parameters():
    seen = {}

    def fetch(url, params=None, **kwargs):
        seen.update(params)
        return mymemory(" Кітап ")

    result = translate_text("book", "EN", "kk", fetch=fetch)
    assert result == {"translation": "Кітап", "source_lang": "en", "target_lang": "kk"}
    assert seen == {"q": "book", "langpair": "en|kk"}


@pytest.mark.parametrize(
    "args",
    [("", "en", "ru"), ("book", "en", "en"), ("book", "de", "ru"), ("book", "en", "xx"), ("x" * 201, "en", "ru")],
)
def test_translate_text_invalid_arguments_are_rejected_before_the_call(args):
    calls = []
    result = translate_text(*args, fetch=lambda *a, **k: calls.append(1))
    assert result["error_type"] == "invalid_input"
    assert calls == []


@pytest.mark.parametrize(
    "payload",
    [mymemory("INVALID LANGUAGE PAIR", status=403), mymemory(""), mymemory("x", quota=True), {"oops": 1}],
)
def test_translate_text_bad_service_answers_become_unavailable(payload):
    result = translate_text("book", "en", "ru", fetch=fetch_returning(payload))
    assert result["error_type"] == "unavailable"
    assert "translation" not in result


def test_translate_text_network_failure_is_reported():
    result = translate_text("book", "en", "ru", fetch=fetch_raising(ToolUnavailableError("timeout")))
    assert result == {"error": "timeout", "error_type": "unavailable"}


# ---------- flashcards ----------


def test_flashcard_is_saved_persisted_and_listed_newest_first(tmp_path):
    path = tmp_path / "cards.json"
    saved = save_flashcard("book", "книга", "I read a book.", store=FlashcardStore(path))
    assert saved["saved"] is True and saved["card_id"] == 1
    save_flashcard("water", "су", store=FlashcardStore(path))  # new store object: data was persisted
    listed = list_flashcards(10, store=FlashcardStore(path))
    assert listed["total"] == 2
    assert [c["word"] for c in listed["cards"]] == ["water", "book"]
    assert json.loads(path.read_text(encoding="utf-8"))[0]["translation"] == "книга"


def test_flashcard_duplicate_is_rejected_case_insensitively(tmp_path):
    store = FlashcardStore(tmp_path / "cards.json")
    save_flashcard("Book", "книга", store=store)
    again = save_flashcard("book", "кітап", store=store)
    assert again["error_type"] == "invalid_input"
    assert list_flashcards(store=store)["total"] == 1


def test_flashcard_validation_and_limit(tmp_path):
    store = FlashcardStore(tmp_path / "cards.json")
    assert save_flashcard("", "x", store=store)["error_type"] == "invalid_input"
    assert save_flashcard("a", "", store=store)["error_type"] == "invalid_input"
    assert save_flashcard("a", "b", "e" * 301, store=store)["error_type"] == "invalid_input"
    for i in range(3):
        save_flashcard(f"w{i}", "t", store=store)
    assert len(list_flashcards(2, store=store)["cards"]) == 2
    assert list_flashcards(0, store=store)["error_type"] == "invalid_input"


def test_flashcard_empty_store_and_corrupted_file(tmp_path):
    assert list_flashcards(store=FlashcardStore(tmp_path / "none.json")) == {"cards": [], "total": 0}
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    result = list_flashcards(store=FlashcardStore(bad))
    assert result["error_type"] == "unavailable"
    assert bad.read_text(encoding="utf-8") == "{not json"  # the broken file is not overwritten
    assert save_flashcard("a", "b", store=FlashcardStore(bad))["error_type"] == "unavailable"


# ---------- HTTP helper ----------


class FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def opener_returning(body: bytes):
    return lambda request, timeout: FakeResponse(body)


def opener_raising(error):
    def opener(request, timeout):
        raise error

    return opener


def http_error(code):
    return urllib.error.HTTPError("http://x", code, "msg", {}, io.BytesIO(b""))


def test_get_json_parses_and_builds_query_string():
    seen = {}

    def opener(request, timeout):
        seen["url"], seen["timeout"] = request.full_url, timeout
        return FakeResponse(b'{"ok": 1}')

    assert get_json("http://x/api", params={"q": "a b"}, timeout=3, opener=opener) == {"ok": 1}
    assert seen == {"url": "http://x/api?q=a+b", "timeout": 3}


def test_get_json_error_mapping():
    with pytest.raises(NotFoundError):
        get_json("http://x", opener=opener_raising(http_error(404)))
    for failing in (
        opener_raising(http_error(500)),
        opener_raising(urllib.error.URLError("no network")),
        opener_raising(socket.timeout()),
        opener_raising(urllib.error.URLError(socket.timeout())),
        opener_returning(b"<html>not json</html>"),
    ):
        with pytest.raises(ToolUnavailableError):
            get_json("http://x", opener=failing)
