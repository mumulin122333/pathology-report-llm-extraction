"""Compare structured predictions with reference annotations."""

from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .scoring import clean_value, load_metadata, score_case

METRICS = ("scalar", "mol_f1", "ihc_f1", "overall")


def case_key(path: Path, key_mode: str) -> str:
    """Return the case key for a JSON file."""
    if key_mode == "report_id":
        return clean_value(load_metadata(path).get("report_id", "")).upper()
    return path.stem.upper()


def index_directories(
    directories: Iterable[str | Path],
    key_mode: str,
) -> tuple[dict[str, Path], list[str]]:
    """Index JSON files in one or more directories."""
    indexed: dict[str, Path] = {}
    duplicates: list[str] = []
    for directory_value in directories:
        directory = Path(directory_value)
        if not directory.is_dir():
            raise ValueError(f"not a directory: {directory}")
        for path in sorted(directory.glob("*.json")):
            try:
                key = case_key(path, key_mode)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if not key:
                continue
            if key in indexed:
                duplicates.append(key)
                continue
            indexed[key] = path
    return indexed, duplicates


def evaluate_directories(
    reference_dirs: Iterable[str | Path],
    prediction_dirs: Iterable[str | Path],
    *,
    key_mode: str = "filename",
    exclude_cases: Iterable[str] = (),
    exclude_fields: Iterable[str] = (),
    normalize_grade: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Score every case found in both the reference and prediction sets."""
    references, reference_duplicates = index_directories(reference_dirs, key_mode)
    predictions, prediction_duplicates = index_directories(prediction_dirs, key_mode)
    excluded = {str(value).strip().upper() for value in exclude_cases if str(value).strip()}

    shared = sorted(set(references) & set(predictions))
    keys = [key for key in shared if key not in excluded]
    rows: list[dict[str, Any]] = []
    invalid: list[dict[str, str]] = []

    for key in keys:
        try:
            reference = load_metadata(references[key])
            prediction = load_metadata(predictions[key])
            scores = score_case(reference, prediction, exclude_fields, normalize_grade)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            invalid.append({"case": key, "error": str(error)})
            continue
        rows.append({"case": key, **scores})

    summary: dict[str, Any] = {
        "reference_files": len(references),
        "prediction_files": len(predictions),
        "paired": len(shared),
        "excluded": len(set(shared) & excluded),
        "scored": len(rows),
        "reference_only": len(set(references) - set(predictions)),
        "prediction_only": len(set(predictions) - set(references)),
        "reference_duplicates": len(reference_duplicates),
        "prediction_duplicates": len(prediction_duplicates),
        "invalid": invalid,
    }
    for metric in METRICS:
        summary[metric] = (
            sum(float(row[metric]) for row in rows) / len(rows) if rows else 0.0
        )
    return rows, summary


def write_csv(path_value: str | Path, rows: list[dict[str, Any]]) -> None:
    """Write per-case scores."""
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=("case", *METRICS))
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: round(value, 4) if isinstance(value, float) else value
                    for key, value in row.items()
                }
            )


def write_summary(path_value: str | Path, summary: dict[str, Any]) -> None:
    """Write the aggregate result as JSON."""
    path = Path(path_value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference-dir",
        action="append",
        required=True,
        help="directory containing reference JSON; repeat for multiple directories",
    )
    parser.add_argument(
        "--prediction-dir",
        action="append",
        required=True,
        help="directory containing prediction JSON; repeat for multiple directories",
    )
    parser.add_argument(
        "--key",
        choices=("filename", "report_id"),
        default="filename",
        help="pair files by full filename stem or metadata.report_id",
    )
    parser.add_argument(
        "--exclude-cases",
        default="",
        help="comma-separated case keys to omit",
    )
    parser.add_argument(
        "--exclude-fields",
        default="",
        help="comma-separated dotted scalar paths to omit",
    )
    parser.add_argument(
        "--normalize-grade",
        action="store_true",
        help="treat numeric and Roman grade values as equivalent",
    )
    parser.add_argument("--output-csv", help="write per-case scores to CSV")
    parser.add_argument("--output-json", help="write the aggregate summary to JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        rows, summary = evaluate_directories(
            args.reference_dir,
            args.prediction_dir,
            key_mode=args.key,
            exclude_cases=args.exclude_cases.split(","),
            exclude_fields={
                value.strip() for value in args.exclude_fields.split(",") if value.strip()
            },
            normalize_grade=args.normalize_grade,
        )
    except ValueError as error:
        parser.error(str(error))

    print(
        f"reference files {summary['reference_files']:>5}   "
        f"prediction files {summary['prediction_files']:>5}"
    )
    print(
        f"paired          {summary['paired']:>5}   "
        f"scored          {summary['scored']:>5}"
    )
    if summary["excluded"]:
        print(f"excluded        {summary['excluded']:>5}")
    if summary["reference_only"] or summary["prediction_only"]:
        print(
            f"unpaired         reference-only {summary['reference_only']}   "
            f"prediction-only {summary['prediction_only']}"
        )
    if summary["reference_duplicates"] or summary["prediction_duplicates"]:
        print(
            "duplicates       "
            f"reference {summary['reference_duplicates']}   "
            f"prediction {summary['prediction_duplicates']}"
        )
    if summary["invalid"]:
        print(f"invalid          {len(summary['invalid']):>5}")

    if not rows:
        print("\nNothing scored. Check the directories and pairing mode.")
        return 1

    print("\nmetric         score")
    for metric in METRICS:
        print(f"{metric:<12}{summary[metric]:>8.4f}")

    if args.output_csv:
        write_csv(args.output_csv, rows)
        print(f"\nper-case CSV: {args.output_csv}")
    if args.output_json:
        write_summary(args.output_json, summary)
        print(f"summary JSON: {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
