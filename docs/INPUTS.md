# Input files

The evaluator reads reference annotations and model predictions from separate
directories. Input directories may be anywhere on the local filesystem and
should not be committed to this repository.

## JSON files

Each directory contains one JSON file per case. The evaluator accepts either a
bare metadata object:

```json
{
  "report_id": "case-001",
  "diagnosis": {
    "who_grade": "not specified"
  }
}
```

or the wrapped form used by the extraction pipeline:

```json
[
  {
    "metadata": {
      "report_id": "case-001",
      "diagnosis": {
        "who_grade": "not specified"
      }
    }
  }
]
```

The reference and prediction for a case must have the same filename unless they
are paired by `report_id`.

## Pairing cases

The default mode uses the complete filename stem. For example, two files named
`case-001.json` are both keyed as `CASE-001`.

```bash
pathology-report-score \
  --reference-dir /secure/annotations \
  --prediction-dir /secure/predictions
```

To pair files using `metadata.report_id`, pass:

```bash
pathology-report-score \
  --reference-dir /secure/annotations \
  --prediction-dir /secure/predictions \
  --key report_id
```

Case keys are compared without regard to letter case. Duplicate keys are
reported and ignored after the first occurrence.

## Multiple directories

Repeat an argument when a set is stored in more than one directory:

```bash
pathology-report-score \
  --reference-dir /secure/annotations-part-a \
  --reference-dir /secure/annotations-part-b \
  --prediction-dir /secure/predictions
```

Only keys found in both the annotation and prediction sets are scored. Counts
for unpaired, duplicate, empty, and unreadable files are printed with the
result.

## Exclusions

Use `--exclude-cases` with a comma-separated list of case keys to omit cases.
This is useful when an example was included in a model prompt and must not be
evaluated.

Use `--exclude-fields` with comma-separated dotted field paths to omit fields
from the scalar metric. No fields are excluded by default.

```bash
pathology-report-score \
  --reference-dir /secure/annotations \
  --prediction-dir /secure/predictions \
  --exclude-cases case-001,case-002 \
  --exclude-fields clinical_context.patient_age,report_id
```
