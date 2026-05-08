"""Tests for cronlens.formatter module."""

import pytest
from datetime import datetime
from cronlens.parser import CronExpression
from cronlens.formatter import format_explanation, format_next_runs, format_full_report


FIXED_DT = datetime(2024, 6, 1, 12, 0)


def test_format_explanation_contains_fields():
    expr = CronExpression("0 9 * * 1")
    output = format_explanation(expr)
    assert "Minute" in output
    assert "Hour" in output
    assert "Day of Month" in output
    assert "Month" in output
    assert "Day of Week" in output
    assert "Summary" in output


def test_format_next_runs_count():
    expr = CronExpression("* * * * *")
    output = format_next_runs(expr, FIXED_DT, count=3)
    lines = [l for l in output.splitlines() if l.strip().startswith(("1.", "2.", "3.", "1", "2", "3"))]
    assert len(lines) == 3


def test_format_next_runs_includes_delta():
    expr = CronExpression("* * * * *")
    output = format_next_runs(expr, FIXED_DT, count=1)
    assert "in " in output


def test_format_next_runs_default_five():
    expr = CronExpression("*/5 * * * *")
    output = format_next_runs(expr, FIXED_DT)
    numbered = [l for l in output.splitlines() if ". " in l]
    assert len(numbered) == 5


def test_format_full_report_structure():
    output = format_full_report("0 12 * * *", FIXED_DT)
    assert "Cron Expression" in output
    assert "Human Readable" in output
    assert "Field Breakdown" in output
    assert "Next 5 runs" in output


def test_format_full_report_contains_expression():
    raw = "30 8 * * 1-5"
    output = format_full_report(raw, FIXED_DT)
    assert raw in output


def test_format_full_report_custom_count():
    output = format_full_report("* * * * *", FIXED_DT, count=3)
    assert "Next 3 runs" in output
