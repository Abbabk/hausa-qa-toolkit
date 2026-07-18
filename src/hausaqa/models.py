"""Segment and MQM-style QA report models."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Iterable


class Severity(IntEnum):
    """Ordered severities used for CLI failure thresholds."""

    MINOR = 1
    MAJOR = 2
    CRITICAL = 3

    @classmethod
    def parse(cls, value: str) -> "Severity":
        try:
            return cls[value.upper()]
        except KeyError as exc:
            raise ValueError(f"Unknown severity: {value}") from exc


@dataclass(frozen=True, slots=True)
class Segment:
    source: str
    target: str
    reference: str


@dataclass(frozen=True, slots=True)
class Issue:
    category: str
    code: str
    message: str
    severity: Severity
    reference: str

    def to_dict(self) -> dict[str, str]:
        data = asdict(self)
        data["severity"] = self.severity.name.lower()
        return data


@dataclass(slots=True)
class Report:
    issues: list[Issue] = field(default_factory=list)
    segments_checked: int = 0

    def extend(self, issues: Iterable[Issue]) -> None:
        self.issues.extend(issues)

    def count(self, severity: Severity | None = None) -> int:
        if severity is None:
            return len(self.issues)
        return sum(issue.severity == severity for issue in self.issues)

    def fails_at(self, threshold: Severity) -> bool:
        return any(issue.severity >= threshold for issue in self.issues)

    def to_dict(self) -> dict[str, object]:
        return {
            "version": "0.1.0",
            "segments_checked": self.segments_checked,
            "issue_count": len(self.issues),
            "summary": {
                severity.name.lower(): self.count(severity)
                for severity in (Severity.CRITICAL, Severity.MAJOR, Severity.MINOR)
            },
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_text(self) -> str:
        lines = [
            f"HausaQA 0.1.0: {self.segments_checked} segment(s), {len(self.issues)} issue(s)",
            (
                "Summary: "
                f"critical={self.count(Severity.CRITICAL)} "
                f"major={self.count(Severity.MAJOR)} "
                f"minor={self.count(Severity.MINOR)}"
            ),
        ]
        for issue in self.issues:
            lines.append(
                f"[{issue.severity.name.lower()}] {issue.reference} "
                f"{issue.category}/{issue.code}: {issue.message}"
            )
        return "\n".join(lines)
