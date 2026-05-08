"""Tests for cronlens.history module."""

from datetime import datetime, timedelta

import pytest

from cronlens.history import build_history, ExecutionWindow, HistorySummary


START = datetime(2024, 1, 1, 0, 0, 0)
ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)


def test_every_minute_one_hour_has_60_runs():
    summary = build_history("* * * * *", START, START + ONE_HOUR)
    assert summary.actual_count == 60


def test_every_minute_expected_matches_actual():
    summary = build_history("* * * * *", START, START + ONE_HOUR)
    assert summary.expected_count == summary.actual_count


def test_hourly_one_day_has_24_runs():
    summary = build_history("0 * * * *", START, START + ONE_DAY)
    assert summary.actual_count == 24


def test_daily_midnight_one_week():
    end = START + timedelta(days=7)
    summary = build_history("0 0 * * *", START, end)
    assert summary.actual_count == 7


def test_first_and_last_run_are_set():
    summary = build_history("0 * * * *", START, START + ONE_DAY)
    assert summary.first_run is not None
    assert summary.last_run is not None
    assert summary.first_run < summary.last_run


def test_no_runs_in_empty_window():
    # Window of zero duration
    summary = build_history("* * * * *", START, START)
    assert summary.actual_count == 0
    assert summary.first_run is None
    assert summary.last_run is None


def test_coverage_percent_full():
    summary = build_history("* * * * *", START, START + ONE_HOUR)
    assert summary.coverage_percent() == pytest.approx(100.0)


def test_coverage_percent_zero_when_no_expected():
    summary = build_history("* * * * *", START, START)
    assert summary.coverage_percent() == 0.0


def test_expression_stored_on_summary():
    expr = "30 9 * * 1-5"
    summary = build_history(expr, START, START + ONE_DAY)
    assert summary.expression == expr


def test_execution_window_duration_hours():
    window = ExecutionWindow(start=START, end=START + ONE_HOUR, expected=60)
    assert window.duration_hours == pytest.approx(1.0)


def test_count_limit_caps_results():
    summary = build_history("* * * * *", START, START + timedelta(days=1), count_limit=10)
    assert summary.actual_count == 10


def test_runs_are_within_window():
    end = START + ONE_HOUR
    summary = build_history("* * * * *", START, end)
    for run in summary.run_times:
        assert START <= run < end
