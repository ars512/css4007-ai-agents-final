# LinguaAgent

A tool-using AI agent for learning English, Russian and Kazakh vocabulary (course project, level C).
See [reports/proposal.md](reports/proposal.md) for the full plan.

**Status (Week 12):** the application can send a validated user message to an OpenAI model and print
the answer. The three core functions (dictionary lookup, translation, flashcards) are implemented and
tested and can be run directly from the command line. Letting the model choose and call them as tools
is planned for Week 13.

## Setup

Requires Python 3.11+ and an OpenAI API key.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # macOS/Linux
cp .env.example .env     # then put your key into .env (the file is git-ignored)
```

## Run

```bash
python -m linguaagent.cli "What does the word 'resilient' mean?"   # one question
python -m linguaagent.cli                                          # interactive mode
```

## Core functions (Week 12)

Each function validates its arguments first and returns a structured dict. It never raises for expected
problems: on failure it returns `{"error": "...", "error_type": "invalid_input | not_found | unavailable"}`.

| Function | Returns on success | Source |
|---|---|---|
| `lookup_word(word, lang="en")` | `{"word", "meanings": [{"part_of_speech", "definition", "example"}]}` | Free Dictionary API |
| `translate_text(text, source_lang, target_lang)` | `{"translation", "source_lang", "target_lang"}` (`en`, `ru`, `kk`) | MyMemory API |
| `save_flashcard(word, translation, example="")` | `{"saved": true, "card_id", "card"}` | `data/flashcards.json` (git-ignored) |
| `list_flashcards(limit=10)` | `{"cards": [...newest first], "total"}` | `data/flashcards.json` |

Try them without the LLM:

```bash
python -m linguaagent.tools_cli lookup resilient
python -m linguaagent.tools_cli translate book en kk
python -m linguaagent.tools_cli save book книга --example "I read a book."
python -m linguaagent.tools_cli list
```

Known limitation: the free translation service is a translation memory, so quality varies for rare
words, especially in Kazakh. The storage path can be changed with `FLASHCARDS_PATH`.

## Test

```bash
python -m pytest -q      # project tests; they use a mocked client, no key or network needed
npm test                 # starter utilities from the instructor repository
```

## Layout

| Path | Purpose |
|---|---|
| `linguaagent/config.py` | loads settings from the environment / `.env`, never prints the key |
| `linguaagent/validation.py` | validates user input before the model is called |
| `linguaagent/llm_client.py` | OpenAI wrapper; converts provider failures into `LLMError` |
| `linguaagent/cli.py` | command-line entry point for the LLM chat |
| `linguaagent/http_client.py` | JSON GET helper; maps HTTP/network/timeout failures to tool errors |
| `linguaagent/dictionary.py` | `lookup_word` |
| `linguaagent/translation.py` | `translate_text` |
| `linguaagent/flashcards.py` | `FlashcardStore`, `save_flashcard`, `list_flashcards` |
| `linguaagent/tools_cli.py` | run the core functions directly |
| `tests/test_llm_client.py` | tests for input validation, config and the LLM wrapper (mocked) |
| `tests/test_tools.py` | tests for validators, the three functions and the HTTP helper (mocked) |

## AI assistant disclosure

The code and documents in this repository were written with the help of an AI coding assistant
(Claude Code). I review, run and test the generated code and am responsible for explaining it.
