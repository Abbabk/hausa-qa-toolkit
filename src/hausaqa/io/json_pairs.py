"""JSON bilingual-pair input."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import Segment


def read_json_pairs(path: str | Path) -> list[Segment]:
    file_path = Path(path)
    payload = json.loads(file_path.read_text(encoding="utf-8-sig"))
    segments: list[Segment] = []

    if isinstance(payload, list):
        items = [(str(index), item) for index, item in enumerate(payload, 1)]
    elif isinstance(payload, dict):
        items = list(payload.items())
    else:
        raise ValueError("JSON pairs must be an object or list")

    for key, value in items:
        if not isinstance(value, dict) or "source" not in value or "target" not in value:
            raise ValueError(f"JSON entry {key!r} must contain source and target strings")
        source = value["source"]
        target = value["target"]
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError(f"JSON entry {key!r} source and target must be strings")
        if "reference" in value:
            reference_value = value["reference"]
            if not isinstance(reference_value, str) or not reference_value.strip():
                raise ValueError(f"JSON entry {key!r} reference must be a non-empty string")
            reference = reference_value
        else:
            reference = str(key)
        segments.append(Segment(source, target, reference))
    return segments
