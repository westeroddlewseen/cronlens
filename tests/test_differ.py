"""Tests for cronlens.differ module."""

import pytest
from cronlens.differ import diff_expressions, format_diff, FieldDiff, CronDiff


def test_identical_expressions_have_no_changes():
    diff = diff_expressions("* * * * *", "* * * * *")
    assert not diff.has_changes


def test_different_minute_detected():
    diff = diff_expressions("0 * * * *", "30 * * * *")
    assert diff.has_changes
    changed = {d.field for d in diff.changed_fields}
    assert "minute" in changed


def test_changed_fields_excludes_unchanged():
    diff = diff_expressions("0 12 * * *", "0 14 * * *")
    changed = {d.field for d in diff.changed_fields}
    assert "hour" in changed
    assert "minute" not in changed


def test_field_diff_added_and_removed():
    diff = diff_expressions("0 * * * *", "30 * * * *")
    minute_diff = next(d for d in diff.field_diffs if d.field == "minute")
    assert 0 in minute_diff.removed
    assert 30 in minute_diff.added


def test_wildcard_vs_specific():
    diff = diff_expressions("* * * * *", "0 * * * *")
    minute_diff = next(d for d in diff.field_diffs if d.field == "minute")
    assert minute_diff.changed
    assert 0 in minute_diff.values_b
    assert len(minute_diff.values_a) == 60


def test_multiple_fields_changed():
    diff = diff_expressions("0 12 1 * *", "30 6 15 * *")
    changed = {d.field for d in diff.changed_fields}
    assert "minute" in changed
    assert "hour" in changed
    assert "day_of_month" in changed
    assert "month" not in changed


def test_format_diff_no_changes():
    diff = diff_expressions("* * * * *", "* * * * *")
    result = format_diff(diff)
    assert "No differences" in result


def test_format_diff_shows_field_name():
    diff = diff_expressions("0 * * * *", "30 * * * *")
    result = format_diff(diff)
    assert "minute" in result


def test_format_diff_shows_added_and_removed():
    diff = diff_expressions("0 * * * *", "30 * * * *")
    result = format_diff(diff)
    assert "removed" in result
    assert "added" in result


def test_diff_stores_original_expressions():
    diff = diff_expressions("0 12 * * *", "0 14 * * *")
    assert diff.expr_a == "0 12 * * *"
    assert diff.expr_b == "0 14 * * *"


def test_field_diff_unchanged_not_changed():
    fd = FieldDiff("month", [1, 2, 3], [1, 2, 3])
    assert not fd.changed
    assert fd.added == []
    assert fd.removed == []
