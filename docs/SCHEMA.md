# JSON schema

The evaluator expects a metadata object containing scalar fields and two lists:
`molecular` and `immunohistochemistry`. Every leaf value should be a string.

This empty example shows the accepted structure without containing report data:

```json
[
  {
    "metadata": {
      "report_id": "case-001",
      "clinical_context": {
        "patient_age": "not specified",
        "lesion_location": "not specified",
        "lesion_laterality": "not specified"
      },
      "diagnosis": {
        "integrated_diagnosis": "not specified",
        "who_entity": "not specified",
        "who_grade": "not specified",
        "molecular_entity": "not specified",
        "diagnostic_certainty": "not specified"
      },
      "histopathology": {
        "growth_pattern": "not specified",
        "necrosis": "not specified",
        "microvascular_proliferation": "not specified",
        "cellular_morphology": "not specified"
      },
      "proliferation": {
        "ki67_index": "not specified"
      },
      "molecular": [],
      "immunohistochemistry": []
    }
  }
]
```

## Scalar fields

Nested dictionaries are flattened into dotted paths during scoring. The
reference annotation determines which scalar paths are evaluated. Extra scalar
fields found only in a prediction do not add points or penalties.

Common values that indicate missing information are normalized to
`not specified`. Fields copied from an external table rather than extracted by
the model should be excluded with `--exclude-fields`.

## Molecular findings

Each item in `molecular` may contain:

```json
{
  "molecular_marker": "marker name",
  "molecular_status": "result",
  "molecular_method": "method"
}
```

The molecular metric is F1 over normalized marker names. Status and method do
not contribute to the overall score.

## Immunohistochemistry findings

Each item in `immunohistochemistry` may contain:

```json
{
  "IHC_marker": "marker name",
  "IHC_result": "result"
}
```

The immunohistochemistry metric is F1 over normalized marker names.

## Custom schemas

The scalar scorer accepts additional nested fields without code changes. List
fields other than `molecular` and `immunohistochemistry` are ignored by the
current metrics. Supporting another scored list requires a corresponding
comparison function in `evaluation/scoring.py`.
