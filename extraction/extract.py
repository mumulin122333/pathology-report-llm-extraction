"""Extract structured JSON from one UTF-8 pathology report."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Protocol

from .client import ChatCompletionsClient
from .models import get_model, load_registry
from .parsing import parse_model_output
from .prompts import build_messages, load_few_shots


class CompletionClient(Protocol):
    def complete(self, messages: list[dict[str, str]]) -> str: ...


def extract_report(
    report_text: str,
    report_id: str,
    language: str,
    client: CompletionClient,
    few_shots: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Call the model and parse its direct JSON response."""
    messages = build_messages(report_id, report_text, language, few_shots)
    return parse_model_output(client.complete(messages))


def build_parser() -> argparse.ArgumentParser:
    registry = load_registry()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(registry["models"]), help="model key")
    parser.add_argument("--list-models", action="store_true", help="print configured models")
    parser.add_argument("--language", choices=("en", "ja"), help="report language")
    parser.add_argument("--input", help="UTF-8 report text file")
    parser.add_argument("--output", help="destination JSON file")
    parser.add_argument("--report-id", help="output report_id; defaults to input filename stem")
    parser.add_argument("--few-shot", help="user-supplied few-shot JSON")
    parser.add_argument("--base-url", help="override the model's OpenAI-compatible base URL")
    parser.add_argument("--served-model", help="override the served model name")
    parser.add_argument("--api-key", help="API key; defaults to OPENAI_API_KEY")
    parser.add_argument("--max-tokens", type=int, help="override the registry token limit")
    parser.add_argument("--timeout", type=float, default=600)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    registry = load_registry()

    if args.list_models:
        for key, spec in registry["models"].items():
            print(f"{key:<20} {spec['label']:<28} {spec['hf_id']}")
        return 0

    missing = [name for name in ("model", "language", "input", "output") if not getattr(args, name)]
    if missing:
        parser.error(f"required unless --list-models: {', '.join('--' + name for name in missing)}")

    input_path = Path(args.input)
    if not input_path.is_file():
        parser.error(f"input is not a file: {input_path}")
    report_text = input_path.read_text(encoding="utf-8").strip()
    if not report_text:
        parser.error("input report is empty")

    try:
        spec = get_model(args.model)
        few_shots = load_few_shots(args.few_shot)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    client = ChatCompletionsClient(
        base_url=args.base_url or spec["base_url"],
        served_model=args.served_model or spec["served_model"],
        api_key=args.api_key or os.environ.get("OPENAI_API_KEY"),
        timeout=args.timeout,
        max_tokens=args.max_tokens or spec["max_tokens"],
        temperature=spec["temperature"],
        seed=spec["seed"],
        extra_body=spec.get("extra_body"),
    )
    try:
        result = extract_report(
            report_text,
            args.report_id or input_path.stem,
            args.language,
            client,
            few_shots,
        )
    except (RuntimeError, ValueError) as error:
        parser.exit(1, f"extraction failed: {error}\n")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
