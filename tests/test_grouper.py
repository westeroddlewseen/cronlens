"""Tests for cronlens.grouper and cronlens.cli_grouper."""

import pytest

from cronlens.grouper import group_expressions, ExpressionGroup, GroupReport
from cronlens.cli_grouper import format_group_report


# ---------------------------------------------------------------------------
# group_expressions
# ---------------------------------------------------------------------------

def test_group_report_returned():
    report = group_expressions(["* * * * *"])
    assert isinstance(report, GroupReport)


def test_every_minute_lands_in_frequent():
    report = group_expressions(["* * * * *"])
    assert "frequent" in report.groups
    assert "* * * * *" in report.groups["frequent"].expressions


def test_hourly_expression_grouped():
    report = group_expressions(["0 * * * *"])
    assert "hourly" in report.groups


def test_daily_expression_grouped():
    report = group_expressions(["0 9 * * *"])
    assert "daily" in report.groups


def test_weekly_expression_grouped():
    report = group_expressions(["0 9 * * 1"])
    assert "weekly" in report.groups


def test_monthly_expression_grouped():
    report = group_expressions(["0 9 1 * *"])
    assert "monthly" in report.groups


def test_invalid_expression_goes_to_ungrouped():
    report = group_expressions(["not_a_cron"])
    assert "not_a_cron" in report.ungrouped


def test_multiple_expressions_split_into_groups():
    exprs = ["* * * * *", "0 * * * *", "0 9 * * *"]
    report = group_expressions(exprs)
    assert len(report.groups) >= 2


def test_group_names_returns_list():
    report = group_expressions(["* * * * *", "0 9 * * *"])
    assert isinstance(report.group_names, list)


def test_get_missing_group_returns_empty():
    report = group_expressions(["* * * * *"])
    empty = report.get("nonexistent")
    assert isinstance(empty, ExpressionGroup)
    assert len(empty) == 0


def test_expression_group_len():
    grp = ExpressionGroup(label="daily", expressions=["0 9 * * *", "0 12 * * *"])
    assert len(grp) == 2


def test_empty_input_returns_empty_report():
    report = group_expressions([])
    assert report.groups == {}
    assert report.ungrouped == []


# ---------------------------------------------------------------------------
# format_group_report
# ---------------------------------------------------------------------------

def test_format_contains_group_label():
    report = group_expressions(["* * * * *"])
    output = format_group_report(report)
    assert "FREQUENT" in output


def test_format_contains_expression():
    report = group_expressions(["0 9 * * *"])
    output = format_group_report(report)
    assert "0 9 * * *" in output


def test_format_empty_report():
    from cronlens.grouper import GroupReport
    report = GroupReport(groups={}, ungrouped=[])
    output = format_group_report(report)
    assert "No expressions" in output


def test_format_invalid_section_present():
    report = group_expressions(["bad_expr"])
    output = format_group_report(report)
    assert "INVALID" in output
