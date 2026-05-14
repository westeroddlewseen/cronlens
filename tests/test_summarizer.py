"""Tests for cronlens.summarizer."""

import pytest
from cronlens.parser import CronExpression
from cronlens.summarizer import summarize, ExpressionSummary, DigestReport


def parse(expr: str) -> CronExpression:
    return CronExpression(expr)


def test_summarize_returns_digest_report():
    exprs = [parse("* * * * *"), parse("0 * * * *")]
    report = summarize(exprs)
    assert isinstance(report, DigestReport)


def test_summarize_count_matches_input():
    exprs = [parse("* * * * *"), parse("0 9 * * 1"), parse("0 0 1 * *")]
    report = summarize(exprs)
    assert len(report.summaries) == 3


def test_each_summary_has_human_text():
    report = summarize([parse("0 9 * * 1")])
    assert report.summaries[0].human != ""


def test_most_frequent_is_every_minute():
    every_min = parse("* * * * *")
    hourly = parse("0 * * * *")
    report = summarize([every_min, hourly])
    assert report.most_frequent.expression == str(every_min)


def test_least_frequent_is_monthly():
    every_min = parse("* * * * *")
    monthly = parse("0 0 1 * *")
    report = summarize([every_min, monthly])
    assert report.least_frequent.expression == str(monthly)


def test_average_frequency_is_between_extremes():
    exprs = [parse("* * * * *"), parse("0 0 * * *")]
    report = summarize(exprs)
    assert report.least_frequent.frequency_per_day < report.average_frequency < report.most_frequent.frequency_per_day


def test_unique_tags_are_deduplicated():
    exprs = [parse("* * * * *"), parse("0 * * * *"), parse("0 0 * * *")]
    report = summarize(exprs)
    assert len(report.unique_tags) == len(set(report.unique_tags))


def test_tag_counts_sum_correctly():
    exprs = [parse("* * * * *"), parse("0 * * * *")]
    report = summarize(exprs)
    tag_counts = report.tag_counts()
    total = sum(tag_counts.values())
    total_tags_in_summaries = sum(len(s.tags) for s in report.summaries)
    assert total == total_tags_in_summaries


def test_empty_expressions_raises():
    with pytest.raises(ValueError):
        summarize([])


def test_single_expression_most_and_least_same():
    report = summarize([parse("0 12 * * *")])
    assert report.most_frequent.expression == report.least_frequent.expression


def test_average_score_within_range():
    exprs = [parse("* * * * *"), parse("0 9 * * 1-5")]
    report = summarize(exprs)
    assert 0.0 <= report.average_score <= 1.0
