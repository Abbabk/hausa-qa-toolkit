from __future__ import annotations

import json

import pytest

from hausaqa.models import Issue, Report, Segment, Severity


def make_issue(severity: Severity = Severity.MAJOR) -> Issue:
    return Issue("orthography", "sample", "Sample finding", severity, "row-1")


def test_severity_parse_is_case_insensitive():
    assert Severity.parse("major") is Severity.MAJOR


def test_severity_parse_rejects_unknown_value():
    with pytest.raises(ValueError, match="Unknown severity"):
        Severity.parse("urgent")


def test_issue_to_dict_uses_machine_readable_severity():
    assert make_issue().to_dict()["severity"] == "major"


def test_report_count_all_and_by_severity():
    report = Report([make_issue(Severity.MINOR), make_issue(Severity.CRITICAL)], 1)
    assert report.count() == 2
    assert report.count(Severity.CRITICAL) == 1


def test_report_failure_threshold_is_ordered():
    report = Report([make_issue(Severity.MAJOR)], 1)
    assert report.fails_at(Severity.MAJOR)
    assert not report.fails_at(Severity.CRITICAL)


def test_report_json_is_unicode_and_structured():
    report = Report([Issue("orthography", "hook", "Ƙofa", Severity.MINOR, "s1")], 1)
    payload = json.loads(report.to_json())
    assert payload["segments_checked"] == 1
    assert payload["issues"][0]["message"] == "Ƙofa"


def test_report_text_contains_summary_and_reference():
    text = Report([make_issue()], 2).to_text()
    assert "2 segment(s), 1 issue(s)" in text
    assert "row-1 orthography/sample" in text


def test_report_extend_accepts_iterable():
    report = Report()
    report.extend(make_issue(level) for level in (Severity.MINOR, Severity.MAJOR))
    assert [issue.severity for issue in report.issues] == [Severity.MINOR, Severity.MAJOR]


def test_segment_is_immutable():
    segment = Segment("a", "b", "r")
    with pytest.raises(AttributeError):
        segment.source = "changed"  # type: ignore[misc]


def test_segment_rejects_non_string_fields_immediately():
    with pytest.raises(TypeError, match="source must be a string"):
        Segment(1, "b", "r")  # type: ignore[arg-type]


def test_segment_rejects_empty_reference():
    with pytest.raises(ValueError, match="reference must not be empty"):
        Segment("a", "b", "  ")
