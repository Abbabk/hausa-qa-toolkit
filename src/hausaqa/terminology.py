"""Glossary model and terminology consistency checks."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .models import Issue, Segment, Severity


@dataclass(frozen=True, slots=True)
class GlossaryEntry:
    source_term: str
    approved_term: str
    forbidden_variants: tuple[str, ...] = ()


def _contains(text: str, term: str) -> bool:
    normalized_text = unicodedata.normalize("NFC", text)
    normalized_term = unicodedata.normalize("NFC", term)
    pattern = rf"(?<!\w){re.escape(normalized_term)}(?!\w)"
    return re.search(pattern, normalized_text, flags=re.IGNORECASE) is not None


def _required_text(value: object, field: str, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} {field} must be a non-empty string")
    return value.strip()


def load_glossary(path: str | Path) -> list[GlossaryEntry]:
    """Load JSON entries or tab-separated source, approved, forbidden columns."""

    glossary_path = Path(path)
    suffix = glossary_path.suffix.lower()
    if suffix not in {".json", ".tsv"}:
        raise ValueError(f"Unsupported glossary extension: {suffix or '<none>'}")

    if suffix == ".json":
        raw = json.loads(glossary_path.read_text(encoding="utf-8-sig"))
        if not isinstance(raw, list):
            raise ValueError("JSON glossary must be a list")
        entries: list[GlossaryEntry] = []
        for index, item in enumerate(raw, 1):
            location = f"JSON glossary entry {index}"
            if not isinstance(item, dict):
                raise ValueError(f"{location} must be an object")
            source_term = _required_text(item.get("source_term"), "source_term", location)
            approved_term = _required_text(item.get("approved_term"), "approved_term", location)
            forbidden_raw = item.get("forbidden_variants", [])
            if not isinstance(forbidden_raw, list):
                raise ValueError(f"{location} forbidden_variants must be a list of strings")
            forbidden = tuple(
                _required_text(value, "forbidden_variants item", location)
                for value in forbidden_raw
            )
            entries.append(GlossaryEntry(source_term, approved_term, forbidden))
        return entries

    entries: list[GlossaryEntry] = []
    for number, line in enumerate(glossary_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) < 2:
            raise ValueError(f"Glossary line {number} needs at least two TSV columns")
        if len(columns) > 3:
            raise ValueError(f"Glossary line {number} has more than three TSV columns")
        source_term = _required_text(columns[0], "source term", f"Glossary line {number}")
        approved_term = _required_text(columns[1], "approved term", f"Glossary line {number}")
        forbidden = (
            tuple(value.strip() for value in columns[2].split("|") if value.strip())
            if len(columns) > 2
            else ()
        )
        entries.append(GlossaryEntry(source_term, approved_term, forbidden))
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
