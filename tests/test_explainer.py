"""Tests for cronlens.explainer module."""

import pytest
from cronlens.parser import CronExpression
from cronlens.explainer import explain, _ordinal, _explain_field


@pytest.fixture
def parse(request):
    return CronExpression(request.param)


def test_ordinal_basic():
    assert _ordinal(1) == "1st"
    assert _ordinal(2) == "2nd"
    assert _ordinal(3) == "3rd"
    assert _ordinal(4) == "4th"
    assert _ordinal(11) == "11th"
    assert _ordinal(21) == "21st"


def test_explain_field_single_value():
    result = _explain_field([5], "minute")
    assert result == "at minute 5"


def test_explain_field_few_values():
    result = _explain_field([1, 2, 3], "hour")
    assert "1" in result and "2" in result and "3" in result


def test_explain_field_step_pattern():
    result = _explain_field(list(range(0, 60, 15)), "minute")
    assert "every 15" in result


def test_explain_every_minute():
    expr = CronExpression("* * * * *")
    result = explain(expr)
    assert "every minute" in result["summary"]


def test_explain_specific_time():
    expr = CronExpression("30 9 * * *")
    result = explain(expr)
    assert "09:30" in result["summary"]
    assert "minute" in result["minute"]
    assert "hour" in result["hour"]


def test_explain_weekdays_only():
    expr = CronExpression("0 8 * * 1-5")
    result = explain(expr)
    assert "Monday" in result["day_of_week"]
    assert "Friday" in result["day_of_week"]


def test_explain_monthly():
    expr = CronExpression("0 0 1 * *")
    result = explain(expr)
    assert "1st" in result["summary"] or "1" in result["day_of_month"]


def test_explain_specific_months():
    expr = CronExpression("0 12 * 3,6,9,12 *")
    result = explain(expr)
    assert "March" in result["month"]


def test_explain_returns_all_keys():
    expr = CronExpression("*/10 * * * *")
    result = explain(expr)
    expected_keys = {"minute", "hour", "day_of_month", "month", "day_of_week", "summary"}
    assert set(result.keys()) == expected_keys
