"""Load model endpoint settings from the packaged registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGISTRY_PATH = Path(__file__).with_name("models.json")


def load_registry(path: str | Path | None = None) -> dict[str, Any]:
    registry_path = Path(path) if path else REGISTRY_PATH
    with registry_path.open(encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry.get("models"), dict) or not registry["models"]:
        raise ValueError("model registry must contain a non-empty 'models' object")
    return registry


def get_model(model_key: str, path: str | Path | None = None) -> dict[str, Any]:
    registry = load_registry(path)
    try:
        model = registry["models"][model_key]
    except KeyError as error:
        choices = ", ".join(sorted(registry["models"]))
        raise ValueError(f"unknown model {model_key!r}; choose from: {choices}") from error
    return {**registry.get("decoding", {}), **model}
