"""Tests for cronlens.snapshotter."""

from datetime import datetime, timezone

import pytest

from cronlens.snapshotter import (
    CronSnapshot,
    SnapshotDiff,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
)


def make_snapshot(name, exprs, note=None):
    return CronSnapshot(
        name=name,
        expressions=exprs,
        captured_at=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        note=note,
    )


def test_snapshot_to_dict_round_trip():
    snap = make_snapshot("prod", ["* * * * *", "0 9 * * 1"])
    d = snap.to_dict()
    restored = CronSnapshot.from_dict(d)
    assert restored.name == "prod"
    assert restored.expressions == ["* * * * *", "0 9 * * 1"]
    assert restored.note is None


def test_snapshot_with_note():
    snap = make_snapshot("staging", ["0 0 * * *"], note="nightly job")
    d = snap.to_dict()
    assert d["note"] == "nightly job"
    restored = CronSnapshot.from_dict(d)
    assert restored.note == "nightly job"


def test_diff_added_expressions():
    before = make_snapshot("v1", ["* * * * *"])
    after = make_snapshot("v2", ["* * * * *", "0 9 * * 1"])
    diff = diff_snapshots(before, after)
    assert "0 9 * * 1" in diff.added
    assert diff.removed == []
    assert "* * * * *" in diff.unchanged


def test_diff_removed_expressions():
    before = make_snapshot("v1", ["* * * * *", "0 0 * * *"])
    after = make_snapshot("v2", ["* * * * *"])
    diff = diff_snapshots(before, after)
    assert "0 0 * * *" in diff.removed
    assert diff.added == []


def test_diff_no_changes():
    before = make_snapshot("v1", ["* * * * *"])
    after = make_snapshot("v2", ["* * * * *"])
    diff = diff_snapshots(before, after)
    assert not diff.has_changes
    assert diff.summary() == "No changes"


def test_diff_has_changes_flag():
    before = make_snapshot("v1", ["* * * * *"])
    after = make_snapshot("v2", ["0 0 * * *"])
    diff = diff_snapshots(before, after)
    assert diff.has_changes


def test_diff_summary_format():
    diff = SnapshotDiff(added=["a", "b"], removed=["c"], unchanged=[])
    assert "+2 added" in diff.summary()
    assert "-1 removed" in diff.summary()


def test_save_and_load_snapshot(tmp_path):
    snap = make_snapshot("test", ["*/5 * * * *"])
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded.name == "test"
    assert loaded.expressions == ["*/5 * * * *"]


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_snapshot(str(tmp_path / "missing.json"))
