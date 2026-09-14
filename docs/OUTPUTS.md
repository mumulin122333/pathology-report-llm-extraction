# Output

The evaluator prints file counts followed by aggregate scores.

```text
reference files   100   prediction files   100
paired            100   scored             100

metric         score
scalar        0.0000
mol_f1        0.0000
ihc_f1        0.0000
overall       0.0000
```

The values above only illustrate the output format. They are not experimental
results.

Warnings are printed for:

- keys present only in annotations or predictions
- duplicate case keys
- unreadable JSON
- empty metadata objects

## Per-case CSV

Pass `--output-csv` to write one row per scored case:

```bash
pathology-report-score \
  --reference-dir /secure/annotations \
  --prediction-dir /secure/predictions \
  --output-csv /secure/results/per-case.csv
```

The CSV contains:

| Column | Meaning |
|---|---|
| `case` | Matched case key |
| `scalar` | Mean scalar-field similarity |
| `mol_f1` | Molecular marker-name F1 |
| `ihc_f1` | Immunohistochemistry marker-name F1 |
| `overall` | Weighted overall score |

Scores are calculated at full precision and rounded to four decimal places only
when written for display.

Pass `--output-json` to save the aggregate metrics and validation counts in a
machine-readable JSON file.
