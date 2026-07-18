"""Core orchestration across independent QA checks."""

from __future__ import annotations

from collections.abc import Iterable

from .models import Report, Segment
from .orthography import check_orthography
from .placeholders import check_placeholders
from .terminology import GlossaryEntry, check_terminology


def check_segments(
    segments: Iterable[Segment], glossary: list[GlossaryEntry] | None = None
) -> Report:
    report = Report()
    for segment in segments:
        report.segments_checked += 1
        report.extend(check_placeholders(segment))
        report.extend(check_orthography(segment))
        if glossary:
            report.extend(check_terminology(segment, glossary))
    return report
