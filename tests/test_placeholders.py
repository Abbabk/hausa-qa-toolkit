from __future__ import annotations

import pytest

from hausaqa.models import Segment
from hausaqa.placeholders import check_placeholders, extract_tokens


@pytest.mark.parametrize(
    ("text", "raw", "family"),
    [
        ("Hello {name}", "{name}", "icu"),
        ("Value %1$s", "%1$s", "printf"),
        ("Hello {{ person }}", "{{ person }}", "mustache"),
        ("Use <strong>this</strong>", "<strong>", "html"),
        ("Click [1]now[/1]", "[1]", "bracket"),
        ("At {time, time}", "{time, time}", "icu"),
    ],
)
def test_extract_supported_token_families(text, raw, family):
    tokens = extract_tokens(text)
    assert any(token.raw == raw and token.family == family for token in tokens)


def codes(source: str, target: str) -> list[str]:
    return [issue.code for issue in check_placeholders(Segment(source, target, "seg"))]


def test_missing_placeholder_is_critical():
    issues = check_placeholders(Segment("Hi {name}", "Sannu", "s1"))
    assert [(issue.code, issue.severity.name) for issue in issues] == [("missing", "CRITICAL")]


def test_extra_placeholder_is_detected():
    assert "extra" in codes("Hello", "Sannu {name}")


def test_reordered_placeholders_are_detected_when_inventory_matches():
    assert codes("{first} then {second}", "{second} sannan {first}") == ["reordered"]


def test_changed_printf_type_is_missing_and_extra():
    result = codes("Total %1$s", "Jimilla %1$d")
    assert set(result) == {"missing", "extra"}


def test_unbalanced_brace_is_malformed():
    assert "malformed" in codes("Hello {name}", "Sannu {name")


def test_malformed_printf_fragment_is_detected():
    assert "malformed" in codes("Count %d", "Adadi %q")


def test_mismatched_html_closing_tag_is_malformed():
    result = codes("<b>Read</b>", "<b>Karanta</i>")
    assert "malformed" in result


def test_unclosed_html_tag_is_malformed():
    assert "malformed" in codes("<b>Read</b>", "<b>Karanta")


def test_corrupted_named_placeholder_is_detected():
    result = codes("Hello {person}", "Sannu (person)")
    assert "corrupted" in result
    assert "missing" in result


def test_duplicate_placeholder_count_is_checked():
    result = codes("{x} and {x}", "{x}")
    assert result == ["missing"]


def test_valid_self_closing_tag_has_no_issue():
    assert codes("Line<br/>next", "Layi<br/>na gaba") == []


def test_valid_numbered_inline_tags_have_no_issue():
    assert codes("Save [1]three[/1]", "Ajiye [1]uku[/1]") == []


def test_literal_percent_escape_is_not_malformed():
    assert codes("Save 100%%", "Ajiye 100%%") == []
