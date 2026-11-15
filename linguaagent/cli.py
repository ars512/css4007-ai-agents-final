"""Command-line interface: `python -m linguaagent.cli "your question"` or interactive mode."""
from __future__ import annotations

import sys

from .config import get_settings
from .errors import LinguaAgentError
from .llm_client import LLMClient
from .validation import validate_user_message


def ask(client: LLMClient, message: str) -> str:
    """Validate the message, call the model, and return the answer text."""
    cleaned = validate_user_message(message)
    return client.chat([{"role": "user", "content": cleaned}])


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        client = LLMClient(get_settings())
        if args:
            print(ask(client, " ".join(args)))
            return 0
        print("LinguaAgent. Type a question, or 'exit' to quit.")
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print()
                return 0
            if line.strip().lower() in {"exit", "quit"}:
                return 0
            try:
                print(ask(client, line))
            except LinguaAgentError as exc:
                print(f"Error: {exc}")
    except LinguaAgentError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
