# Semester Week 11 Progress Report

## Completed Work

- Set up the Python development environment: virtual environment, `requirements.txt` (`openai`, `pytest`), `.env` / `.env.example` for the key and model name (the real `.env` is git-ignored).
- Integrated the OpenAI Chat Completions API (`gpt-4o-mini`) in `linguaagent/llm_client.py`. A system prompt tells the model to help with English, Russian and Kazakh vocabulary and to admit uncertainty instead of guessing.
- Implemented the first working request: `python -m linguaagent.cli "..."` sends a validated message to the model and prints the answer; interactive mode is also available.
- Added input validation (`linguaagent/validation.py`): message must be text, not empty, at most 1000 characters.
- Added error handling: authentication, rate limit, timeout, connection and generic API errors, as well as empty or malformed replies, become a clear `LLMError`; missing configuration raises `ConfigError`. The API key is never printed (`Settings.__repr__` hides it).
- Wrote 18 pytest cases that use a mocked OpenAI client, so they need no key or network.
- Wrote `PROJECT.md` (setup, run, test, layout) with the AI assistant disclosure.
- Disclosure: the code and documents were written with the help of an AI coding assistant (Claude Code); I ran the code against the real API, reviewed it and test it myself.

## Important Commits

- Commit hash: 75ac85f
- Description: Add OpenAI client wrapper with settings and error handling
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/75ac85f

- Commit hash: a18bd88
- Description: Add input validation and command-line interface
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/a18bd88

- Commit hash: 48add44
- Description: Add tests for validation, config and LLM error handling
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/48add44

- Commit hash: 3b95e4c
- Description: Document setup, usage and layout; add AI assistant disclosure
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/3b95e4c

## Current Functionality

The application answers free-form language questions through the real OpenAI API from the command line (for example "Say hello in Kazakh" returns "Сәлем!"). Empty or too long input is rejected before any model call, and API or configuration failures produce a readable error and exit code 1. There are no tools yet: the model answers from its own knowledge. Tools and tool selection are planned for Weeks 12–14.

## Problems Encountered

- The installed `openai` package (3.x) depends on `httpx2` instead of `httpx`, so the tests that build provider exceptions failed with `ModuleNotFoundError`.
- The first API key had been pasted into a chat and had to be replaced.
- The `.env` file was first created outside the project folder.

## Solutions

- The tests import `httpx2 as httpx` to construct the request and response objects for the error cases.
- The old key was revoked and a new one is stored only in the git-ignored `.env`; a search of the repository confirmed that no key is committed.
- Moved `.env` into the project root, where `config.py` looks for it.

## What I Learned

- How a Chat Completions request is built (system prompt plus messages) and how to read the reply.
- Which exceptions the OpenAI SDK raises for different failures and why they should be translated into application-level errors.
- How to make code testable with dependency injection: the client can be replaced by a fake object, so tests are deterministic and free.
- Why secrets must stay in environment files and out of logs and reprs.

## Next Week

Week 12: implement the core functions `lookup_word` (dictionary API), `translate_text` (translation API) and flashcard storage in a JSON file, with argument validation, structured results and error cases, and add tests for them with mocked HTTP.
