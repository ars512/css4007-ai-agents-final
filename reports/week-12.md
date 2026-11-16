# Semester Week 12 Progress Report

## Completed Work

- Implemented the three core functions of the application:
  - `lookup_word` (Free Dictionary API): returns structured meanings (part of speech, definition, example), at most two definitions per part of speech and five in total.
  - `translate_text` (MyMemory API): translation between English, Russian and Kazakh.
  - `save_flashcard` and `list_flashcards`: a persistent JSON store with atomic writes, duplicate rejection and newest-first listing.
- Added argument validation (`linguaagent/validation.py`): supported languages (`en`, `ru`, `kk`), single words, phrases up to 200 characters, optional examples up to 300 characters, list limits 1–50. Invalid arguments are rejected before any service call.
- Added a small HTTP helper (`linguaagent/http_client.py`) that maps failures to application errors: 404 means not found; HTTP errors, network failures, timeouts and invalid JSON mean the service is unavailable.
- Introduced structured outputs: every function returns a dict, and on any expected problem returns `{"error", "error_type"}` with `invalid_input`, `not_found` or `unavailable` instead of raising an exception.
- Validated the service outputs too: unexpected formats, a finished translation quota, a bad status code, empty translations and a corrupted flashcard file are all reported as errors (the corrupted file is not overwritten).
- Added `linguaagent/tools_cli.py` to run the functions directly without the LLM, and checked all of them against the real APIs.
- Added 31 new tests (49 in total) with mocked HTTP, and updated `PROJECT.md`.
- Disclosure: the code was written with the help of an AI coding assistant (Claude Code); I ran it against the real services, reviewed it and test it myself.

## Important Commits

- Commit hash: f8868ff
- Description: Add tool argument validators, tool error types and HTTP helper
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/f8868ff

- Commit hash: 27ebf42
- Description: Implement lookup_word and translate_text with structured results
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/27ebf42

- Commit hash: 7235c7e
- Description: Implement persistent flashcard store (save_flashcard, list_flashcards)
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/7235c7e

- Commit hash: 34920a9
- Description: Add tools_cli to run the core functions without the LLM
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/34920a9

- Commit hash: f58d2c1
- Description: Add 31 tests for validators, tools, flashcards and HTTP helper
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/f58d2c1

- Commit hash: 87d5bed
- Description: Document core functions, CLI usage and project layout
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/87d5bed

## Current Functionality

From the command line the user can look up an English word (`lookup resilient`), translate text between English, Russian and Kazakh (`translate book en kk` gives "Кітап"), save a flashcard and list saved cards. An unknown word (`xqzvbn`), a non-word (`12345`), identical languages and a duplicate card each produce a clear error without a crash or an invented answer. The LLM chat from Week 11 still works; the model does not call these functions yet, because tool registration and tool selection by the model are planned for Week 13.

## Problems Encountered

- The first attempt to write all files in one large command failed because the permission check did not respond, so nothing had been written.
- The free translation service is a translation memory: its quality varies for rare words and it can return a quota message.
- Deciding what a "tool failure" is: a missing word is not an outage, and a network error is not a missing word, and the model must be able to tell them apart later.

## Solutions

- Wrote the files individually and re-ran the whole suite before committing.
- The translation function checks the response status, the quota flag and an empty result, and returns a clear error instead of a doubtful text. The limitation is documented in `PROJECT.md`.
- Introduced three error types (`invalid_input`, `not_found`, `unavailable`) so that the later agent can decide whether to retry, correct arguments or report that the data does not exist.

## What I Learned

- How to design tool-style functions: validate arguments first, return structured results, never raise for expected failures.
- How to test code that calls web services: inject the fetch function and the opener so tests are deterministic and offline.
- How to write a JSON store safely: write to a temporary file and replace the original, and do not overwrite a file that cannot be parsed.
- How the same error categories will be used in Week 13 when tool results are sent back to the model.

## Next Week

Week 13: describe the four functions as tool schemas for OpenAI function calling, let the model choose the tool and its arguments, validate the arguments in the dispatcher, execute the tool, return the result to the model and produce an answer based on it. Also support requests that need no tool, and add tests with a scripted mock model.
