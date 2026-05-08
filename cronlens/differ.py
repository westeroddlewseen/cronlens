"""Compare two cron expressions and describe their differences."""

from dataclasses import dataclass
from typing import List, Optional

from cronlens.parser import CronExpression
from cronlens.scheduler import CronScheduler


@dataclass
class FieldDiff:
    field: str
    values_a: List[int]
    values_b: List[int]

    @property
    def changed(self) -> bool:
        return self.values_a != self.values_b

    @property
    def added(self) -> List[int]:
        return sorted(set(self.values_b) - set(self.values_a))

    @property
    def removed(self) -> List[int]:
        return sorted(set(self.values_a) - set(self.values_b))


@dataclass
class CronDiff:
    expr_a: str
    expr_b: str
    field_diffs: List[FieldDiff]

    @property
    def has_changes(self) -> bool:
        return any(d.changed for d in self.field_diffs)

    @property
    def changed_fields(self) -> List[FieldDiff]:
        return [d for d in self.field_diffs if d.changed]


FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


def diff_expressions(expr_a: str, expr_b: str) -> CronDiff:
    """Compare two cron expression strings and return a structured diff."""
    parsed_a = CronExpression(expr_a)
    parsed_b = CronExpression(expr_b)

    fields_a = [
        parsed_a.minute,
        parsed_a.hour,
        parsed_a.day_of_month,
        parsed_a.month,
        parsed_a.day_of_week,
    ]
    fields_b = [
        parsed_b.minute,
        parsed_b.hour,
        parsed_b.day_of_month,
        parsed_b.month,
        parsed_b.day_of_week,
    ]

    diffs = [
        FieldDiff(name, list(fa.values), list(fb.values))
        for name, fa, fb in zip(FIELD_NAMES, fields_a, fields_b)
    ]

    return CronDiff(expr_a=expr_a, expr_b=expr_b, field_diffs=diffs)


def format_diff(diff: CronDiff) -> str:
    """Return a human-readable string describing the diff."""
    if not diff.has_changes:
        return f"No differences between '{diff.expr_a}' and '{diff.expr_b}'."

    lines = [f"Differences between '{diff.expr_a}' and '{diff.expr_b}':\n"]
    for fd in diff.changed_fields:
        lines.append(f"  {fd.field}:")
        if fd.removed:
            lines.append(f"    - removed: {fd.removed}")
        if fd.added:
            lines.append(f"    + added:   {fd.added}")
    return "\n".join(lines)
