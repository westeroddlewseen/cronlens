"""Deduplicator: identify and remove duplicate or equivalent cron expressions."""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from cronlens.parser import CronExpression


@dataclass
class DeduplicationReport:
    """Result of deduplicating a list of cron expressions."""
    unique: List[str]
    duplicates: Dict[str, List[str]]  # canonical -> list of equivalent raw strings
    removed_count: int

    @property
    def has_duplicates(self) -> bool:
        return self.removed_count > 0

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicates found."
        lines = [f"{self.removed_count} duplicate(s) removed:"]
        for canonical, dupes in self.duplicates.items():
            lines.append(f"  '{canonical}' duplicated by: {dupes}")
        return "\n".join(lines)


def _normalize(expr: CronExpression) -> Tuple:
    """Return a hashable tuple representing the resolved schedule."""
    return (
        tuple(sorted(expr.minutes)),
        tuple(sorted(expr.hours)),
        tuple(sorted(expr.days)),
        tuple(sorted(expr.months)),
        tuple(sorted(expr.weekdays)),
    )


def _canonical_string(expr: CronExpression) -> str:
    """Return a normalized canonical string for the expression."""
    def fmt(values, max_val):
        s = sorted(values)
        if s == list(range(min(s), max_val + 1)) and min(s) == 0:
            return "*"
        return ",".join(str(v) for v in s)

    return " ".join([
        fmt(expr.minutes, 59),
        fmt(expr.hours, 23),
        fmt(expr.days, 31),
        fmt(expr.months, 12),
        fmt(expr.weekdays, 6),
    ])


def deduplicate(expressions: List[str]) -> DeduplicationReport:
    """Deduplicate a list of cron expression strings.

    Two expressions are considered duplicates if they resolve to the
    same set of minutes, hours, days, months, and weekdays.
    """
    seen: Dict[Tuple, str] = {}  # normalized tuple -> first canonical string
    unique: List[str] = []
    duplicates: Dict[str, List[str]] = {}
    removed = 0

    for raw in expressions:
        try:
            parsed = CronExpression(raw)
        except Exception:
            # Keep unparseable expressions as-is
            unique.append(raw)
            continue

        key = _normalize(parsed)
        canonical = _canonical_string(parsed)

        if key not in seen:
            seen[key] = canonical
            unique.append(raw)
        else:
            existing = seen[key]
            duplicates.setdefault(existing, [])
            duplicates[existing].append(raw)
            removed += 1

    return DeduplicationReport(
        unique=unique,
        duplicates=duplicates,
        removed_count=removed,
    )
