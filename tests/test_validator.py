"""Tests for cronlens.validator."""

import pytest
from cronlens.validator import validate, ValidationResult


def test_valid_every_minute():
    result = validate("* * * * *")
    assert result.valid is True
    assert result.errors == []


def test_valid_specific_time():
    result = validate("30 9 * * 1")
    assert result.valid is True


def test_valid_range():
    result = validate("0-30 8-17 * * 1-5")
    assert result.valid is True


def test_valid_step():
    result = validate("*/5 * * * *")
    assert result.valid is True


def test_valid_step_with_base():
    result = validate("0/15 * * * *")
    assert result.valid is True


def test_valid_list():
    result = validate("0,15,30,45 * * * *")
    assert result.valid is True


def test_wrong_field_count_too_few():
    result = validate("* * * *")
    assert result.valid is False
    assert any("5 fields" in str(e) for e in result.errors)


def test_wrong_field_count_too_many():
    result = validate("* * * * * *")
    assert result.valid is False


def test_minute_out_of_range():
    result = validate("60 * * * *")
    assert result.valid is False
    assert any(e.field == "minute" for e in result.errors)


def test_hour_out_of_range():
    result = validate("0 24 * * *")
    assert result.valid is False
    assert any(e.field == "hour" for e in result.errors)


def test_day_of_month_zero():
    result = validate("0 0 0 * *")
    assert result.valid is False
    assert any(e.field == "day_of_month" for e in result.errors)


def test_month_out_of_range():
    result = validate("0 0 1 13 *")
    assert result.valid is False
    assert any(e.field == "month" for e in result.errors)


def test_day_of_week_out_of_range():
    result = validate("0 0 * * 7")
    assert result.valid is False
    assert any(e.field == "day_of_week" for e in result.errors)


def test_invalid_range_reversed():
    result = validate("30-10 * * * *")
    assert result.valid is False
    assert any("start" in str(e) and "end" in str(e) for e in result.errors)


def test_invalid_step_zero():
    result = validate("*/0 * * * *")
    assert result.valid is False
    assert any("step" in str(e) for e in result.errors)


def test_non_numeric_value():
    result = validate("abc * * * *")
    assert result.valid is False


def test_summary_valid():
    result = validate("* * * * *")
    assert "valid" in result.summary().lower()
    assert "invalid" not in result.summary().lower()


def test_summary_invalid_lists_errors():
    result = validate("99 25 * * *")
    summary = result.summary()
    assert "invalid" in summary.lower()
    assert "minute" in summary
    assert "hour" in summary


def test_bool_true():
    assert bool(validate("* * * * *")) is True


def test_bool_false():
    assert bool(validate("99 * * * *")) is False
