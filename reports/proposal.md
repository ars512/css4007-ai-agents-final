# Project Proposal — Semester Week 10

## Project Title

LinguaAgent — a tool-using AI agent for learning English, Russian and Kazakh vocabulary.

## Problem Description

Language learners constantly switch between a dictionary, a translator and a notes app: they look up a word, translate it, copy an example sentence somewhere and later forget to review it. Each step is a different tool with its own interface.

LinguaAgent lets the learner talk to one assistant in natural language. The LLM decides which tool is needed (dictionary lookup, translation, saving a flashcard, listing saved cards) or answers directly when no tool is needed (for example a grammar question). Definitions and translations come from real tool results, not from the model's memory, so the agent does not invent word meanings.

This matters because vocabulary study is only effective when lookup and review are connected, and because a common failure of plain chatbots is confidently inventing definitions or translations, especially for lower-resource languages such as Kazakh.

## Target Users

University students and self-learners who study English and whose first languages are Russian or Kazakh. The primary user is the author of the project, which makes the application easy to test with real use.

## Selected Difficulty

C — Intermediate: an agent in which the LLM chooses and calls tools. The application also meets the D-level foundations (real LLM integration, prompts, output validation, error handling, at least five tests).

## Expected Functionality

- Explain an English word: definitions, part of speech, example sentences (from a dictionary API).
- Translate words and short phrases between English, Russian and Kazakh (from a translation API).
- Save a word with its translation and an example sentence as a flashcard (persistent local JSON file).
- List saved flashcards and run a short quiz over them.
- Answer language questions that need no tools (grammar, difference between similar words) directly.
- Compound requests where the model chains tools, e.g. "explain 'resilient', translate it to Russian and save a card".
- Honest handling of missing data: a word that is not in the dictionary is reported as not found, and the agent does not invent a definition.
- Input validation (supported languages, non-empty word, length limit), an execution log of every tool call, and graceful handling of API failures, timeouts and invalid model output.

## Proposed Functions

| Name | Purpose | Input | Expected output | Dependencies |
|---|---|---|---|---|
| `lookup_word(word, lang="en")` | Get definitions, part of speech and examples for a word | `word: str` (1–40 characters, letters, hyphen, apostrophe), `lang: str` (only `en` in the first version) | `{"word", "meanings": [{"part_of_speech", "definition", "example"}]}` or `{"error": "..."}` | Free Dictionary API (dictionaryapi.dev), `requests`/`httpx` |
| `translate_text(text, source_lang, target_lang)` | Translate a word or short phrase | `text: str` (1–200 characters), languages from `{en, ru, kk}`, source ≠ target | `{"translation", "source_lang", "target_lang"}` or `{"error": "..."}` | MyMemory Translation API |
| `save_flashcard(word, translation, example="")` | Persist a flashcard | `word: str`, `translation: str`, `example: str` (optional) | `{"saved": true, "card_id"}` or `{"error": "duplicate"}` | Local JSON file (`data/flashcards.json`) |
| `list_flashcards(limit=10)` | Return saved flashcards | `limit: int` (1–50) | `{"cards": [...], "total": n}` | Local JSON file |
| `validate_*` helpers | Check tool arguments before execution | raw arguments from the model | validated arguments or a validation error | Standard library (pydantic or manual checks) |
| `run_agent(user_message)` | Main loop: model call, tool dispatch, final answer | user text | final answer text plus the tool-call log | OpenAI API, the tools above |
| `log_tool_call(...)` | Record each tool call (name, validated arguments, outcome, duration) | tool call data | line in `logs/tool_calls.jsonl` (no secrets) | Standard library |

## Proposed Agent Tools

The model can call these four functions as tools (OpenAI function calling, with JSON schemas):

1. `lookup_word` — the agent needs it to ground definitions and examples in a real dictionary instead of relying on model memory.
2. `translate_text` — the agent needs it for translations, in particular for Kazakh, where model-only translations are less reliable.
3. `save_flashcard` — a state-changing tool that makes the agent useful over time: the learner's vocabulary persists between sessions.
4. `list_flashcards` — lets the agent show saved cards and build a quiz from the learner's own words.

Not exposed as tools: validation, logging and the agent loop (they are application code the model cannot bypass). Requests that need no tool (grammar questions, small talk) are answered by the model directly.

## Model Selection

OpenAI API, model `gpt-4o-mini` through the Chat Completions API with function calling. It is inexpensive, supports tool calls and JSON output, and is enough for this task. The model name and API key are read from environment variables (`OPENAI_API_KEY`, `MODEL_NAME`) stored in a local `.env` file that is excluded from git; `.env.example` contains only placeholders. Unit tests use a mocked LLM client, so the test suite needs no key and no network.

Language: Python 3.

## Architecture

```
User request (CLI)
      |
      v
Input validation  --invalid--> error message
      |
      v
Prompt construction (system prompt + tool schemas + history)
      |
      v
LLM (gpt-4o-mini)  --no tool needed--> final answer
      |
  tool call chosen
      v
Argument validation --invalid--> error returned to LLM
      |
      v
Tool execution (dictionary API / translation API / flashcard store)
      |        \--> tool call log (JSONL)
      v
Tool result (or structured error) sent back to LLM
      |
      v
LLM (may call another tool, up to a step limit)
      |
      v
Final answer grounded in tool results
```

## Example Requests

1. "What does 'serendipity' mean? Give me an example." — expected: the model calls `lookup_word` and answers from the returned definition.
2. "Translate 'книга' to English and save it as a flashcard." — expected: `translate_text` followed by `save_flashcard`, then confirmation.
3. "What is the difference between 'affect' and 'effect'?" — expected: no tool call, direct answer.
4. "Show my flashcards and quiz me on three of them." — expected: `list_flashcards`, then a quiz built from the real cards.
5. "Define 'xqzvbn'." — expected: `lookup_word` returns not found; the agent says the word was not found and does not invent a meaning.

## Evaluation Plan

All tests use a mocked LLM client and mocked HTTP responses, so they are deterministic and run offline. The target is at least 8 project tests (C requirement), which also cover the D foundations (at least 5):

- Tool schema is valid and all four tools are registered.
- The model's tool call is dispatched to the correct function with the correct arguments (scripted mock LLM responses).
- A request that needs no tool produces no tool call.
- Invalid arguments (unsupported language, empty word, text too long, limit out of range) are rejected before execution.
- Dictionary "word not found" and translation API failure/timeout are handled and reported honestly.
- Tool results are returned to the model and appear in the final answer.
- Saving a flashcard persists it; a duplicate is rejected; listing returns saved cards.
- Invalid model output (malformed tool arguments JSON) and OpenAI API errors are handled without crashing.
- The execution log records every tool call and contains no API key.
- The step limit stops a model that keeps calling tools.

In addition, a short manual run with the real API before the demo, and a few unseen-style requests (unknown word, unsupported language, an off-topic request, a tool failure) rehearsed for the defense. Test results are recorded in the Week 16 report.

## Weekly Milestones

| Week | Dates | Plan |
|---|---|---|
| 10 | 2–8 Nov | Fork the repository; choose topic and level; complete this proposal and the Week 10 report. |
| 11 | 9–15 Nov | Project skeleton, virtual environment, `.env` handling, first working OpenAI request from the CLI, basic README, first tests. |
| 12 | 16–22 Nov | Core functions: `lookup_word`, `translate_text`, flashcard storage; input and output validation; structured outputs; initial tests. |
| 13 | 23–29 Nov | Register tools with function calling; the LLM selects and the program executes tools; return results to the model; request without tools. |
| 14 | 30 Nov–6 Dec | Complete the tool-calling workflow with multi-tool requests, tool error handling, execution logs. |
| 15 | 7–13 Dec | Failure handling (timeouts, rate limits, malformed output), step limit, stronger validation, expand tests to 8 or more. |
| 16 | 14–20 Dec | Run the full suite, record results, analyze failures, fix, update documentation; write `week-16.md`. |
| 17 | 21–22 Dec | Final README, final report, AI-assistant disclosure, final commit hash, demo and defense. |
