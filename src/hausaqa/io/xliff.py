"""XLIFF 1.2 and 2.0 bilingual-pair input."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from ..models import Segment


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _inline_text(element: ET.Element) -> str:
    parts = [element.text or ""]
    for child in element:
        name = _local(child.tag)
        attributes = "".join(
            f' {key.rsplit("}", 1)[-1]}="{value}"' for key, value in sorted(child.attrib.items())
        )
        if len(child) or child.text:
            parts.append(f"<{name}{attributes}>")
            parts.append(_inline_text(child))
            parts.append(f"</{name}>")
        else:
            parts.append(f"<{name}{attributes}/>")
        parts.append(child.tail or "")
    return "".join(parts)


def _children(element: ET.Element, name: str) -> list[ET.Element]:
    return [child for child in element.iter() if _local(child.tag) == name]


def _first_child(element: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in element if _local(child.tag) == name), None)


def read_xliff(path: str | Path) -> list[Segment]:
    file_path = Path(path)
    root = ET.parse(file_path).getroot()
    version = root.attrib.get("version", "")
    segments: list[Segment] = []

    if version.startswith("1"):
        for index, unit in enumerate(_children(root, "trans-unit"), 1):
            source = _first_child(unit, "source")
            target = _first_child(unit, "target")
            if source is None or target is None:
                continue
            reference = unit.attrib.get("id", f"unit-{index}")
            segments.append(Segment(_inline_text(source), _inline_text(target), reference))
        return segments

    if version.startswith("2"):
        for unit_index, unit in enumerate(_children(root, "unit"), 1):
            unit_id = unit.attrib.get("id", f"unit-{unit_index}")
            for segment_index, item in enumerate(_children(unit, "segment"), 1):
                source = _first_child(item, "source")
                target = _first_child(item, "target")
                if source is None or target is None:
                    continue
                segment_id = item.attrib.get("id", str(segment_index))
                segments.append(
                    Segment(
                        _inline_text(source),
                        _inline_text(target),
                        f"{unit_id}:{segment_id}",
                    )
                )
        return segments

    raise ValueError(f"Unsupported or missing XLIFF version: {version!r}")
