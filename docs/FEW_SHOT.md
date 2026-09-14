# Few-shot input

The reports used as few-shot examples in the experiments are not distributed.
Users can supply their own examples with `--few-shot`.

Copy the template to a location outside the repository:

```bash
cp examples/fewshot.example.json /secure/path/fewshot.json
```

Replace every placeholder before use. Each entry requires:

- `report_id`
- `report`
- `output`, using the extraction schema

```bash
pathology-report-extract \
  --model qwen38_27b \
  --language en \
  --input /secure/path/report.txt \
  --output /secure/path/prediction.json \
  --few-shot /secure/path/fewshot.json
```

Without `--few-shot`, extraction is zero-shot. Results from a user-supplied
prompt are not expected to reproduce results obtained with a different set of
examples.

Any case used in a few-shot prompt should be excluded from evaluation with
`--exclude-cases`.
