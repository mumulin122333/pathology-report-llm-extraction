# Pathology Report LLM Extraction and Evaluation

This repository provides command-line tools for extracting structured data from
pathology reports and comparing the generated JSON with reference annotations.
The extraction command supports English and Japanese reports and uses the same
prompt and decoding settings across the configured models.

The reports used as few-shot examples in the experiments are not distributed.
Users can run zero-shot extraction or provide their own examples with the
included template.

## Install

Python 3.10 or newer is required. The package has no runtime dependencies.

```bash
pip install -e .
```

## Extract a report

The selected model must already be available through an OpenAI-compatible
chat-completions endpoint. List the configured models with:

```bash
pathology-report-extract --list-models
```

Run direct extraction on an English report:

```bash
pathology-report-extract \
  --model qwen38_27b \
  --language en \
  --input /path/to/report.txt \
  --output /path/to/prediction.json
```

Use `--language ja` for a Japanese report. The `--model` flag selects the model
name, endpoint, decoding settings, and model-specific request options from
[`extraction/models.json`](extraction/models.json). Endpoint values can be
overridden with `--base-url` and `--served-model`.

The saved JSON is the direct model result after schema-shaped JSON parsing. The
extractor does not translate the input, add findings with rules, or remove
markers from the response.

See [Extraction](docs/EXTRACTION.md) and [Models](docs/MODELS.md).

## Add your own few-shot examples

Copy the template outside the repository and replace its placeholders:

```bash
cp examples/fewshot.example.json /secure/path/fewshot.json
```

Pass the completed file to extraction:

```bash
pathology-report-extract \
  --model qwen38_27b \
  --language en \
  --input /path/to/report.txt \
  --output /path/to/prediction.json \
  --few-shot /secure/path/fewshot.json
```

Without `--few-shot`, extraction runs zero-shot. See
[Few-shot input](docs/FEW_SHOT.md).

## Evaluate predictions

Place reference annotations and predictions in separate directories, then run:

```bash
pathology-report-score \
  --reference-dir /path/to/annotations \
  --prediction-dir /path/to/predictions \
  --output-csv /path/to/scores.csv \
  --output-json /path/to/summary.json
```

Each case receives `scalar`, `mol_f1`, `ihc_f1`, and `overall` scores.

```text
overall = 0.50 * scalar + 0.25 * mol_f1 + 0.25 * ihc_f1
```

See [Input files](docs/INPUTS.md), [JSON schema](docs/SCHEMA.md),
[Scoring](docs/SCORING.md), and [Output](docs/OUTPUTS.md).

## Demo reports

One reviewed English report and one reviewed Japanese report are planned as
direct-extraction demos. They will be added only after de-identification and
publication approval. Demo reports are not used as few-shot examples or
included in evaluation results.

See [`examples/README.md`](examples/README.md) for the expected files.

## Data policy

Do not commit reports, annotations, completed few-shot files, model responses,
or logs unless they are explicitly approved for public release. The future demo
files are the only planned report-level exception.

See [Data policy](docs/DATA_POLICY.md) for the release checklist.

## License

MIT. See [LICENSE](LICENSE).
