from __future__ import annotations

import json

import pytest

from hausaqa.io import read_delimited, read_json_pairs, read_xliff


def test_read_tsv_with_header_and_reference(tmp_path):
    path = tmp_path / "pairs.tsv"
    path.write_text("reference\tsource\ttarget\nr1\tHello\tSannu\n", encoding="utf-8")
    assert read_delimited(path)[0].reference == "r1"


def test_read_csv_without_header_uses_line_reference(tmp_path):
    path = tmp_path / "pairs.csv"
    path.write_text('"Hello, friend","Sannu, aboki"\n', encoding="utf-8")
    segment = read_delimited(path)[0]
    assert segment.source == "Hello, friend"
    assert segment.reference == "pairs.csv:1"


def test_read_delimited_skips_blank_rows(tmp_path):
    path = tmp_path / "pairs.tsv"
    path.write_text("source\ttarget\n\t\nHello\tSannu\n", encoding="utf-8")
    assert len(read_delimited(path)) == 1


def test_read_delimited_rejects_short_row(tmp_path):
    path = tmp_path / "pairs.tsv"
    path.write_text("Hello\n", encoding="utf-8")
    with pytest.raises(ValueError, match="source and target"):
        read_delimited(path)


def test_read_json_object_pairs(tmp_path):
    path = tmp_path / "pairs.json"
    path.write_text(json.dumps({"welcome": {"source": "Hello", "target": "Sannu"}}))
    assert read_json_pairs(path)[0].reference == "welcome"


def test_read_json_list_pairs_with_explicit_reference(tmp_path):
    path = tmp_path / "pairs.json"
    path.write_text(json.dumps([{"source": "Hello", "target": "Sannu", "reference": "x"}]))
    assert read_json_pairs(path)[0].reference == "x"


def test_read_json_rejects_string_values(tmp_path):
    path = tmp_path / "pairs.json"
    path.write_text(json.dumps({"welcome": "Sannu"}))
    with pytest.raises(ValueError, match="must contain source and target"):
        read_json_pairs(path)


def test_read_xliff_12(tmp_path):
    path = tmp_path / "sample.xlf"
    path.write_text(
        '<?xml version="1.0"?><xliff version="1.2"><file><body>'
        '<trans-unit id="u1"><source>Hello</source><target>Sannu</target></trans-unit>'
        '</body></file></xliff>',
        encoding="utf-8",
    )
    segment = read_xliff(path)[0]
    assert (segment.source, segment.target, segment.reference) == ("Hello", "Sannu", "u1")


def test_read_xliff_20_namespaced(tmp_path):
    path = tmp_path / "sample.xliff"
    path.write_text(
        '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0">'
        '<file id="f"><unit id="u"><segment id="s"><source>Hello</source>'
        '<target>Sannu</target></segment></unit></file></xliff>',
        encoding="utf-8",
    )
    assert read_xliff(path)[0].reference == "u:s"


def test_read_xliff_preserves_inline_element_shape(tmp_path):
    path = tmp_path / "inline.xlf"
    path.write_text(
        '<xliff version="1.2"><file><body><trans-unit id="1">'
        '<source>Hi <ph id="1"/>there</source><target>Sannu <ph id="1"/>can</target>'
        '</trans-unit></body></file></xliff>',
        encoding="utf-8",
    )
    segment = read_xliff(path)[0]
    assert segment.source == 'Hi <ph id="1"/>there'
    assert segment.target == 'Sannu <ph id="1"/>can'


def test_read_xliff_rejects_unknown_version(tmp_path):
    path = tmp_path / "sample.xlf"
    path.write_text('<xliff version="3.0"/>', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported"):
        read_xliff(path)
