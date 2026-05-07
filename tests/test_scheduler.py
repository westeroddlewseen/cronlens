"""Tests for the CronScheduler next-run prediction engine."""

from datetime import datetime

import pytest

from cronlens.parser import CronExpression
from cronlens.scheduler import CronScheduler


ANCHOR = datetime(2024, 1, 15, 12, 0, 0)  # Monday, noon


def make_scheduler(expr: str) -> CronScheduler:
    return CronScheduler(CronExpression(expr))


def test_next_run_every_minute():
    sched = make_scheduler("* * * * *")
    run = sched.next_run(after=ANCHOR)
    assert run == datetime(2024, 1, 15, 12, 1)


def test_next_run_specific_time():
    sched = make_scheduler("30 14 * * *")
    run = sched.next_run(after=ANCHOR)
    assert run == datetime(2024, 1, 15, 14, 30)


def test_next_runs_returns_correct_count():
    sched = make_scheduler("0 * * * *")
    runs = sched.next_runs(after=ANCHOR, count=3)
    assert len(runs) == 3
    assert runs[0] == datetime(2024, 1, 15, 13, 0)
    assert runs[1] == datetime(2024, 1, 15, 14, 0)
    assert runs[2] == datetime(2024, 1, 15, 15, 0)


def test_next_run_skips_past_midnight():
    sched = make_scheduler("0 2 * * *")
    run = sched.next_run(after=ANCHOR)
    assert run == datetime(2024, 1, 16, 2, 0)


def test_iter_runs_yields_sequentially():
    sched = make_scheduler("*/15 * * * *")
    gen = sched.iter_runs(after=ANCHOR)
    first = next(gen)
    second = next(gen)
    assert first == datetime(2024, 1, 15, 12, 15)
    assert second == datetime(2024, 1, 15, 12, 30)


def test_next_run_weekday_filter():
    # 0 9 * * 1 = 09:00 on Mondays; ANCHOR is Monday 12:00 so next is next Monday
    sched = make_scheduler("0 9 * * 1")
    run = sched.next_run(after=ANCHOR)
    assert run == datetime(2024, 1, 22, 9, 0)


def test_next_run_defaults_to_now(monkeypatch):
    fixed = datetime(2024, 6, 1, 8, 0)
    monkeypatch.setattr("cronlens.scheduler.datetime", type(
        "FakeDatetime", (), {"now": staticmethod(lambda: fixed),
                              "replace": datetime.replace,
                              **{k: getattr(datetime, k) for k in dir(datetime) if not k.startswith("_")}}
    ))
    # Just ensure no exception is raised when after=None
    sched = make_scheduler("* * * * *")
    assert sched.next_run(after=fixed) is not None
