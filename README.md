# HausaQA

HausaQA is a clean-room, MIT-licensed localization QA toolkit for Hausa bilingual files. It finds placeholder and inline-tag damage, conservative orthography problems, and terminology drift, then emits MQM-style findings as text or JSON.

HausaQA is authored by Abba Bello Kanwa of [Hausa AI Studio](https://hausaai.studio).

## Features

- ICU placeholders such as `{name}` and typed forms such as `{count, number}`
- printf placeholders such as `%s`, `%d`, and `%1$s`
- mustache placeholders such as `{{person}}`
- XML/HTML tags and generic numbered inline tags such as `[1]...[/1]`
- missing, extra, reordered, malformed, and likely corrupted token detection
- conservative Hausa checks for hooked-letter loss, apostrophe damage, ASCII fallbacks, mixed scripts, repeated spaces, replacement characters, and sentence capitalization
- TSV or JSON glossaries with approved terms and forbidden variants
- CSV, TSV, JSON, XLIFF 1.2, and XLIFF 2.0 input
- human-readable and machine-readable reports
- reproducible synthetic evaluation corpus

## Quickstart

HausaQA requires Python 3.11 or later.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
hausaqa check fixtures/cli-demo.tsv --glossary fixtures/glossary.tsv --format text
```

Real output from the included fixture:

```text
HausaQA 0.1.0: 2 segment(s), 3 issue(s)
Summary: critical=1 major=1 minor=1
[critical] demo-1 placeholder/missing: Missing 1 occurrence(s) of '{name}'
[minor] demo-2 orthography/double_space: Target contains repeated spaces
[major] demo-2 terminology/approved_term_missing: Expected approved term 'asusu' for 'account'
```

A critical finding makes `hausaqa check` exit with status 1 by default. To fail on major findings too:

```bash
hausaqa check pairs.xliff --fail-on major
```

For JSON suitable for automation:

```bash
hausaqa check pairs.json --format json
```

## Input formats

### CSV and TSV

Use `source` and `target` columns. An optional `reference` column supplies stable segment identifiers. Without a header, the first two columns are treated as source and target.

### JSON

Use an object keyed by segment identifier:

```json
{
  "welcome": {"source": "Welcome, {name}!", "target": "Barka da zuwa, {name}!"}
}
```

A list of objects with `source`, `target`, and optional `reference` fields is also accepted.

### XLIFF

XLIFF 1.2 `trans-unit` and XLIFF 2.0 `unit/segment` pairs are supported. Inline XML elements are converted to stable token text before engine checks.

## Glossary format

TSV columns are source term, approved Hausa term, and optional pipe-separated forbidden variants:

```text
account\tasusu\tlissafi|akwati
```

JSON glossaries are lists of objects with `source_term`, `approved_term`, and optional `forbidden_variants`.

## Exit codes

- `0`: input was read and no issue met the failure threshold
- `1`: at least one issue met the failure threshold
- `2`: invalid arguments, unsupported input, unreadable file, or malformed data

## Development

```bash
python -m pip install -e '.[dev]'
python -m pytest --cov
ruff check .
python scripts/evaluate.py
```

See [architecture](docs/architecture.md), [evaluation](docs/evaluation.md), [provenance](docs/provenance.md), [contributing](CONTRIBUTING.md), [security](SECURITY.md), and [release process](docs/release.md).
