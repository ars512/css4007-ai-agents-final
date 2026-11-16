"""Run the tools directly (no LLM), e.g. `python -m linguaagent.tools_cli lookup resilient`."""
from __future__ import annotations

import argparse
import json
import sys

from .dictionary import lookup_word
from .flashcards import list_flashcards, save_flashcard
from .translation import translate_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="linguaagent.tools_cli", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("lookup", help="English dictionary lookup")
    p.add_argument("word")
    p = sub.add_parser("translate", help="translate between en, ru, kk")
    p.add_argument("text")
    p.add_argument("source_lang")
    p.add_argument("target_lang")
    p = sub.add_parser("save", help="save a flashcard")
    p.add_argument("word")
    p.add_argument("translation")
    p.add_argument("--example", default="")
    p = sub.add_parser("list", help="list saved flashcards")
    p.add_argument("--limit", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "lookup":
        result = lookup_word(args.word)
    elif args.command == "translate":
        result = translate_text(args.text, args.source_lang, args.target_lang)
    elif args.command == "save":
        result = save_flashcard(args.word, args.translation, args.example)
    else:
        result = list_flashcards(args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if "error" in result else 0


if __name__ == "__main__":
    sys.exit(main())
