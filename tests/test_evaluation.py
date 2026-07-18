from __future__ import annotations

import json

from hausaqa.evaluation import evaluate_fixture, format_evaluation
from hausaqa.terminology import GlossaryEntry


def test_evaluation_scores_true_positive_and_true_negative(tmp_path):
    path = tmp_path / "eval.json"
    path.write_text(
        json.dumps(
            [
                {
                    "reference": "1",
                    "source": "Hello {name}",
                    "target": "Sannu",
                    "expected_categories": ["placeholder"],
                },
                {
                    "reference": "2",
                    "source": "Hello",
                    "target": "Sannu",
                    "expected_categories": [],
                },
            ]
        ),
        encoding="utf-8",
    )
    result = evaluate_fixture(path)
    assert result["categories"]["placeholder"]["precision"] == 1.0
    assert result["categories"]["placeholder"]["recall"] == 1.0


def test_evaluation_format_reports_each_category(tmp_path):
    path = tmp_path / "eval.json"
    path.write_text(
        json.dumps(
            [
                {
                    "reference": "1",
                    "source": "account",
                    "target": "asusu",
                    "expected_categories": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    result = evaluate_fixture(path, [GlossaryEntry("account", "asusu")])
    text = format_evaluation(result)
    assert "placeholder: precision=" in text
    assert "orthography: precision=" in text
    assert "terminology: precision=" in text
