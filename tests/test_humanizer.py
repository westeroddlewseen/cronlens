"""Tests for the cron expression humanizer."""

import pytest

from cronlens.parser import CronExpression
from cronlens.humanizer import humanize


def h(expr: str) -> str:
    return humanize(CronExpression(expr))


def test_every_minute():
    assert h("* * * * *") == "every minute"


def test_specific_minute_every_hour():
    result = h("30 * * * *")
    assert "minute 30" in result


def test_specific_hour_and_minute():
    result = h("0 9 * * *")
    assert "minute 0" in result
    assert "hour 9" in result


def test_specific_day_of_month():
    result = h("0 0 1 * *")
    assert "day 1" in result


def test_specific_month():
    result = h("0 0 * 6 *")
    assert "June" in result


def test_specific_weekday():
    result = h("0 9 * * 1")
    assert "Monday" in result


def test_multiple_weekdays():
    result = h("0 9 * * 1,3,5")
    assert "Monday" in result
    assert "Wednesday" in result
    assert "Friday" in result


def test_every_hour():
    result = h("0 * * * *")
    assert "minute 0" in result


def test_step_minutes():
    result = h("*/15 * * * *")
    assert "minute" in result
