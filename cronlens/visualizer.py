"""ASCII schedule visualizer for cron expressions."""

from datetime import datetime
from typing import List

from cronlens.scheduler import CronScheduler
from cronlens.parser import CronExpression


def format_schedule_table(expression: CronExpression, count: int = 5, after: datetime = None) -> str:
    """Return a formatted table of upcoming run times."""
    scheduler = CronScheduler(expression)
    runs = scheduler.next_runs(after=after, count=count)

    if not runs:
        return "No upcoming runs found within the search window."

    header = f"{'#':<4} {'Datetime':<22} {'Relative'}"
    separator = "-" * 50
    now = after or datetime.now()

    rows = [header, separator]
    for i, run in enumerate(runs, start=1):
        delta = run - now
        total_minutes = int(delta.total_seconds() // 60)
        if total_minutes < 60:
            relative = f"in {total_minutes}m"
        elif total_minutes < 1440:
            relative = f"in {total_minutes // 60}h {total_minutes % 60}m"
        else:
            days = total_minutes // 1440
            hours = (total_minutes % 1440) // 60
            relative = f"in {days}d {hours}h"
        rows.append(f"{i:<4} {run.strftime('%Y-%m-%d %H:%M'):<22} {relative}")

    return "\n".join(rows)


def format_minute_heatmap(expression: CronExpression) -> str:
    """Return a 60-char heatmap of active minutes in an hour."""
    active = expression.fields["minute"]
    bar = "".join("#" if m in active else "." for m in range(60))
    legend = "Minutes: 0" + " " * 24 + "30" + " " * 23 + "59"
    return f"{legend}\n         {bar}"
