"""Metric primitives for structured pathology-report extraction."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

OVERALL_WEIGHTS = {
    "scalar": 0.50,
    "mol_f1": 0.25,
    "ihc_f1": 0.25,
}

MISSING_VALUES = {
    "",
    "not described",
    "not mentioned",
    "not specified",
    "not stated",
    "unknown",
}

NECROSIS_PRESENT = {
    "present",
    "focal necrosis",
    "palisading necrosis",
}

GRADE_MAP = {
    "1": "i",
    "2": "ii",
    "3": "iii",
    "4": "iv",
    "i": "i",
    "ii": "ii",
    "iii": "iii",
    "iv": "iv",
}

CONFIDENCE_SUFFIX = re.compile(r"\s*\*\*\*(?:0\.\d{2}|1\.00)\*\*\*\s*$")


def clean_value(value: Any) -> str:
    """Return the normalized string used for comparison."""
    if value is None:
        return ""
    text = CONFIDENCE_SUFFIX.sub("", str(value))
    text = text.strip().lower().replace("％", "%")
    return re.sub(r"\s+", " ", text)


def canonical_value(value: Any, normalize_grade: bool = False) -> str:
    """Normalize missing values and, optionally, numeric/Roman grades."""
    text = clean_value(value)
    if text in MISSING_VALUES:
        return "not specified"
    if normalize_grade:
        return GRADE_MAP.get(text, text)
    return text


def similarity(reference: Any, prediction: Any) -> float:
    """Compare two scalar values after basic text normalization."""
    reference_text = clean_value(reference)
    prediction_text = clean_value(prediction)
    if reference_text == prediction_text:
        return 1.0
    if not reference_text or not prediction_text:
        return 0.0
    return SequenceMatcher(None, reference_text, prediction_text).ratio()


def load_metadata(path: str | Path) -> dict[str, Any]:
    """Load a bare metadata object or a one-item wrapper containing metadata."""
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        if len(data) != 1:
            raise ValueError("expected a one-item JSON array")
        data = data[0]

    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")

    metadata = data.get("metadata", data)
    if not isinstance(metadata, dict) or not metadata:
        raise ValueError("metadata must be a non-empty JSON object")
    return metadata


def flatten_scalars(data: Mapping[str, Any], prefix: str = "") -> dict[str, str]:
    """Flatten nested mappings to dotted paths while skipping list values."""
    flattened: dict[str, str] = {}
    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            flattened.update(flatten_scalars(value, path))
        elif isinstance(value, list):
            continue
        else:
            flattened[path] = clean_value(value)
    return flattened


def field_score(
    field: str,
    reference: Any,
    prediction: Any,
    normalize_grade: bool = False,
) -> float:
    """Score one scalar field."""
    reference_value = canonical_value(reference, normalize_grade)
    prediction_value = canonical_value(prediction, normalize_grade)
    if field.endswith("necrosis"):
        if reference_value in NECROSIS_PRESENT and prediction_value in NECROSIS_PRESENT:
            return 1.0
    if reference_value == prediction_value:
        return 1.0
    return similarity(reference, prediction)


def scalar_score(
    reference: Mapping[str, Any],
    prediction: Mapping[str, Any],
    exclude_fields: Iterable[str] = (),
    normalize_grade: bool = False,
) -> float:
    """Return mean similarity over scalar fields present in the reference."""
    excluded = set(exclude_fields)
    reference_fields = flatten_scalars(reference)
    prediction_fields = flatten_scalars(prediction)
    scores = [
        field_score(
            field,
            reference_value,
            prediction_fields.get(field, ""),
            normalize_grade,
        )
        for field, reference_value in reference_fields.items()
        if field not in excluded
    ]
    return sum(scores) / len(scores) if scores else 0.0


def normalize_marker(value: Any) -> str:
    """Normalize a marker name for set comparison."""
    return clean_value(value).replace(" ", "").replace("-", "")


def marker_f1(
    reference_items: Any,
    prediction_items: Any,
    marker_key: str,
) -> float:
    """Return marker-name F1 for one list field."""
    reference_items = reference_items if isinstance(reference_items, list) else []
    prediction_items = prediction_items if isinstance(prediction_items, list) else []

    reference_markers = {
        normalize_marker(item.get(marker_key, ""))
        for item in reference_items
        if isinstance(item, Mapping) and normalize_marker(item.get(marker_key, ""))
    }
    prediction_markers = {
        normalize_marker(item.get(marker_key, ""))
        for item in prediction_items
        if isinstance(item, Mapping) and normalize_marker(item.get(marker_key, ""))
    }

    matched = len(reference_markers & prediction_markers)
    precision = matched / len(prediction_markers) if prediction_markers else 0.0
    recall = matched / len(reference_markers) if reference_markers else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def score_case(
    reference: Mapping[str, Any],
    prediction: Mapping[str, Any],
    exclude_fields: Iterable[str] = (),
    normalize_grade: bool = False,
) -> dict[str, float]:
    """Calculate all report-level metrics."""
    scalar = scalar_score(reference, prediction, exclude_fields, normalize_grade)
    mol_f1 = marker_f1(
        reference.get("molecular", []),
        prediction.get("molecular", []),
        "molecular_marker",
    )
    ihc_f1 = marker_f1(
        reference.get("immunohistochemistry", []),
        prediction.get("immunohistochemistry", []),
        "IHC_marker",
    )
    overall = (
        OVERALL_WEIGHTS["scalar"] * scalar
        + OVERALL_WEIGHTS["mol_f1"] * mol_f1
        + OVERALL_WEIGHTS["ihc_f1"] * ihc_f1
    )
    return {
        "scalar": scalar,
        "mol_f1": mol_f1,
        "ihc_f1": ihc_f1,
        "overall": overall,
    }
