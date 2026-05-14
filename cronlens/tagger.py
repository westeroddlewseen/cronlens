"""Tag cron expressions with descriptive category labels."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from cronlens.parser import CronExpression

KNOWN_TAGS = [
    "frequent",
    "hourly",
    "daily",
    "weekly",
    "monthly",
    "business-hours",
    "off-hours",
    "weekend",
    "weekday",
    "simple",
    "complex",
]


@dataclass
class TagResult:
    tags: List[str] = field(default_factory=list)

    def has(self, tag: str) -> bool:
        return tag in self.tags

    def __repr__(self) -> str:
        return f"TagResult(tags={self.tags})"


def tag(expr: CronExpression) -> TagResult:
    """Assign descriptive tags to a parsed cron expression."""
    tags: List[str] = []

    minutes = expr.minute
    hours = expr.hour
    dom = expr.day_of_month
    dow = expr.day_of_week

    # Frequency-based tags
    if len(minutes) == 60 and len(hours) == 24:
        tags.append("frequent")
    elif len(minutes) == 60:
        tags.append("hourly")
    elif len(hours) == 24 and len(minutes) == 1:
        tags.append("daily")
    elif len(dow) == 1 and len(hours) == 1 and len(minutes) == 1:
        tags.append("weekly")
    elif len(dom) == 1 and len(hours) == 1 and len(minutes) == 1:
        tags.append("monthly")

    # Time-of-day tags
    business = set(range(9, 18))
    if hours and set(hours).issubset(business):
        tags.append("business-hours")
    off_hours = set(range(0, 6)) | set(range(22, 24))
    if hours and set(hours).issubset(off_hours):
        tags.append("off-hours")

    # Day-of-week tags
    weekend = {0, 6}  # Sunday=0, Saturday=6
    weekdays = {1, 2, 3, 4, 5}
    if dow and set(dow).issubset(weekend):
        tags.append("weekend")
    elif dow and set(dow).issubset(weekdays):
        tags.append("weekday")

    # Complexity tags
    total_values = len(minutes) + len(hours) + len(dom) + len(dow)
    if total_values <= 4 + len(expr.month):
        tags.append("simple")
    elif total_values > 80:
        tags.append("complex")

    return TagResult(tags=tags)
