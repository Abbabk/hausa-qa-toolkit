"""Command-line interface for HausaQA."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine import check_segments
from .io import read_delimited, read_json_pairs, read_xliff
from .models import Severity
from .terminology import load_glossary

EXIT_OK = 0
EXIT_QA_FAILURE = 1
EXIT_USAGE_ERROR = 2


def _load_segments(path: Path):
    suffix = path.suffix.lower()
    if suffix in {".csv", ".tsv"}:
        return read_delimited(path)
    if suffix == ".json":
        return read_json_pairs(path)
    if suffix in {".xlf", ".xliff"}:
        return read_xliff(path)
    raise ValueError(f"Unsupported input extension: {suffix or '<none>'}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hausaqa", description="Hausa localization QA toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="check a bilingual localization file")
    check.add_argument("file", type=Path, help="CSV, TSV, JSON, XLF, or XLIFF input")
    check.add_argument("--glossary", type=Path, help="TSV or JSON glossary")
    check.add_argument("--format", choices=("json", "text"), default="text", dest="output_format")
    check.add_argument(
        "--fail-on",
        choices=("critical", "major"),
        default="critical",
        help="return exit code 1 when this severity or higher occurs",
    )
    return parser


def run_check(args: argparse.Namespace) -> int:
    if not args.file.is_file():
        raise ValueError(f"Input file does not exist: {args.file}")
    segments = _load_segments(args.file)
    glossary = load_glossary(args.glossary) if args.glossary else None
    report = check_segments(segments, glossary)
    output = report.to_json() if args.output_format == "json" else report.to_text()
    print(output)
    return EXIT_QA_FAILURE if report.fails_at(Severity.parse(args.fail_on)) else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            return run_check(args)
    except (OSError, ValueError, KeyError) as exc:
        print(f"hausaqa: error: {exc}", file=sys.stderr)
        return EXIT_USAGE_ERROR
    return EXIT_USAGE_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
