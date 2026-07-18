#!/usr/bin/env python3
"""Run the synthetic HausaQA evaluation corpus."""

from __future__ import annotations

import argparse
from pathlib import Path

from hausaqa.evaluation import evaluate_fixture, format_evaluation
from hausaqa.terminology import load_glossary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path, nargs="?", default=Path("fixtures/evaluation.json"))
    parser.add_argument("--glossary", type=Path, default=Path("fixtures/glossary.tsv"))
    args = parser.parse_args()
    result = evaluate_fixture(args.fixture, load_glossary(args.glossary))
    print(format_evaluation(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
