"""Group multiple cron expressions by shared schedule characteristics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from cronlens.parser import CronExpression
from cronlens.tagger import tag, TagResult


@dataclass
class ExpressionGroup:
    """A named group of cron expressions sharing a common characteristic."""

    label: str
    expressions: List[str] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.expressions)

    def __repr__(self) -> str:  # pragma: no cover
        return f"ExpressionGroup(label={self.label!r}, count={len(self)})"


@dataclass
class GroupReport:
    """Result of grouping a collection of cron expressions."""

    groups: Dict[str, ExpressionGroup]
    ungrouped: List[str] = field(default_factory=list)

    @property
    def group_names(self) -> List[str]:
        return list(self.groups.keys())

    def get(self, label: str) -> ExpressionGroup:
        return self.groups.get(label, ExpressionGroup(label=label))


_TAG_PRIORITY = ["frequent", "hourly", "daily", "weekly", "monthly", "restricted"]


def _primary_label(tags: TagResult) -> str:
    """Return the highest-priority tag label for an expression."""
    for label in _TAG_PRIORITY:
        if tags.has(label):
            return label
    return "other"


def group_expressions(expressions: List[str]) -> GroupReport:
    """Group cron expressions by their primary schedule characteristic.

    Args:
        expressions: List of cron expression strings.

    Returns:
        A GroupReport mapping labels to ExpressionGroup instances.
    """
    groups: Dict[str, ExpressionGroup] = {}
    ungrouped: List[str] = []

    for expr in expressions:
        try:
            parsed = CronExpression.parse(expr)
        except Exception:
            ungrouped.append(expr)
            continue

        tags = tag(parsed)
        label = _primary_label(tags)

        if label not in groups:
            groups[label] = ExpressionGroup(label=label)
        groups[label].expressions.append(expr)

    return GroupReport(groups=groups, ungrouped=ungrouped)
