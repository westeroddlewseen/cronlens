"""Tests for cronlens.comparator."""

import pytest
from cronlens.parser import CronExpression
from cronlens.comparator import compare, format_comparison, ComparisonReport


def parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


# --- compare() ---

def test_compare_returns_comparison_report():
    report = compare(parse("* * * * *"), parse("0 * * * *"))
    assert isinstance(report, ComparisonReport)


def test_identical_expressions_flagged():
    report = compare(parse("0 9 * * 1"), parse("0 9 * * 1"))
    assert report.is_identical is True
    assert report.changed_fields == []


def test_different_expressions_not_identical():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    assert report.is_identical is False


def test_changed_fields_detected():
    report = compare(parse("* * * * *"), parse("0 * * * *"))
    assert "minute" in report.changed_fields


def test_human_text_populated():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    assert len(report.human_a) > 0
    assert len(report.human_b) > 0


def test_more_frequent_every_minute_vs_daily():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    assert report.more_frequent == "a"


def test_more_frequent_daily_vs_every_minute():
    report = compare(parse("0 0 * * *"), parse("* * * * *"))
    assert report.more_frequent == "b"


def test_equal_frequency():
    report = compare(parse("0 9 * * *"), parse("0 17 * * *"))
    assert report.more_frequent == "equal"


def test_scores_are_floats():
    report = compare(parse("* * * * *"), parse("*/5 * * * *"))
    assert isinstance(report.score_a, float)
    assert isinstance(report.score_b, float)


def test_freq_values_positive():
    report = compare(parse("* * * * *"), parse("0 * * * *"))
    assert report.freq_a > 0
    assert report.freq_b > 0


def test_expr_strings_stored():
    report = compare(parse("*/5 * * * *"), parse("0 12 * * 1-5"))
    assert "*/5" in report.expr_a or "*" in report.expr_a
    assert report.expr_b is not None


# --- format_comparison() ---

def test_format_comparison_returns_string():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    output = format_comparison(report)
    assert isinstance(output, str)


def test_format_comparison_contains_header():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    output = format_comparison(report)
    assert "Cron Comparison" in output


def test_format_comparison_shows_identical_yes():
    report = compare(parse("0 9 * * *"), parse("0 9 * * *"))
    output = format_comparison(report)
    assert "yes" in output


def test_format_comparison_shows_identical_no():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    output = format_comparison(report)
    assert "no" in output


def test_format_comparison_shows_freq_line():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    output = format_comparison(report)
    assert "Freq/day" in output


def test_format_comparison_shows_score_line():
    report = compare(parse("* * * * *"), parse("0 0 * * *"))
    output = format_comparison(report)
    assert "Score" in output
