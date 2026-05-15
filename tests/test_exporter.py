"""Tests for cronlens.exporter."""

import json
import pytest

from cronlens.parser import CronExpression
from cronlens.exporter import (
    export_json,
    export_csv,
    export_markdown,
    _build_record,
)


def parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


# --- _build_record ---

def test_build_record_has_expression():
    rec = _build_record(parse("0 * * * *"))
    assert rec.expression == "0 * * * *"


def test_build_record_human_is_string():
    rec = _build_record(parse("0 * * * *"))
    assert isinstance(rec.human, str)
    assert len(rec.human) > 0


def test_build_record_tags_is_list():
    rec = _build_record(parse("* * * * *"))
    assert isinstance(rec.tags, list)


def test_build_record_next_runs_count():
    rec = _build_record(parse("0 9 * * 1"), count=5)
    assert len(rec.next_runs) == 5


def test_build_record_fields_keys():
    rec = _build_record(parse("30 6 * * *"))
    assert set(rec.fields.keys()) == {"minutes", "hours", "days_of_month", "months", "days_of_week"}


def test_build_record_to_dict_serializable():
    rec = _build_record(parse("0 0 1 1 *"))
    d = rec.to_dict()
    assert isinstance(d, dict)
    assert "expression" in d


# --- export_json ---

def test_export_json_valid_json():
    result = export_json([parse("* * * * *")])
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 1


def test_export_json_multiple_expressions():
    exprs = [parse("* * * * *"), parse("0 0 * * *")]
    data = json.loads(export_json(exprs))
    assert len(data) == 2


def test_export_json_contains_human():
    data = json.loads(export_json([parse("0 9 * * 1")]))
    assert "human" in data[0]


# --- export_csv ---

def test_export_csv_has_header():
    result = export_csv([parse("* * * * *")])
    assert result.startswith("expression,human")


def test_export_csv_row_count():
    exprs = [parse("* * * * *"), parse("0 0 * * *"), parse("0 9 * * 1")]
    lines = export_csv(exprs).strip().splitlines()
    assert len(lines) == 4  # header + 3 rows


def test_export_csv_contains_expression():
    result = export_csv([parse("0 12 * * *")])
    assert "0 12 * * *" in result


# --- export_markdown ---

def test_export_markdown_has_table_header():
    result = export_markdown([parse("* * * * *")])
    assert "| Expression |" in result


def test_export_markdown_has_separator():
    result = export_markdown([parse("* * * * *")])
    assert "| --- |" in result


def test_export_markdown_contains_expression():
    result = export_markdown([parse("0 0 1 * *")])
    assert "0 0 1 * *" in result
