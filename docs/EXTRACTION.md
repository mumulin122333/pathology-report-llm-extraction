# Extraction

The extraction command reads one UTF-8 text file and sends it to an
OpenAI-compatible chat-completions endpoint. The endpoint must already be
serving the selected model.

```bash
pathology-report-extract \
  --model qwen38_27b \
  --language en \
  --input /secure/path/report.txt \
  --output /secure/path/prediction.json
```

Use `--language ja` for Japanese source text. Both profiles produce the schema
documented in [SCHEMA.md](SCHEMA.md).

## Model selection

List the configured model keys with:

```bash
pathology-report-extract --list-models
```

`--model` selects the served model name, endpoint, decoding settings, and any
chat-template options from `extraction/models.json`. Use `--base-url` and
`--served-model` when the endpoint differs from the registry default.

## Direct output

The command writes the model's schema-shaped JSON. Parsing removes surrounding
prose or a Markdown code fence and selects the last valid schema-shaped JSON
block. It does not add findings, fill fields with rules, remove markers, or
translate the report.

Every output leaf must be a string. Invalid or incomplete JSON is rejected
instead of being silently repaired.

## Credentials

Local endpoints usually do not require a key. For an authenticated compatible
endpoint, set `OPENAI_API_KEY` or pass `--api-key`. Do not commit credentials.
