"""Track and summarize historical cron execution times."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from cronlens.scheduler import CronScheduler


@dataclass
class ExecutionWindow:
    """Represents a time window with expected execution count."""

    start: datetime
    end: datetime
    expected: int

    @property
    def duration_hours(self) -> float:
        delta = self.end - self.start
        return delta.total_seconds() / 3600


@dataclass
class HistorySummary:
    """Summary of cron executions over a historical period."""

    expression: str
    window: ExecutionWindow
    run_times: List[datetime] = field(default_factory=list)

    @property
    def actual_count(self) -> int:
        return len(self.run_times)

    @property
    def expected_count(self) -> int:
        return self.window.expected

    @property
    def first_run(self) -> Optional[datetime]:
        return self.run_times[0] if self.run_times else None

    @property
    def last_run(self) -> Optional[datetime]:
        return self.run_times[-1] if self.run_times else None

    def coverage_percent(self) -> float:
        if self.expected_count == 0:
            return 0.0
        return min(100.0, self.actual_count / self.expected_count * 100)


def build_history(
    expression: str,
    start: datetime,
    end: datetime,
    count_limit: int = 1000,
) -> HistorySummary:
    """Generate a HistorySummary for a cron expression over a time window.

    Args:
        expression: A valid cron expression string.
        start: Start of the historical window (inclusive).
        end: End of the historical window (exclusive).
        count_limit: Maximum number of runs to collect.

    Returns:
        A HistorySummary with all scheduled runs in the window.
    """
    scheduler = CronScheduler(expression)
    runs: List[datetime] = []
    current = start

    for _ in range(count_limit):
        nxt = scheduler.next_run(current)
        if nxt is None or nxt >= end:
            break
        runs.append(nxt)
        # Advance by one minute to avoid re-matching same slot
        from datetime import timedelta
        current = nxt + timedelta(minutes=1)

    window = ExecutionWindow(start=start, end=end, expected=len(runs))
    return HistorySummary(expression=expression, window=window, run_times=runs)
