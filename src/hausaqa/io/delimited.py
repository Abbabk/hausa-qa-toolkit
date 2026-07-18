"""CSV and TSV bilingual-pair input."""

from __future__ import annotations

import csv
from pathlib import Path

from ..models import Segment


def read_delimited(path: str | Path) -> list[Segment]:
    file_path = Path(path)
    delimiter = "\t" if file_path.suffix.lower() == ".tsv" else ","
    with file_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle, delimiter=delimiter))
    if not rows:
        return []

    header = [cell.strip().casefold() for cell in rows[0]]
    has_header = "source" in header and "target" in header
    if has_header:
        source_index = header.index("source")
        target_index = header.index("target")
        reference_index = header.index("reference") if "reference" in header else None
        data_rows = rows[1:]
        start = 2
    else:
        source_index, target_index, reference_index = 0, 1, None
        data_rows = rows
        start = 1

    segments: list[Segment] = []
    for line_number, row in enumerate(data_rows, start):
        if not row or all(not cell.strip() for cell in row):
            continue
        if len(row) <= max(source_index, target_index):
            raise ValueError(f"{file_path.name}:{line_number} needs source and target columns")
        reference = (
            row[reference_index].strip()
            if reference_index is not None
            and len(row) > reference_index
            and row[reference_index].strip()
            else f"{file_path.name}:{line_number}"
        )
        segments.append(Segment(row[source_index], row[target_index], reference))
    return segments
