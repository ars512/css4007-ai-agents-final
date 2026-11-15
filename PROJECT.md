# LinguaAgent

A tool-using AI agent for learning English, Russian and Kazakh vocabulary (course project, level C).
See [reports/proposal.md](reports/proposal.md) for the full plan.

**Status (Week 11):** the application can send a validated user message to an OpenAI model and
print the answer, with clear errors for bad input and API failures. Tools (dictionary, translation,
flashcards) and tool selection by the model are planned for Weeks 12–14.

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
| `linguaagent/cli.py` | command-line entry point |
| `tests/test_llm_client.py` | project tests (mocked LLM) |

## AI assistant disclosure

The code and documents in this repository were written with the help of an AI coding assistant
(Claude Code). I review, run and test the generated code and am responsible for explaining it.
