from hausaqa.engine import check_segments
from hausaqa.models import Segment
from hausaqa.terminology import GlossaryEntry


def test_engine_runs_multiple_check_categories():
    segment = Segment("Open account {name}", "Buɗe lissafi  ", "s1")
    report = check_segments([segment], [GlossaryEntry("account", "asusu", ("lissafi",))])
    assert {issue.category for issue in report.issues} == {
        "placeholder",
        "orthography",
        "terminology",
    }


def test_engine_counts_generator_segments_once():
    segments = (Segment(str(i), str(i), str(i)) for i in range(3))
    assert check_segments(segments).segments_checked == 3


def test_engine_without_glossary_skips_terminology():
    report = check_segments([Segment("account", "lissafi", "s")])
    assert all(issue.category != "terminology" for issue in report.issues)
