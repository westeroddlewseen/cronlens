"""Cron expression profiler: detects patterns, anomalies, and runtime characteristics."""

from dataclasses import dataclass, field
from typing import List, Optional
from cronlens.parser import CronExpression
from cronlens.ranker import CronRank


@dataclass
class ProfileResult:
    expression: str
    frequency_per_day: float
    is_high_frequency: bool
    is_business_hours: bool
    is_overnight: bool
    is_weekend_only: bool
    is_weekday_only: bool
    has_specific_dom: bool
    has_specific_dow: bool
    dom_dow_conflict: bool
    anomalies: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.anomalies) == 0

    def summary(self) -> str:
        lines = [f"Expression : {self.expression}"]
        lines.append(f"Runs/day   : {self.frequency_per_day:.1f}")
        flags = []
        if self.is_high_frequency:
            flags.append("high-frequency")
        if self.is_business_hours:
            flags.append("business-hours")
        if self.is_overnight:
            flags.append("overnight")
        if self.is_weekend_only:
            flags.append("weekend-only")
        if self.is_weekday_only:
            flags.append("weekday-only")
        if flags:
            lines.append("Flags      : " + ", ".join(flags))
        if self.anomalies:
            lines.append("Anomalies  :")
            for a in self.anomalies:
                lines.append(f"  ! {a}")
        if self.notes:
            lines.append("Notes      :")
            for n in self.notes:
                lines.append(f"  - {n}")
        return "\n".join(lines)


def profile(expr: CronExpression) -> ProfileResult:
    rank = CronRank(expr)
    freq = rank._frequency_per_day()

    hours = expr.hours
    minutes = expr.minutes
    dow = expr.days_of_week
    dom = expr.days_of_month

    business_hours = set(range(9, 18))
    overnight_hours = set(range(0, 6))
    weekdays = set(range(1, 6))
    weekend = {0, 6}

    is_biz = bool(set(hours) & business_hours) and not (set(hours) - business_hours)
    is_overnight = bool(set(hours) & overnight_hours) and not (set(hours) - overnight_hours)
    is_weekend = set(dow) == weekend
    is_weekday = set(dow) == weekdays

    has_specific_dom = set(dom) != set(range(1, 32))
    has_specific_dow = set(dow) != set(range(0, 7))
    dom_dow_conflict = has_specific_dom and has_specific_dow

    anomalies = []
    notes = []

    if freq > 1440:
        anomalies.append("Frequency exceeds maximum possible (1440/day)")
    if freq >= 60:
        notes.append("Runs at least once per minute — consider if this is intentional")
    if dom_dow_conflict:
        anomalies.append("Both day-of-month and day-of-week are restricted; behavior is OR-based (may surprise)")
    if 0 in minutes and len(minutes) == 1 and len(hours) == 24:
        notes.append("Runs exactly once per hour on the hour")
    if freq == 0:
        anomalies.append("Expression resolves to zero scheduled runs")

    return ProfileResult(
        expression=str(expr),
        frequency_per_day=freq,
        is_high_frequency=freq >= 60,
        is_business_hours=is_biz,
        is_overnight=is_overnight,
        is_weekend_only=is_weekend,
        is_weekday_only=is_weekday,
        has_specific_dom=has_specific_dom,
        has_specific_dow=has_specific_dow,
        dom_dow_conflict=dom_dow_conflict,
        anomalies=anomalies,
        notes=notes,
    )
