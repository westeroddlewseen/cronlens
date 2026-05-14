"""Tests for cronlens.tagger module."""

import pytest
from cronlens.parser import CronExpression
from cronlens.tagger import tag, TagResult, KNOWN_TAGS


def parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


def test_tag_returns_tag_result():
    result = tag(parse("* * * * *"))
    assert isinstance(result, TagResult)


def test_every_minute_is_frequent():
    result = tag(parse("* * * * *"))
    assert result.has("frequent")


def test_hourly_tag():
    result = tag(parse("0 * * * *"))
    assert result.has("hourly")
    assert not result.has("frequent")


def test_daily_tag():
    result = tag(parse("0 9 * * *"))
    assert result.has("daily")


def test_weekly_tag():
    result = tag(parse("0 9 * * 1"))
    assert result.has("weekly")


def test_monthly_tag():
    result = tag(parse("0 9 1 * *"))
    assert result.has("monthly")


def test_business_hours_tag():
    result = tag(parse("0 9-17 * * *"))
    assert result.has("business-hours")


def test_off_hours_tag():
    result = tag(parse("0 2 * * *"))
    assert result.has("off-hours")


def test_weekend_tag():
    result = tag(parse("0 10 * * 0,6"))
    assert result.has("weekend")


def test_weekday_tag():
    result = tag(parse("0 9 * * 1-5"))
    assert result.has("weekday")


def test_simple_tag_for_specific_time():
    result = tag(parse("30 6 * * *"))
    assert result.has("simple")


def test_complex_tag_for_every_minute():
    result = tag(parse("* * * * *"))
    assert result.has("complex")


def test_has_returns_false_for_missing_tag():
    result = tag(parse("0 9 1 * *"))
    assert not result.has("weekend")


def test_tags_are_subset_of_known_tags():
    result = tag(parse("0 9 * * 1-5"))
    for t in result.tags:
        assert t in KNOWN_TAGS


def test_repr_contains_tags():
    result = tag(parse("0 9 * * *"))
    assert "TagResult" in repr(result)
    assert "tags" in repr(result)
