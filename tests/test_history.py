"""Tests for cronlens.history — execution window analysis."""

import pytest
from datetime import datetime, timezone
from cronlens.history import ExecutionWindow, HistorySummary, analyze_history
from cronlens.parser import CronExpression


def utc(*args):
    """Convenience factory for UTC datetimes."""
    return datetime(*args, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# ExecutionWindow
# ---------------------------------------------------------------------------

def test_every_minute_one_hour_has_60_runs():
    expr = CronExpression.parse("* * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 1, 1, 0),
    )
    assert window.actual_count() == 60


def test_every_minute_expected_matches_actual():
    expr = CronExpression.parse("* * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 1, 1, 0),
    )
    assert window.actual_count() == window.expected_count()


def test_hourly_one_day_has_24_runs():
    expr = CronExpression.parse("0 * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 2, 0, 0),
    )
    assert window.actual_count() == 24


def test_daily_midnight_one_week():
    expr = CronExpression.parse("0 0 * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 8, 0, 0),
    )
    assert window.actual_count() == 7


def test_first_and_last_run_are_set():
    expr = CronExpression.parse("0 9 * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 4, 0, 0),
    )
    runs = window.runs()
    assert runs[0] == utc(2024, 1, 1, 9, 0)
    assert runs[-1] == utc(2024, 1, 3, 9, 0)


def test_duration_hours():
    expr = CronExpression.parse("* * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 1, 6, 0),
    )
    assert window.duration_hours() == 6.0


def test_no_runs_in_empty_window():
    expr = CronExpression.parse("0 0 * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 1),
        end=utc(2024, 1, 1, 23, 59),
    )
    assert window.actual_count() == 0


# ---------------------------------------------------------------------------
# HistorySummary
# ---------------------------------------------------------------------------

def test_history_summary_missed_runs():
    expr = CronExpression.parse("* * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 1, 1, 0),
    )
    # Simulate 10 missed runs
    summary = HistorySummary(window=window, observed=50)
    assert summary.missed() == 10


def test_history_summary_no_missed_runs():
    expr = CronExpression.parse("0 * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 2, 0, 0),
    )
    summary = HistorySummary(window=window, observed=24)
    assert summary.missed() == 0


def test_history_summary_reliability_full():
    expr = CronExpression.parse("0 * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 2, 0, 0),
    )
    summary = HistorySummary(window=window, observed=24)
    assert summary.reliability() == 1.0


def test_history_summary_reliability_partial():
    expr = CronExpression.parse("* * * * *")
    window = ExecutionWindow(
        expression=expr,
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 1, 1, 0),
    )
    summary = HistorySummary(window=window, observed=30)
    assert abs(summary.reliability() - 0.5) < 1e-9


# ---------------------------------------------------------------------------
# analyze_history helper
# ---------------------------------------------------------------------------

def test_analyze_history_returns_summary():
    summary = analyze_history(
        expression="0 9 * * 1-5",
        start=utc(2024, 1, 1, 0, 0),  # Monday
        end=utc(2024, 1, 8, 0, 0),
        observed=5,
    )
    assert isinstance(summary, HistorySummary)
    assert summary.missed() == 0


def test_analyze_history_string_expression():
    """analyze_history should accept a raw cron string."""
    summary = analyze_history(
        expression="*/5 * * * *",
        start=utc(2024, 1, 1, 0, 0),
        end=utc(2024, 1, 1, 1, 0),
        observed=12,
    )
    assert summary.window.actual_count() == 12
    assert summary.missed() == 0
