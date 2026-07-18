from __future__ import annotations

import pytest

from hausaqa.models import Segment
from hausaqa.orthography import check_orthography


def codes(source: str, target: str) -> list[str]:
    return [issue.code for issue in check_orthography(Segment(source, target, "seg"))]


def test_double_spaces_are_minor():
    issues = check_orthography(Segment("A", "Kalma  biyu", "s"))
    assert [(issue.code, issue.severity.name) for issue in issues] == [("double_space", "MINOR")]


@pytest.mark.parametrize("mark", ["'", "’"])
def test_nonpreferred_apostrophe_before_y_is_flagged(mark):
    assert "apostrophe_y" in codes("A", f"{mark}yarinya")


def test_modifier_apostrophe_before_y_is_accepted():
    assert "apostrophe_y" not in codes("A", "ʼyarinya")


def test_ascii_hook_fallback_is_flagged():
    assert "ascii_hook_fallback" in codes("A", "b'arka")


def test_unicode_replacement_character_is_critical():
    issues = check_orthography(Segment("A", "Kalma �", "s"))
    replacement = next(issue for issue in issues if issue.code == "replacement_character")
    assert replacement.severity.name == "CRITICAL"


def test_mixed_latin_and_arabic_scripts_are_flagged():
    assert "mixed_scripts" in codes("A", "Hausa س")


def test_pure_latin_text_is_not_mixed_script():
    assert "mixed_scripts" not in codes("A", "Harshen Hausa")


def test_lowercase_after_sentence_end_is_flagged():
    assert "sentence_capitalization" in codes("A", "Na zo. sai na tafi.")


def test_uppercase_after_sentence_end_is_accepted():
    assert "sentence_capitalization" not in codes("A", "Na zo. Sai na tafi.")


@pytest.mark.parametrize(
    ("source", "target"),
    [("Ƙofa", "Kofa"), ("ɓera", "bera"), ("ɗaki", "daki"), ("ƴa", "ya")],
)
def test_hooked_letter_substitution_is_detected(source, target):
    assert "hooked_letter_substitution" in codes(source, target)


def test_unrelated_translation_does_not_guess_hooked_letter_error():
    assert "hooked_letter_substitution" not in codes("Door", "Kofa")


def test_decomposed_combining_mark_is_flagged():
    assert "combining_mark" in codes("A", "e\u0301")
