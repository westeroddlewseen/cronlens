"""Tests for cronlens.converter module."""

import pytest
from cronlens.converter import to_alias, to_quartz, from_quartz, to_dict, from_dict


# --- to_alias ---

def test_to_alias_daily():
    assert to_alias("0 0 * * *") == "@daily"


def test_to_alias_hourly():
    assert to_alias("0 * * * *") == "@hourly"


def test_to_alias_every_minute():
    assert to_alias("* * * * *") == "@every_minute"


def test_to_alias_unknown_returns_none():
    assert to_alias("5 4 * * 1") is None


def test_to_alias_normalizes_extra_spaces():
    assert to_alias("0  0  *  *  *") == "@daily"


# --- to_quartz ---

def test_to_quartz_prepends_zero_seconds():
    result = to_quartz("5 4 * * *")
    assert result == "0 5 4 * * *"


def test_to_quartz_every_minute():
    assert to_quartz("* * * * *") == "0 * * * * *"


def test_to_quartz_alias_resolved():
    result = to_quartz("@daily")
    assert result == "0 0 0 * * *"


def test_to_quartz_rejects_wrong_field_count():
    with pytest.raises(ValueError, match="5-field"):
        to_quartz("0 * * * * *")  # already 6 fields


# --- from_quartz ---

def test_from_quartz_strips_seconds():
    assert from_quartz("0 5 4 * * *") == "5 4 * * *"


def test_from_quartz_every_minute():
    assert from_quartz("0 * * * * *") == "* * * * *"


def test_from_quartz_rejects_wrong_field_count():
    with pytest.raises(ValueError, match="6-field"):
        from_quartz("* * * * *")


# --- to_dict ---

def test_to_dict_returns_all_keys():
    d = to_dict("0 9 * * 1")
    assert set(d.keys()) == {"minute", "hour", "day_of_month", "month", "day_of_week"}


def test_to_dict_specific_values():
    d = to_dict("30 14 * * *")
    assert d["minute"] == [30]
    assert d["hour"] == [14]


def test_to_dict_wildcard_expands_all_minutes():
    d = to_dict("* * * * *")
    assert d["minute"] == list(range(60))


def test_to_dict_resolves_alias():
    d = to_dict("@daily")
    assert d["minute"] == [0]
    assert d["hour"] == [0]


# --- from_dict ---

def test_from_dict_basic():
    result = from_dict({"minute": [0], "hour": [9], "day_of_month": "*", "month": "*", "day_of_week": "*"})
    assert result == "0 9 * * *"


def test_from_dict_multiple_minutes():
    result = from_dict({"minute": [0, 15, 30, 45], "hour": "*", "day_of_month": "*", "month": "*", "day_of_week": "*"})
    assert result == "0,15,30,45 * * * *"


def test_from_dict_deduplicates_values():
    result = from_dict({"minute": [5, 5, 10], "hour": "*", "day_of_month": "*", "month": "*", "day_of_week": "*"})
    assert result == "5,10 * * * *"


def test_from_dict_roundtrip():
    original = "30 6 * * 1"
    assert from_dict(to_dict(original)) == original
