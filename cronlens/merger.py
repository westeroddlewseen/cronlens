"""Merge multiple cron expressions into a unified schedule description."""

from dataclasses import dataclass, field
from typing import List, Dict, Set
from cronlens.parser import CronExpression


@dataclass
class MergeResult:
    """Result of merging multiple cron expressions."""

    expressions: List[CronExpression]
    common_fields: Dict[str, Set[int]] = field(default_factory=dict)
    union_fields: Dict[str, Set[int]] = field(default_factory=dict)
    all_identical: bool = False

    def common_minutes(self) -> Set[int]:
        return self.common_fields.get("minute", set())

    def common_hours(self) -> Set[int]:
        return self.common_fields.get("hour", set())

    def union_minutes(self) -> Set[int]:
        return self.union_fields.get("minute", set())

    def union_hours(self) -> Set[int]:
        return self.union_fields.get("hour", set())


FIELD_NAMES = ["minute", "hour", "day", "month", "weekday"]


def _get_field_values(expr: CronExpression) -> Dict[str, Set[int]]:
    return {
        "minute": set(expr.minutes),
        "hour": set(expr.hours),
        "day": set(expr.days),
        "month": set(expr.months),
        "weekday": set(expr.weekdays),
    }


def merge_expressions(expressions: List[CronExpression]) -> MergeResult:
    """Compute intersection and union of multiple cron expressions."""
    if not expressions:
        raise ValueError("At least one expression is required")

    field_sets = [_get_field_values(e) for e in expressions]

    common: Dict[str, Set[int]] = {}
    union: Dict[str, Set[int]] = {}

    for name in FIELD_NAMES:
        values = [fs[name] for fs in field_sets]
        common[name] = set.intersection(*values)
        union[name] = set.union(*values)

    all_identical = all(
        field_sets[0][name] == field_sets[i][name]
        for i in range(1, len(field_sets))
        for name in FIELD_NAMES
    )

    return MergeResult(
        expressions=expressions,
        common_fields=common,
        union_fields=union,
        all_identical=all_identical,
    )


def format_merge_report(result: MergeResult) -> str:
    """Format a human-readable merge report."""
    lines = [f"Merged {len(result.expressions)} expression(s)"]

    if result.all_identical:
        lines.append("  All expressions are identical.")
        return "\n".join(lines)

    lines.append("")
    lines.append("  Common values (intersection):")
    for name in FIELD_NAMES:
        vals = sorted(result.common_fields.get(name, set()))
        lines.append(f"    {name:8s}: {vals if vals else '(none)'}")

    lines.append("")
    lines.append("  All values (union):")
    for name in FIELD_NAMES:
        vals = sorted(result.union_fields.get(name, set()))
        lines.append(f"    {name:8s}: {vals}")

    return "\n".join(lines)
