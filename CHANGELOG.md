# Changelog

All notable changes follow semantic versioning.

## [Unreleased]

### Fixed

- Reject empty bilingual inputs and report empty targets as critical findings.
- Return controlled CLI usage errors for malformed XLIFF and glossary data.
- Validate public segment values, JSON references, and glossary fields at their boundaries.
- Accept UTF-8 byte-order marks in JSON and normalize Unicode during glossary matching.
- Document the validated input and glossary behavior.

## [0.1.0] - 2026-07-18

### Added

- Placeholder and inline-tag inventory, order, syntax, and corruption checks.
- Conservative Hausa orthography damage checks.
- TSV and JSON glossary validation with approved and forbidden terms.
- MQM-style report model with text and JSON output.
- CSV, TSV, JSON, XLIFF 1.2, and XLIFF 2.0 adapters.
- `hausaqa check` CLI with documented exit codes and severity thresholds.
- Synthetic evaluation corpus and reproducible scoring script.
- Behavioral test suite, coverage threshold, lint configuration, and project documentation.
