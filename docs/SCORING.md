# Scoring

The evaluator calculates four values for each paired case and reports the
macro-average across all successfully scored cases.

```text
overall = 0.50 * scalar + 0.25 * mol_f1 + 0.25 * ihc_f1
```

## Scalar score

The annotation metadata is flattened into dotted field paths, excluding lists.
Each annotated field is compared with the value at the same path in the
prediction.

An exact normalized match receives `1.0`. Other non-empty values receive the
similarity ratio calculated by Python's `difflib.SequenceMatcher`. If only one
side is empty, the score is `0.0`. The case-level scalar score is the mean over
all included annotation fields.

## Marker F1

Molecular and immunohistochemistry lists are evaluated independently. Marker
names are lowercased and compared without spaces or hyphens. Repeated marker
names in a prediction collapse to one entry.

For each list:

```text
precision = matched markers / predicted markers
recall    = matched markers / annotated markers
F1        = 2 * precision * recall / (precision + recall)
```

Status, method, and result values do not contribute to the overall score.

## Normalization

Before comparison, the scorer:

- lowercases text
- removes leading and trailing whitespace
- collapses repeated internal whitespace
- converts full-width percent signs to `%`
- treats empty values and common missing-value phrases as `not specified`
- treats named necrosis subtypes as evidence that necrosis is present

Use `--normalize-grade` when numeric and Roman grade values should be treated as
equivalent.

When both marker lists are empty, marker F1 is `0.0`. This preserves the metric
definition used by the tool and prevents empty lists from inflating the score.

## Exclusions

Exclude fields that were copied into the output, were not available to the
model, or should not be part of the target task. Exclude cases that appeared in
the prompt or otherwise belong to the development set.

The command prints the number of excluded and unpaired cases. These counts
should be reported with the aggregate score.

## Interpretation

The overall value is a project-specific weighted metric, not a clinical
performance claim. Comparisons are meaningful only when models use the same
schema, cases, exclusions, prompts, decoding settings, and parsing rules.
