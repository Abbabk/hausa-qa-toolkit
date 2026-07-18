from __future__ import annotations

import json

import pytest

from hausaqa.models import Segment
from hausaqa.terminology import GlossaryEntry, check_terminology, load_glossary

ENTRY = GlossaryEntry("account", "asusu", ("lissafi", "akwati"))


def codes(source: str, target: str):
    return [issue.code for issue in check_terminology(Segment(source, target, "line-4"), [ENTRY])]


def test_approved_term_passes():
    assert codes("Open the account", "Buɗe asusu") == []


def test_missing_approved_term_is_flagged():
    assert codes("Open the account", "Buɗe bayanai") == ["approved_term_missing"]


def test_forbidden_variant_and_missing_approved_are_both_flagged():
    assert codes("Open the account", "Buɗe lissafi") == [
        "forbidden_variant",
        "approved_term_missing",
    ]


def test_source_term_absence_skips_entry():
    assert codes("Open the page", "Buɗe lissafi") == []


def test_term_matching_is_case_insensitive():
    assert codes("ACCOUNT", "ASUSU") == []


def test_term_matching_respects_word_boundaries():
    assert codes("accounting", "bayanai") == []


def test_issue_keeps_segment_reference():
    issue = check_terminology(Segment("account", "bayanai", "row-22"), [ENTRY])[0]
    assert issue.reference == "row-22"


def test_load_tsv_glossary_with_comments(tmp_path):
    path = tmp_path / "terms.tsv"
    path.write_text("# note\naccount\tasusu\tlissafi|akwati\n", encoding="utf-8")
    assert load_glossary(path) == [ENTRY]


def test_load_json_glossary(tmp_path):
    path = tmp_path / "terms.json"
    path.write_text(
        json.dumps(
            [
                {
                    "source_term": "page",
                    "approved_term": "shafi",
                    "forbidden_variants": ["takarda"],
                }
            ]
        ),
        encoding="utf-8",
    )
    assert load_glossary(path) == [GlossaryEntry("page", "shafi", ("takarda",))]


def test_invalid_tsv_glossary_reports_line(tmp_path):
    path = tmp_path / "bad.tsv"
    path.write_text("only-one-column\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 1"):
        load_glossary(path)


def test_json_glossary_requires_list(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a list"):
        load_glossary(path)
