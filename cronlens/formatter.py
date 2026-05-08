"""Formats cron schedule information for CLI output."""

from datetime import datetime
from cronlens.parser import CronExpression
from cronlens.explainer import explain
from cronlens.humanizer import humanize
from cronlens.scheduler import CronScheduler


def format_explanation(expr: CronExpression) -> str:
    """Format a detailed multi-line explanation of a cron expression."""
    details = explain(expr)
    lines = [
        f"  Minute       : {details['minute']}",
        f"  Hour         : {details['hour']}",
        f"  Day of Month : {details['day_of_month']}",
        f"  Month        : {details['month']}",
        f"  Day of Week  : {details['day_of_week']}",
        "",
        f"  Summary      : {details['summary']}",
    ]
    return "\n".join(lines)


def format_next_runs(expr: CronExpression, from_dt: datetime, count: int = 5) -> str:
    """Format the next N scheduled run times as a numbered list."""
    scheduler = CronScheduler(expr)
    runs = scheduler.next_runs(from_dt, count)
    lines = [f"  Next {count} runs from {from_dt.strftime('%Y-%m-%d %H:%M')}:"]
    for i, run in enumerate(runs, 1):
        delta = run - from_dt
        total_minutes = int(delta.total_seconds() // 60)
        if total_minutes < 60:
            delta_str = f"in {total_minutes}m"
        elif total_minutes < 1440:
            delta_str = f"in {total_minutes // 60}h {total_minutes % 60}m"
        else:
            delta_str = f"in {delta.days}d {(total_minutes % 1440) // 60}h"
        lines.append(f"  {i:>2}. {run.strftime('%Y-%m-%d %H:%M')}  ({delta_str})")
    return "\n".join(lines)


def format_full_report(raw: str, from_dt: datetime, count: int = 5) -> str:
    """Generate a full formatted report for a cron expression string."""
    expr = CronExpression(raw)
    sections = [
        f"Cron Expression : {raw}",
        f"Human Readable  : {humanize(expr)}",
        "",
        "Field Breakdown:",
        format_explanation(expr),
        "",
        format_next_runs(expr, from_dt, count),
    ]
    return "\n".join(sections)
