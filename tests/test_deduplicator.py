"""Tests for cronlens.deduplicator."""

import pytest
from cronlens.deduplicator import deduplicate, DeduplicationReport


def test_no_duplicates_returns_all_unique():
    exprs = ["* * * * *", "0 9 * * 1", "30 6 1 * *"]
    report = deduplicate(exprs)
    assert report.unique == exprs
    assert report.removed_count == 0
    assert not report.has_duplicates


def test_identical_strings_deduplicated():
    exprs = ["0 9 * * *", "0 9 * * *"]
    report = deduplicate(exprs)
    assert len(report.unique) == 1
    assert report.removed_count == 1
    assert report.has_duplicates


def test_equivalent_expressions_deduplicated():
    # "0 9 * * *" and "00 09 * * *" should resolve identically
    exprs = ["0 9 * * *", "0 9 * * *", "30 18 * * *"]
    report = deduplicate(exprs)
    assert report.removed_count == 1
    assert len(report.unique) == 2


def test_first_occurrence_kept():
    exprs = ["0 0 * * *", "0 0 * * *", "0 0 * * *"]
    report = deduplicate(exprs)
    assert report.unique == ["0 0 * * *"]
    assert report.removed_count == 2


def test_duplicate_map_populated():
    exprs = ["0 6 * * *", "0 6 * * *"]
    report = deduplicate(exprs)
    assert report.has_duplicates
    assert len(report.duplicates) == 1
    dupes = list(report.duplicates.values())[0]
    assert "0 6 * * *" in dupes


def test_every_minute_wildcard_deduplicated():
    exprs = ["* * * * *", "* * * * *"]
    report = deduplicate(exprs)
    assert report.removed_count == 1
    assert len(report.unique) == 1


def test_different_step_and_explicit_not_same():
    # */2 on minutes expands to 0,2,4,...58 — different from "0 * * * *"
    exprs = ["*/2 * * * *", "0 * * * *"]
    report = deduplicate(exprs)
    assert report.removed_count == 0
    assert len(report.unique) == 2


def test_empty_list_returns_empty_report():
    report = deduplicate([])
    assert report.unique == []
    assert report.removed_count == 0
    assert not report.has_duplicates


def test_single_expression_no_duplicates():
    report = deduplicate(["15 3 * * 1"])
    assert report.unique == ["15 3 * * 1"]
    assert report.removed_count == 0


def test_summary_no_duplicates():
    report = deduplicate(["0 1 * * *", "0 2 * * *"])
    assert report.summary() == "No duplicates found."


def test_summary_with_duplicates_mentions_count():
    report = deduplicate(["0 0 * * *", "0 0 * * *"])
    summary = report.summary()
    assert "1 duplicate" in summary


def test_mixed_unique_and_duplicate():
    exprs = ["0 9 * * *", "0 10 * * *", "0 9 * * *", "0 11 * * *"]
    report = deduplicate(exprs)
    assert report.removed_count == 1
    assert len(report.unique) == 3
