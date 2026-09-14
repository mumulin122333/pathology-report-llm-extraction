# Pathology Report LLM Evaluation

This repository provides command-line tools for evaluating structured data
extracted from pathology reports. It compares model-generated JSON with
reference annotations and reports per-case and aggregate scores.

No reports, annotations, few-shot examples, translations, or model outputs are
included. All data must be supplied locally by the user.

## Install

Python 3.10 or newer is required. The package has no runtime dependencies.

```bash
pip install -e .
```

## Run an evaluation

Place reference annotations and predictions in separate directories outside the
repository, then run:

```bash
pathology-report-score \
  --reference-dir /path/to/annotations \
  --prediction-dir /path/to/predictions
```

To save per-case scores:

```bash
pathology-report-score \
  --reference-dir /path/to/annotations \
  --prediction-dir /path/to/predictions \
  --output-csv /path/to/scores.csv \
  --output-json /path/to/summary.json
```

The command reports how many files were found, paired, skipped, or rejected as
invalid before printing the aggregate metrics.

## Input

Annotations and predictions use the same JSON schema. Files are paired by their
complete filename stem by default. They can instead be paired with
`metadata.report_id` by passing `--key report_id`.

Use `--reference-dir` or `--prediction-dir` more than once when files are split
across multiple directories. Use `--exclude-cases` for case identifiers that
should not be scored, and `--exclude-fields` for fields that should not
contribute to the scalar score.

See [Input files](docs/INPUTS.md) and [JSON schema](docs/SCHEMA.md) for details.

## Scores

Each case receives four values:

- `scalar`: mean similarity over non-list fields
- `mol_f1`: marker-name F1 for molecular findings
- `ihc_f1`: marker-name F1 for immunohistochemistry findings
- `overall`: weighted combination of the three metrics

```text
overall = 0.50 * scalar + 0.25 * mol_f1 + 0.25 * ihc_f1
```

Aggregate scores are macro-averages over the cases that were successfully
paired and parsed. The exact normalization and matching rules are documented in
[Scoring](docs/SCORING.md).

## Data policy

The repository is intended to contain code and documentation only. Keep source
reports, annotations, prompts containing report text, translations, logs, and
generated outputs outside the repository. The included `.gitignore` blocks the
default local data and output paths, but users should still inspect staged files
before every push.

See [Data policy](docs/DATA_POLICY.md) for the release checklist.

## Documentation

- [Input files](docs/INPUTS.md)
- [JSON schema](docs/SCHEMA.md)
- [Scoring](docs/SCORING.md)
- [Output](docs/OUTPUTS.md)
- [Data policy](docs/DATA_POLICY.md)

## License

MIT. See [LICENSE](LICENSE).
