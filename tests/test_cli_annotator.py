"""Tests for cronlens.cli_annotator."""

import json
import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from cronlens.cli_annotator import cmd_annotate, format_annotation, build_annotate_parser
from cronlens.parser import CronExpression
from cronlens.annotator import annotate


class FakeArgs:
    def __init__(self, expression, note=None, labels=None, json_out=False):
        self.expression = expression
        self.note = note
        self.labels = labels
        self.json = json_out


def test_format_annotation_contains_expression():
    ann = annotate(CronExpression.parse("0 9 * * 1"), note="weekly")
    out = format_annotation(ann)
    assert ann.expression in out


def test_format_annotation_contains_human():
    ann = annotate(CronExpression.parse("0 0 * * *"))
    out = format_annotation(ann)
    assert ann.human in out


def test_format_annotation_shows_note():
    ann = annotate(CronExpression.parse("0 0 * * *"), note="midnight run")
    out = format_annotation(ann)
    assert "midnight run" in out


def test_format_annotation_shows_labels():
    ann = annotate(CronExpression.parse("*/5 * * * *"), labels=["prod", "fast"])
    out = format_annotation(ann)
    assert "prod" in out
    assert "fast" in out


def test_format_annotation_no_note_no_note_line():
    ann = annotate(CronExpression.parse("0 12 * * *"))
    out = format_annotation(ann)
    assert "Note" not in out


def test_cmd_annotate_prints_output(capsys):
    args = FakeArgs("0 0 * * *", note="daily")
    cmd_annotate(args)
    captured = capsys.readouterr()
    assert "Expression" in captured.out


def test_cmd_annotate_json_flag(capsys):
    args = FakeArgs("*/10 * * * *", json_out=True)
    cmd_annotate(args)
    captured = capsys.readouterr()
    # should contain valid JSON block
    assert "{" in captured.out


def test_cmd_annotate_json_parseable(capsys):
    args = FakeArgs("0 6 * * 1-5", json_out=True)
    cmd_annotate(args)
    captured = capsys.readouterr()
    lines = captured.out.strip().split("\n")
    json_start = next(i for i, l in enumerate(lines) if l.strip() == "{")
    json_block = "\n".join(lines[json_start:])
    data = json.loads(json_block)
    assert "expression" in data


def test_build_annotate_parser_returns_parser():
    p = build_annotate_parser()
    assert isinstance(p, argparse.ArgumentParser)


def test_build_annotate_parser_subparsers():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_annotate_parser(sub)
    assert p is not None
