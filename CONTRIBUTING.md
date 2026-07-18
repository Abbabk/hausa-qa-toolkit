# Contributing

Thank you for helping improve HausaQA.

## Clean-room requirement

Contributions must be authored from public knowledge or fresh synthetic examples. Do not submit private data, client text, proprietary glossaries, screenshots, prompts, credentials, confidential workflows, or material copied from restricted systems. When provenance is uncertain, leave the material out.

By contributing, you affirm that you have the right to provide the contribution under the MIT license.

## Development setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest --cov
ruff check .
python scripts/evaluate.py
```

## Change expectations

- Add behavioral tests for every rule change.
- Keep adapters thin and checks independently testable.
- Use stable issue codes and document severity changes.
- Add only synthetic, reviewable fixtures.
- Document conservative behavior and known ambiguity.
- Keep core-engine coverage at or above 85 percent.

A pull request should explain the problem, the rule boundary, fixture provenance, tests run, and compatibility impact.
