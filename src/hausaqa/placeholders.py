"""Placeholder and inline-tag parity checks."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from .models import Issue, Segment, Severity

_TOKEN_RE = re.compile(
    r"(?P<mustache>\{\{\s*[A-Za-z_][\w.-]*\s*\}\})"
    r"|(?P<printf>%(?:\d+\$)?[diouxXeEfFgGcrsa])"
    r"|(?P<html></?[A-Za-z][\w:-]*(?:\s+[A-Za-z_:][\w:.-]*"
    r"(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s>]+))?)*\s*/?>)"
    r"|(?P<bracket>\[/?(?:[A-Za-z][\w.-]*|\d+)\])"
    r"|(?P<icu>\{\s*[A-Za-z_][\w.-]*(?:\s*,\s*(?:number|date|time))?\s*\})"
)
_PRINTF_FRAGMENT_RE = re.compile(r"%(?!%|(?:\d+\$)?[diouxXeEfFgGcrsa])\S*")
_IDENTIFIER_RE = re.compile(r"[A-Za-z_][\w.-]*")
_TAG_NAME_RE = re.compile(r"</?([A-Za-z][\w:-]*)")


@dataclass(frozen=True, slots=True)
class Token:
    raw: str
    family: str
    start: int


def extract_tokens(text: str) -> list[Token]:
    """Return supported placeholders and tags in source order."""

    tokens: list[Token] = []
    for match in _TOKEN_RE.finditer(text):
        family = match.lastgroup
        if family is not None:
            tokens.append(Token(match.group(), family, match.start()))
    return tokens


def _html_structure_errors(text: str) -> list[str]:
    stack: list[str] = []
    errors: list[str] = []
    for token in extract_tokens(text):
        if token.family != "html":
            continue
        name_match = _TAG_NAME_RE.match(token.raw)
        if name_match is None:
            continue
        name = name_match.group(1).lower()
        if token.raw.rstrip().endswith("/>"):
            continue
        if token.raw.startswith("</"):
            if not stack or stack[-1] != name:
                errors.append(f"unexpected closing tag </{name}>")
            else:
                stack.pop()
        else:
            stack.append(name)
    errors.extend(f"unclosed tag <{name}>" for name in reversed(stack))
    return errors


def _delimiter_errors(text: str) -> list[str]:
    errors: list[str] = []
    scrubbed = _TOKEN_RE.sub("", text)
    if "{{" in scrubbed or "}}" in scrubbed:
        errors.append("unbalanced double-brace placeholder")
    if scrubbed.count("{") != scrubbed.count("}"):
        errors.append("unbalanced brace placeholder")
    for fragment in _PRINTF_FRAGMENT_RE.findall(scrubbed.replace("%%", "")):
        errors.append(f"malformed printf fragment {fragment!r}")
    errors.extend(_html_structure_errors(text))
    return errors


def _placeholder_identifier(raw: str) -> str | None:
    if raw.startswith("%") or raw.startswith("<") or raw.startswith("["):
        return None
    match = _IDENTIFIER_RE.search(raw)
    return match.group().casefold() if match else None


def check_placeholders(segment: Segment) -> list[Issue]:
    """Compare placeholder/tag inventory, order, syntax, and likely corruption."""

    source_tokens = extract_tokens(segment.source)
    target_tokens = extract_tokens(segment.target)
    source_values = [token.raw for token in source_tokens]
    target_values = [token.raw for token in target_tokens]
    source_count = Counter(source_values)
    target_count = Counter(target_values)
    issues: list[Issue] = []

    for token, count in (source_count - target_count).items():
        issues.append(
            Issue(
                "placeholder",
                "missing",
                f"Missing {count} occurrence(s) of {token!r}",
                Severity.CRITICAL,
                segment.reference,
            )
        )
    for token, count in (target_count - source_count).items():
        issues.append(
            Issue(
                "placeholder",
                "extra",
                f"Extra {count} occurrence(s) of {token!r}",
                Severity.CRITICAL,
                segment.reference,
            )
        )

    if source_count == target_count and source_values != target_values:
        issues.append(
            Issue(
                "placeholder",
                "reordered",
                "Placeholder or tag order differs from the source",
                Severity.MAJOR,
                segment.reference,
            )
        )

    for error in _delimiter_errors(segment.target):
        issues.append(
            Issue(
                "placeholder",
                "malformed",
                error,
                Severity.CRITICAL,
                segment.reference,
            )
        )

    target_lower = segment.target.casefold()
    for token in source_tokens:
        identifier = _placeholder_identifier(token.raw)
        if token.raw not in target_values and identifier and identifier in target_lower:
            issues.append(
                Issue(
                    "placeholder",
                    "corrupted",
                    f"Identifier {identifier!r} remains but its placeholder delimiters changed",
                    Severity.CRITICAL,
                    segment.reference,
                )
            )
    return _deduplicate(issues)


def _deduplicate(issues: list[Issue]) -> list[Issue]:
    return list(dict.fromkeys(issues))
