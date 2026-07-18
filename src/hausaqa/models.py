"""Shared report models. Implemented fully in scope section 2."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Severity(IntEnum):
    MINOR = 1
    MAJOR = 2
    CRITICAL = 3


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


@dataclass(slots=True)
class Report:
    issues: list[Issue] = field(default_factory=list)
