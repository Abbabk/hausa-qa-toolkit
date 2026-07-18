# Evaluation

## Purpose

The evaluation harness measures segment-level precision and recall for the placeholder, orthography, and terminology categories. It is a reproducibility aid, not a claim of broad linguistic accuracy.

## Corpus

`fixtures/evaluation.json` contains 12 entirely synthetic bilingual segments written for this repository. Each segment lists the expected issue categories. `fixtures/glossary.tsv` is also synthetic.

## Run

```bash
python scripts/evaluate.py
```

The script runs the same public engine used by the CLI and prints true positives, false positives, false negatives, precision, and recall for each category.

## Version 0.1.0 baseline

```text
Synthetic evaluation: 12 segments
placeholder: precision=1.0000 recall=1.0000 tp=3 fp=0 fn=0
orthography: precision=1.0000 recall=1.0000 tp=3 fp=0 fn=0
terminology: precision=0.6667 recall=1.0000 tp=2 fp=1 fn=0
```

The terminology false positive is retained because exact whole-term matching does not understand Hausa inflection. It makes the limitation measurable instead of hiding it. A future morphology-aware change should improve precision without reducing recall and should add new synthetic cases.

## Interpretation limits

The corpus is small, synthetic, and category-level. It does not measure fluent translation quality, dialect coverage, domain terminology, or performance on private production data. Public evaluation should expand through independently contributed clean-room fixtures.
