"""Tests for cronlens.profiler."""

import pytest
from cronlens.parser import CronExpression
from cronlens.profiler import profile, ProfileResult


def parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


def test_profile_returns_profile_result():
    result = profile(parse("* * * * *"))
    assert isinstance(result, ProfileResult)


def test_every_minute_is_high_frequency():
    result = profile(parse("* * * * *"))
    assert result.is_high_frequency is True
    assert result.frequency_per_day == pytest.approx(1440, rel=0.01)


def test_hourly_not_high_frequency():
    result = profile(parse("0 * * * *"))
    assert result.is_high_frequency is False
    assert result.frequency_per_day == pytest.approx(24, rel=0.01)


def test_business_hours_detected():
    # Runs every minute from 9 to 17 (9 hours inclusive = 9..17)
    result = profile(parse("* 9-17 * * *"))
    assert result.is_business_hours is True


def test_non_business_hours_not_flagged():
    result = profile(parse("0 0 * * *"))
    assert result.is_business_hours is False


def test_overnight_detected():
    result = profile(parse("0 1-5 * * *"))
    assert result.is_overnight is True


def test_weekday_only_detected():
    result = profile(parse("0 9 * * 1-5"))
    assert result.is_weekday_only is True
    assert result.is_weekend_only is False


def test_weekend_only_detected():
    result = profile(parse("0 10 * * 0,6"))
    assert result.is_weekend_only is True
    assert result.is_weekday_only is False


def test_dom_dow_conflict_detected():
    result = profile(parse("0 0 1 * 1"))
    assert result.dom_dow_conflict is True
    assert any("day-of-month" in a for a in result.anomalies)


def test_no_conflict_when_only_dom():
    result = profile(parse("0 0 15 * *"))
    assert result.dom_dow_conflict is False


def test_no_conflict_when_only_dow():
    result = profile(parse("0 0 * * 1"))
    assert result.dom_dow_conflict is False


def test_clean_expression_has_no_anomalies():
    result = profile(parse("0 6 * * *"))
    assert result.clean is True
    assert result.anomalies == []


def test_summary_contains_expression():
    result = profile(parse("30 8 * * 1-5"))
    summary = result.summary()
    assert "30 8 * * 1-5" in summary


def test_summary_contains_frequency():
    result = profile(parse("0 * * * *"))
    summary = result.summary()
    assert "24" in summary


def test_hourly_on_the_hour_note():
    result = profile(parse("0 * * * *"))
    assert any("once per hour" in n for n in result.notes)
