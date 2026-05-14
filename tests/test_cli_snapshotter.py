"""Tests for cronlens.cli_snapshotter."""

import json
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from cronlens.cli_snapshotter import format_diff, cmd_snapshot_save, cmd_snapshot_diff
from cronlens.snapshotter import CronSnapshot, SnapshotDiff, save_snapshot


class FakeArgs:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def make_snapshot(tmp_path, name, exprs, fname):
    """Helper to create and persist a CronSnapshot for use in tests."""
    snap = CronSnapshot(
        name=name,
        expressions=exprs,
        captured_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    path = str(tmp_path / fname)
    save_snapshot(snap, path)
    return path


def test_format_diff_no_changes():
    diff = SnapshotDiff(added=[], removed=[], unchanged=["* * * * *"])
    output = format_diff(diff)
    assert "No changes" in output


def test_format_diff_shows_added():
    diff = SnapshotDiff(added=["0 9 * * 1"], removed=[], unchanged=[])
    output = format_diff(diff)
    assert "+ 0 9 * * 1" in output


def test_format_diff_shows_removed():
    diff = SnapshotDiff(added=[], removed=["0 0 * * *"], unchanged=[])
    output = format_diff(diff)
    assert "- 0 0 * * *" in output


def test_cmd_snapshot_save_creates_file(tmp_path, capsys):
    out = str(tmp_path / "snap.json")
    args = FakeArgs(name="ci", expressions=["* * * * *", "0 9 * * 1"], output=out, note=None)
    cmd_snapshot_save(args)
    captured = capsys.readouterr()
    assert "ci" in captured.out
    assert "2 expression" in captured.out
    with open(out) as f:
        data = json.load(f)
    assert data["name"] == "ci"
    assert len(data["expressions"]) == 2


def test_cmd_snapshot_diff_prints_summary(tmp_path, capsys):
    before_path = make_snapshot(tmp_path, "v1", ["* * * * *"], "before.json")
    after_path = make_snapshot(tmp_path, "v2", ["* * * * *", "0 9 * * 1"], "after.json")
    args = FakeArgs(before=before_path, after=after_path)
    cmd_snapshot_diff(args)
    captured = capsys.readouterr()
    assert "v1" in captured.out
    assert "v2" in captured.out
    assert "+1 added" in captured.out


def test_cmd_snapshot_diff_no_changes(tmp_path, capsys):
    """Diffing identical snapshots should report no changes."""
    before_path = make_snapshot(tmp_path, "v1", ["* * * * *"], "before.json")
    after_path = make_snapshot(tmp_path, "v1", ["* * * * *"], "after.json")
    args = FakeArgs(before=before_path, after=after_path)
    cmd_snapshot_diff(args)
    captured = capsys.readouterr()
    assert "No changes" in captured.out


def test_cmd_snapshot_diff_missing_file_exits(tmp_path):
    args = FakeArgs(before="/no/such/before.json", after="/no/such/after.json")
    with pytest.raises(SystemExit):
        cmd_snapshot_diff(args)
