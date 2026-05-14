"""Snapshot and diff cron expression sets over time."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class CronSnapshot:
    """A named snapshot of a set of cron expressions."""

    name: str
    expressions: List[str]
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "expressions": self.expressions,
            "captured_at": self.captured_at.isoformat(),
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CronSnapshot":
        return cls(
            name=data["name"],
            expressions=data["expressions"],
            captured_at=datetime.fromisoformat(data["captured_at"]),
            note=data.get("note"),
        )


@dataclass
class SnapshotDiff:
    """Difference between two snapshots."""

    added: List[str]
    removed: List[str]
    unchanged: List[str]

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if not parts:
            return "No changes"
        return ", ".join(parts)


def diff_snapshots(before: CronSnapshot, after: CronSnapshot) -> SnapshotDiff:
    """Compute the diff between two snapshots."""
    before_set = set(before.expressions)
    after_set = set(after.expressions)
    return SnapshotDiff(
        added=sorted(after_set - before_set),
        removed=sorted(before_set - after_set),
        unchanged=sorted(before_set & after_set),
    )


def save_snapshot(snapshot: CronSnapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    with open(path, "w") as f:
        json.dump(snapshot.to_dict(), f, indent=2)


def load_snapshot(path: str) -> CronSnapshot:
    """Load a snapshot from a JSON file."""
    with open(path) as f:
        data = json.load(f)
    return CronSnapshot.from_dict(data)
