"""Tests for cronlens.ranker."""

import pytest
from cronlens.parser import CronExpression
from cronlens.ranker import CronRank, rank, rank_many, _frequency_per_day, _regularity, _complexity


def parse(expr: str) -> CronExpression:
    return CronExpression(expr)


# --- frequency ---

def test_every_minute_frequency_is_1440():
    expr = parse("* * * * *")
    assert _frequency_per_day(expr) == pytest.approx(1440 / 7 * 7, rel=0.01)


def test_hourly_frequency_is_24():
    expr = parse("0 * * * *")
    freq = _frequency_per_day(expr)
    assert freq == pytest.approx(24.0, rel=0.05)


def test_daily_midnight_frequency_less_than_2():
    expr = parse("0 0 * * *")
    freq = _frequency_per_day(expr)
    assert 0 < freq <= 2


def test_weekly_frequency_less_than_daily():
    daily = _frequency_per_day(parse("0 0 * * *"))
    weekly = _frequency_per_day(parse("0 0 * * 0"))
    assert weekly < daily


# --- regularity ---

def test_single_minute_is_perfectly_regular():
    expr = parse("0 * * * *")
    assert _regularity(expr) == pytest.approx(1.0)


def test_evenly_spaced_minutes_high_regularity():
    expr = parse("0,15,30,45 * * * *")
    score = _regularity(expr)
    assert score >= 0.9


def test_unevenly_spaced_minutes_lower_regularity():
    even = _regularity(parse("0,15,30,45 * * * *"))
    uneven = _regularity(parse("0,1,30,59 * * * *"))
    assert even > uneven


# --- complexity ---

def test_wildcard_expression_moderate_complexity():
    expr = parse("* * * * *")
    score = _complexity(expr)
    assert 0 < score <= 1.0


def test_single_value_expression_low_complexity():
    expr = parse("0 0 1 1 0")
    score = _complexity(expr)
    assert score < 0.2


# --- rank ---

def test_rank_returns_cron_rank():
    result = rank(parse("* * * * *"))
    assert isinstance(result, CronRank)


def test_rank_label_every_minute():
    result = rank(parse("* * * * *"))
    assert result.label == "high-frequency"


def test_rank_label_daily():
    result = rank(parse("0 9 * * *"))
    assert result.label in ("regular", "irregular", "weekly", "rare")


def test_rank_overall_score_type():
    result = rank(parse("0 * * * *"))
    assert isinstance(result.overall_score, float)


# --- rank_many ---

def test_rank_many_sorted_descending():
    exprs = [parse(e) for e in ["0 0 * * *", "* * * * *", "0 * * * *"]]
    results = rank_many(exprs)
    scores = [r.overall_score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_rank_many_length_preserved():
    exprs = [parse(e) for e in ["0 0 1 1 *", "*/5 * * * *", "0 12 * * 1"]]
    assert len(rank_many(exprs)) == 3


def test_rank_many_empty_list():
    assert rank_many([]) == []
