"""Tests for cronlens.parser module."""

import pytest
from cronlens.parser import parse, CronExpression, CronField


def test_parse_returns_cron_expression():
    expr = parse("* * * * *")
    assert isinstance(expr, CronExpression)
    assert expr.raw == "* * * * *"


def test_wildcard_expands_all_values():
    expr = parse("* * * * *")
    assert expr.minute.values == list(range(0, 60))
    assert expr.hour.values == list(range(0, 24))
    assert expr.day_of_month.values == list(range(1, 32))
    assert expr.month.values == list(range(1, 13))
    assert expr.day_of_week.values == list(range(0, 7))


def test_specific_values():
    expr = parse("30 9 15 6 1")
    assert expr.minute.values == [30]
    assert expr.hour.values == [9]
    assert expr.day_of_month.values == [15]
    assert expr.month.values == [6]
    assert expr.day_of_week.values == [1]


def test_range_field():
    expr = parse("0-5 * * * *")
    assert expr.minute.values == [0, 1, 2, 3, 4, 5]


def test_step_field():
    expr = parse("*/15 * * * *")
    assert expr.minute.values == [0, 15, 30, 45]


def test_step_with_range():
    expr = parse("0-30/10 * * * *")
    assert expr.minute.values == [0, 10, 20, 30]


def test_list_field():
    expr = parse("0 9,12,18 * * *")
    assert expr.hour.values == [9, 12, 18]


def test_month_name_aliases():
    expr = parse("0 0 1 jan *")
    assert expr.month.values == [1]

    expr2 = parse("0 0 1 dec *")
    assert expr2.month.values == [12]


def test_day_of_week_name_aliases():
    expr = parse("0 0 * * mon")
    assert expr.day_of_week.values == [1]

    expr2 = parse("0 0 * * sun")
    assert expr2.day_of_week.values == [0]


def test_is_wildcard_flag():
    expr = parse("* 0 * * *")
    assert expr.minute.is_wildcard is True
    assert expr.hour.is_wildcard is False


def test_invalid_field_count_raises():
    with pytest.raises(ValueError, match="Expected 5 fields"):
        parse("* * * *")


def test_out_of_range_raises():
    with pytest.raises(ValueError, match="out of range"):
        parse("60 * * * *")

    with pytest.raises(ValueError, match="out of range"):
        parse("* 25 * * *")


def test_fields_property_order():
    expr = parse("1 2 3 4 5")
    fields = expr.fields
    assert len(fields) == 5
    assert fields[0].field == "minute"
    assert fields[4].field == "day_of_week"
