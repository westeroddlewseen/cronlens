"""Tests for cronlens.cli_exporter."""

import argparse
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from cronlens.cli_exporter import cmd_export, build_export_parser


class FakeArgs:
    def __init__(self, expressions, fmt="json", count=3, output=None):
        self.expressions = expressions
        self.format = fmt
        self.count = count
        self.output = output


def test_cmd_export_json_prints_output(capsys):
    args = FakeArgs(["* * * * *"], fmt="json")
    cmd_export(args)
    captured = capsys.readouterr()
    assert "expression" in captured.out


def test_cmd_export_csv_prints_header(capsys):
    args = FakeArgs(["0 0 * * *"], fmt="csv")
    cmd_export(args)
    captured = capsys.readouterr()
    assert "expression,human" in captured.out


def test_cmd_export_markdown_prints_table(capsys):
    args = FakeArgs(["0 9 * * 1"], fmt="markdown")
    cmd_export(args)
    captured = capsys.readouterr()
    assert "| Expression |" in captured.out


def test_cmd_export_resolves_alias(capsys):
    args = FakeArgs(["@daily"], fmt="json")
    cmd_export(args)
    captured = capsys.readouterr()
    import json
    data = json.loads(captured.out)
    assert len(data) == 1


def test_cmd_export_skips_invalid_expression(capsys):
    args = FakeArgs(["not_a_cron", "* * * * *"], fmt="json")
    cmd_export(args)
    captured = capsys.readouterr()
    import json
    data = json.loads(captured.out)
    assert len(data) == 1


def test_cmd_export_all_invalid_exits(capsys):
    args = FakeArgs(["bad_expr"], fmt="json")
    with pytest.raises(SystemExit):
        cmd_export(args)


def test_cmd_export_writes_to_file(tmp_path, capsys):
    out_file = tmp_path / "out.json"
    args = FakeArgs(["* * * * *"], fmt="json", output=str(out_file))
    cmd_export(args)
    assert out_file.exists()
    content = out_file.read_text()
    assert "expression" in content


def test_build_export_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    build_export_parser(subs)
    args = parser.parse_args(["export", "* * * * *", "-f", "csv"])
    assert args.format == "csv"
    assert args.expressions == ["* * * * *"]
