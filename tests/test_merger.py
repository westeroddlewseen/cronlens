"""Tests for cronlens.merger module."""

import pytest
from cronlens.parser import CronExpression
from cronlens.merger import merge_expressions, format_merge_report, MergeResult


def parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


def test_merge_single_expression_returns_itself():
    expr = parse("0 * * * *")
    result = merge_expressions([expr])
    assert result.expressions == [expr]
    assert result.common_minutes() == {0}
    assert result.union_minutes() == {0}


def test_identical_expressions_flagged():
    a = parse("0 12 * * *")
    b = parse("0 12 * * *")
    result = merge_expressions([a, b])
    assert result.all_identical is True


def test_different_expressions_not_identical():
    a = parse("0 12 * * *")
    b = parse("30 12 * * *")
    result = merge_expressions([a, b])
    assert result.all_identical is False


def test_common_minutes_intersection():
    a = parse("0,30 * * * *")
    b = parse("0,15 * * * *")
    result = merge_expressions([a, b])
    assert result.common_minutes() == {0}


def test_union_minutes():
    a = parse("0,30 * * * *")
    b = parse("15,45 * * * *")
    result = merge_expressions([a, b])
    assert result.union_minutes() == {0, 15, 30, 45}


def test_common_hours():
    a = parse("* 6,12 * * *")
    b = parse("* 12,18 * * *")
    result = merge_expressions([a, b])
    assert result.common_hours() == {12}


def test_no_common_minutes_returns_empty():
    a = parse("0 * * * *")
    b = parse("30 * * * *")
    result = merge_expressions([a, b])
    assert result.common_minutes() == set()


def test_three_expressions_union():
    a = parse("0 * * * *")
    b = parse("15 * * * *")
    c = parse("30 * * * *")
    result = merge_expressions([a, b, c])
    assert result.union_minutes() == {0, 15, 30}


def test_three_expressions_common():
    a = parse("0,15,30 * * * *")
    b = parse("0,30 * * * *")
    c = parse("0,30,45 * * * *")
    result = merge_expressions([a, b, c])
    assert result.common_minutes() == {0, 30}


def test_empty_expressions_raises():
    with pytest.raises(ValueError):
        merge_expressions([])


def test_format_merge_report_identical():
    a = parse("* * * * *")
    b = parse("* * * * *")
    result = merge_expressions([a, b])
    report = format_merge_report(result)
    assert "identical" in report.lower()


def test_format_merge_report_shows_union_and_common():
    a = parse("0 * * * *")
    b = parse("30 * * * *")
    result = merge_expressions([a, b])
    report = format_merge_report(result)
    assert "union" in report.lower()
    assert "common" in report.lower()
    assert "(none)" in report


def test_format_merge_report_expression_count():
    exprs = [parse("0 * * * *"), parse("30 * * * *"), parse("15 * * * *")]
    result = merge_expressions(exprs)
    report = format_merge_report(result)
    assert "3" in report
