# Data policy

This repository contains code and documentation only. Do not commit clinical
text or derived case-level data.

Keep the following outside the repository:

- source reports
- reference annotations
- prompts or few-shot examples containing report text
- translations
- model responses and parsed predictions
- evaluation CSV and JSON outputs
- logs containing input text or model responses
- case identifiers and crosswalks

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
