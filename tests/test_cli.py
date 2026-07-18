from __future__ import annotations

import json

from hausaqa.cli import EXIT_OK, EXIT_QA_FAILURE, EXIT_USAGE_ERROR, main


def test_cli_clean_file_exits_zero(tmp_path, capsys):
    path = tmp_path / "clean.tsv"
    path.write_text("source\ttarget\nHello {name}\tSannu {name}\n", encoding="utf-8")
    assert main(["check", str(path)]) == EXIT_OK
    assert "0 issue(s)" in capsys.readouterr().out


def test_cli_critical_issue_exits_one(tmp_path, capsys):
    path = tmp_path / "bad.tsv"
    path.write_text("source\ttarget\nHello {name}\tSannu\n", encoding="utf-8")
    assert main(["check", str(path)]) == EXIT_QA_FAILURE
    assert "placeholder/missing" in capsys.readouterr().out


def test_cli_major_threshold_can_fail_on_orthography(tmp_path):
    path = tmp_path / "bad.tsv"
    path.write_text("source\ttarget\nA\t'yara\n", encoding="utf-8")
    assert main(["check", str(path), "--fail-on", "major"]) == EXIT_QA_FAILURE


def test_cli_default_threshold_does_not_fail_on_minor(tmp_path):
    path = tmp_path / "minor.tsv"
    path.write_text("source\ttarget\nA\tKalma  biyu\n", encoding="utf-8")
    assert main(["check", str(path)]) == EXIT_OK


def test_cli_json_output_is_machine_readable(tmp_path, capsys):
    path = tmp_path / "clean.tsv"
    path.write_text("source\ttarget\nHello\tSannu\n", encoding="utf-8")
    assert main(["check", str(path), "--format", "json"]) == EXIT_OK
    assert json.loads(capsys.readouterr().out)["segments_checked"] == 1


def test_cli_missing_file_exits_two(tmp_path, capsys):
    assert main(["check", str(tmp_path / "missing.tsv")]) == EXIT_USAGE_ERROR
    assert "does not exist" in capsys.readouterr().err


def test_cli_unsupported_extension_exits_two(tmp_path, capsys):
    path = tmp_path / "pairs.txt"
    path.write_text("a|b")
    assert main(["check", str(path)]) == EXIT_USAGE_ERROR
    assert "Unsupported input extension" in capsys.readouterr().err


def test_cli_glossary_adds_terminology_issue(tmp_path, capsys):
    pairs = tmp_path / "pairs.tsv"
    pairs.write_text("source\ttarget\nOpen account\tBuɗe lissafi\n", encoding="utf-8")
    glossary = tmp_path / "terms.tsv"
    glossary.write_text("account\tasusu\tlissafi\n", encoding="utf-8")
    assert main(["check", str(pairs), "--glossary", str(glossary), "--fail-on", "major"]) == 1
    assert "terminology/forbidden_variant" in capsys.readouterr().out
