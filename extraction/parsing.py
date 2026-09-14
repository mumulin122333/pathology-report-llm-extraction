"""Parse a schema-shaped JSON object from a model response."""

from __future__ import annotations

import json
import re
from typing import Any


def _metadata(value: Any) -> dict[str, Any] | None:
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
    if not isinstance(value, dict):
        return None
    metadata = value.get("metadata")
    return metadata if isinstance(metadata, dict) else None


def _validate_leaves(value: Any, path: str = "metadata") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _validate_leaves(child, f"{path}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            _validate_leaves(child, f"{path}[{index}]")
        return
    if not isinstance(value, str):
        raise ValueError(f"{path} must be a string")


def parse_model_output(text: str) -> list[dict[str, Any]]:
    """Return the last valid metadata result found in a model response."""
    cleaned = re.sub(r"^\s*```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    decoder = json.JSONDecoder()
    candidates: list[Any] = []
    for match in re.finditer(r"[\[{]", cleaned):
        try:
            candidate, _ = decoder.raw_decode(cleaned[match.start():])
        except json.JSONDecodeError:
            continue
        if _metadata(candidate) is not None:
            candidates.append(candidate)
    if not candidates:
        raise ValueError("model response did not contain schema-shaped JSON")

    selected = candidates[-1]
    metadata = _metadata(selected)
    assert metadata is not None
    _validate_leaves(metadata)
    if isinstance(selected, dict):
        return [selected]
    return selected
