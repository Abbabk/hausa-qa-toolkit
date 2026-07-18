"""Reproducible segment-level evaluation for synthetic fixtures."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .engine import check_segments
from .models import Segment
from .terminology import GlossaryEntry

CATEGORIES = ("placeholder", "orthography", "terminology")


def evaluate_fixture(
    fixture_path: str | Path, glossary: list[GlossaryEntry] | None = None
) -> dict[str, Any]:
    records = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    counts: dict[str, dict[str, int]] = {category: defaultdict(int) for category in CATEGORIES}

    for record in records:
        segment = Segment(record["source"], record["target"], record["reference"])
        predicted = {issue.category for issue in check_segments([segment], glossary).issues}
        expected = set(record["expected_categories"])
        for category in CATEGORIES:
            if category in predicted and category in expected:
                counts[category]["tp"] += 1
            elif category in predicted:
                counts[category]["fp"] += 1
            elif category in expected:
                counts[category]["fn"] += 1
            else:
                counts[category]["tn"] += 1

    result: dict[str, Any] = {"segments": len(records), "categories": {}}
    for category in CATEGORIES:
        values = counts[category]
        tp, fp, fn = values["tp"], values["fp"], values["fn"]
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        result["categories"][category] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": values["tn"],
            "precision": round(precision, 4),
            "recall": round(recall, 4),
        }
    return result


def format_evaluation(result: dict[str, Any]) -> str:
    lines = [f"Synthetic evaluation: {result['segments']} segments"]
    for category in CATEGORIES:
        values = result["categories"][category]
        lines.append(
            f"{category}: precision={values['precision']:.4f} recall={values['recall']:.4f} "
            f"tp={values['tp']} fp={values['fp']} fn={values['fn']}"
        )
    return "\n".join(lines)
