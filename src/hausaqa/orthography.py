"""Conservative, deterministic Hausa orthography checks."""

from __future__ import annotations

import re
import unicodedata

from .models import Issue, Segment, Severity

_HOOK_MAP = str.maketrans({"ɓ": "b", "ɗ": "d", "ƙ": "k", "ƴ": "y", "Ɓ": "B", "Ɗ": "D", "Ƙ": "K"})
_ASCII_APOSTROPHE_Y = re.compile(r"(?<!\w)['’][yY]")
_ASCII_HOOK_FALLBACK = re.compile(r"(?<!\w)[bBdDkKyY]'(?=[A-Za-z])")
_DOUBLE_SPACE = re.compile(r" {2,}")
_SENTENCE_LOWER = re.compile(r"[.!?][\"'’ʼ)]*\s+([a-zɓɗƙƴ])")
_LATIN = re.compile(r"[A-Za-zɓɗƙƴƁƊƘ]", re.UNICODE)
_ARABIC = re.compile(r"[\u0600-\u06ff]")
_REPLACEMENT = "\ufffd"


def _issue(segment: Segment, code: str, message: str, severity: Severity) -> Issue:
    return Issue("orthography", code, message, severity, segment.reference)


def check_orthography(segment: Segment) -> list[Issue]:
    """Flag high-confidence text damage without trying to judge fluent Hausa."""

    original_target = segment.target
    target = unicodedata.normalize("NFC", original_target)
    source = unicodedata.normalize("NFC", segment.source)
    issues: list[Issue] = []

    if _DOUBLE_SPACE.search(target):
        issues.append(
            _issue(segment, "double_space", "Target contains repeated spaces", Severity.MINOR)
        )

    if _ASCII_APOSTROPHE_Y.search(target):
        issues.append(
            _issue(
                segment,
                "apostrophe_y",
                "Use modifier apostrophe ʼ before y instead of a straight or curly quote",
                Severity.MAJOR,
            )
        )

    if _ASCII_HOOK_FALLBACK.search(target):
        issues.append(
            _issue(
                segment,
                "ascii_hook_fallback",
                "Target contains an ASCII apostrophe fallback for a hooked letter",
                Severity.MAJOR,
            )
        )

    if _REPLACEMENT in target:
        issues.append(
            _issue(
                segment,
                "replacement_character",
                "Target contains the Unicode replacement character",
                Severity.CRITICAL,
            )
        )

    if _LATIN.search(target) and _ARABIC.search(target):
        issues.append(
            _issue(
                segment,
                "mixed_scripts",
                "Target mixes Latin and Arabic-script characters",
                Severity.MAJOR,
            )
        )

    if _SENTENCE_LOWER.search(target):
        issues.append(
            _issue(
                segment,
                "sentence_capitalization",
                "A sentence begins with a lowercase letter after terminal punctuation",
                Severity.MINOR,
            )
        )

    source_plain = source.translate(_HOOK_MAP)
    target_plain = target.translate(_HOOK_MAP)
    if source != target and source_plain.casefold() == target_plain.casefold():
        source_hooks = {char.casefold() for char in source if char in "ɓɗƙƴƁƊƘ"}
        target_hooks = {char.casefold() for char in target if char in "ɓɗƙƴƁƊƘ"}
        if source_hooks - target_hooks:
            issues.append(
                _issue(
                    segment,
                    "hooked_letter_substitution",
                    "One or more hooked Hausa letters were replaced with bare ASCII letters",
                    Severity.MAJOR,
                )
            )

    if any(unicodedata.combining(char) for char in original_target):
        issues.append(
            _issue(
                segment,
                "combining_mark",
                "Target contains a decomposed combining mark; normalize or verify the character",
                Severity.MINOR,
            )
        )

    return issues
