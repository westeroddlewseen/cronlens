"""Next-run prediction engine for cron expressions."""

from datetime import datetime, timedelta
from typing import Iterator, List

from cronlens.parser import CronExpression


class CronScheduler:
    """Predicts upcoming run times for a given cron expression."""

    def __init__(self, expression: CronExpression):
        self.expression = expression

    def _matches(self, dt: datetime) -> bool:
        """Check if a datetime matches the cron expression."""
        fields = self.expression.fields
        return (
            dt.minute in fields["minute"]
            and dt.hour in fields["hour"]
            and dt.day in fields["day"]
            and dt.month in fields["month"]
            and dt.weekday() in [w % 7 for w in fields["weekday"]]
        )

    def next_runs(self, after: datetime = None, count: int = 5) -> List[datetime]:
        """Return the next `count` run times after the given datetime."""
        if after is None:
            after = datetime.now()

        results = []
        current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

        # Guard against infinite loops: search up to 4 years ahead
        limit = current + timedelta(days=4 * 365)

        while len(results) < count and current < limit:
            if self._matches(current):
                results.append(current)
            current += timedelta(minutes=1)

        return results

    def next_run(self, after: datetime = None) -> datetime | None:
        """Return the single next run time."""
        runs = self.next_runs(after=after, count=1)
        return runs[0] if runs else None

    def iter_runs(self, after: datetime = None) -> Iterator[datetime]:
        """Lazily yield run times indefinitely."""
        if after is None:
            after = datetime.now()

        current = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

        while True:
            if self._matches(current):
                yield current
            current += timedelta(minutes=1)
