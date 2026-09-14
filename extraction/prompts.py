"""English and Japanese zero-shot/few-shot prompt profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import SCHEMA

LANGUAGE_INSTRUCTIONS = {
    "en": "The source report is written in English.",
    "ja": (
        "The source report is written in Japanese. Interpret the Japanese text and "
        "write normalized schema values in English while preserving marker names, "
        "grades, and percentages."
    ),
}

SYSTEM = """You extract structured metadata from a pathology report.
Use only information stated in the report. Do not infer unstated findings.
Write "not specified" for a scalar field that is not stated and use an empty
list when no supported list item is stated.
Return only a JSON array containing one object with a metadata key.
Every leaf value must be a string. Do not add prose or Markdown."""


def load_few_shots(path: str | Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    with Path(path).open(encoding="utf-8") as handle:
        examples = json.load(handle)
    if not isinstance(examples, list):
        raise ValueError("few-shot file must contain a JSON array")
    for index, example in enumerate(examples):
        if not isinstance(example, dict):
            raise ValueError(f"few-shot example {index} must be an object")
        missing = {"report_id", "report", "output"} - set(example)
        if missing:
            raise ValueError(
                f"few-shot example {index} is missing: {', '.join(sorted(missing))}"
            )
        if "<" in str(example["report"]) and ">" in str(example["report"]):
            raise ValueError("replace the placeholders in the few-shot template before use")
    return examples


def user_message(report_id: str, report_text: str, language: str) -> str:
    try:
        language_instruction = LANGUAGE_INSTRUCTIONS[language]
    except KeyError as error:
        raise ValueError("language must be 'en' or 'ja'") from error
    return (
        f"{language_instruction}\n\n"
        "Extract metadata from the report using this schema:\n"
        f"{json.dumps(SCHEMA, ensure_ascii=False, indent=2)}\n\n"
        f"Report ID: {report_id}\n\n"
        f"<REPORT>\n{report_text}\n</REPORT>"
    )


def build_messages(
    report_id: str,
    report_text: str,
    language: str,
    few_shots: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    """Build one message sequence shared by every configured model."""
    messages: list[dict[str, str]] = []
    examples = few_shots or []
    for index, example in enumerate(examples):
        content = user_message(
            str(example["report_id"]), str(example["report"]), language
        )
        if index == 0:
            content = f"{SYSTEM}\n\n{content}"
        messages.append({"role": "user", "content": content})
        messages.append(
            {
                "role": "assistant",
                "content": json.dumps(example["output"], ensure_ascii=False),
            }
        )

    content = user_message(report_id, report_text, language)
    if not examples:
        content = f"{SYSTEM}\n\n{content}"
    messages.append({"role": "user", "content": content})
    return messages
