# Data policy

This repository contains code, documentation, empty templates, and at most two
approved public demo cases: one English report and one Japanese report. A demo
may include only the de-identified source text and its direct extraction JSON.
Do not commit any other clinical text or case-level data.

Keep the following outside the repository:

- source reports
- reference annotations
- completed few-shot examples or prompts containing report text
- translations
- model responses and parsed predictions
- evaluation CSV and JSON outputs
- logs containing input text or model responses
- case identifiers and crosswalks

## Demo exception

Before adding either public demo, obtain approval from the data owner and
review both the report and extracted JSON. Remove or generalize identifying
information, including:

- names and initials
- patient, specimen, accession, encounter, and record numbers
- dates and contact details
- clinicians, organizations, locations, and internal systems
- barcodes, URLs, filenames, and other unique codes
- rare free-text details that could identify a person when combined

Use a repository-only identifier such as `demo-en-001` or `demo-ja-001`. The
extracted JSON must not reintroduce anything removed from the report. Do not use
either public demo as a few-shot example unless that use is separately intended
and documented.

De-identification is a review process, not a search-and-replace step. Follow the
applicable institutional, legal, and ethics requirements before publication.

The default `data/`, `outputs/`, and `logs/` paths are ignored by Git. This is a
convenience guard, not a complete privacy control. Files placed elsewhere may
still be staged.

Before pushing, check:

```bash
git status --short
git diff --cached --name-only
git diff --cached
```

Review the staged file contents, not only their names. If sensitive material was
committed at any point, removing it in a later commit is insufficient because it
remains in Git history. Rewrite the history or recreate the repository before
publication.
