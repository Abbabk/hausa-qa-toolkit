"""Glossary model and terminology consistency checks."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .models import Issue, Segment, Severity


@dataclass(frozen=True, slots=True)
class GlossaryEntry:
    source_term: str
    approved_term: str
    forbidden_variants: tuple[str, ...] = ()


def _contains(text: str, term: str) -> bool:
    pattern = rf"(?<!\w){re.escape(term)}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def load_glossary(path: str | Path) -> list[GlossaryEntry]:
    """Load JSON entries or tab-separated source, approved, forbidden columns."""

    glossary_path = Path(path)
    if glossary_path.suffix.lower() == ".json":
        raw = json.loads(glossary_path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("JSON glossary must be a list")
        return [
            GlossaryEntry(
                str(item["source_term"]),
                str(item["approved_term"]),
                tuple(str(value) for value in item.get("forbidden_variants", [])),
            )
            for item in raw
        ]

    entries: list[GlossaryEntry] = []
    for number, line in enumerate(glossary_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) < 2:
            raise ValueError(f"Glossary line {number} needs at least two TSV columns")
        forbidden = tuple(value.strip() for value in columns[2].split("|") if value.strip()) if len(columns) > 2 else ()
        entries.append(GlossaryEntry(columns[0].strip(), columns[1].strip(), forbidden))
    return entries


def check_terminology(segment: Segment, glossary: list[GlossaryEntry]) -> list[Issue]:
    """Check approved and forbidden target terms when a source term is present."""

    issues: list[Issue] = []
    for entry in glossary:
        if not _contains(segment.source, entry.source_term):
            continue
        for forbidden in entry.forbidden_variants:
            if _contains(segment.target, forbidden):
                issues.append(
                    Issue(
                        "terminology",
                        "forbidden_variant",
                        f"Forbidden variant {forbidden!r} used for {entry.source_term!r}",
                        Severity.MAJOR,
                        segment.reference,
                    )
                )
        if not _contains(segment.target, entry.approved_term):
            issues.append(
                Issue(
                    "terminology",
                    "approved_term_missing",
                    f"Expected approved term {entry.approved_term!r} for {entry.source_term!r}",
                    Severity.MAJOR,
                    segment.reference,
                )
            )
    return issues
