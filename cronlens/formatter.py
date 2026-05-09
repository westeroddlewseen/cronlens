"""Format cronlens output structures for terminal display."""

from datetime import datetime, timezone
from typing import List

from cronlens.explainer import explain
from cronlens.parser import CronExpression
from cronlens.ranker import CronRank, rank


def format_explanation(expr: CronExpression) -> str:
    """Return a formatted multi-line explanation of a cron expression."""
    data = explain(expr)
    lines = [
        f"Expression : {expr.expression}",
        f"Summary    : {data['summary']}",
        "",
        "Fields:",
    ]
    for field, desc in data["fields"].items():
        lines.append(f"  {field:<14} {desc}")
    return "\n".join(lines)


def format_next_runs(expr: CronExpression, n: int = 5, from_dt: datetime | None = None) -> str:
    """Return a formatted list of upcoming run times with human-readable deltas."""
    from cronlens.scheduler import CronScheduler

    now = from_dt or datetime.now(timezone.utc)
    scheduler = CronScheduler(expr)
    runs = scheduler.next_runs(n, from_dt=now)

    lines = [f"Next {n} runs (from {now.strftime('%Y-%m-%d %H:%M UTC')}):", ""]
    for i, dt in enumerate(runs, 1):
        delta = dt - now
        total_seconds = int(delta.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        delta_str = f"+{hours}h {minutes:02d}m" if hours else f"+{minutes}m"
        lines.append(f"  {i}. {dt.strftime('%Y-%m-%d %H:%M UTC')}  ({delta_str})")
    return "\n".join(lines)


def format_rank(expr: CronExpression) -> str:
    """Return a formatted rank summary for a cron expression."""
    r: CronRank = rank(expr)
    lines = [
        f"Rank Summary for: {r.expression}",
        f"  Label       : {r.label}",
        f"  Frequency   : {r.frequency_score:.2f} runs/day",
        f"  Regularity  : {r.regularity_score:.2%}",
        f"  Complexity  : {r.complexity_score:.2%}",
        f"  Overall     : {r.overall_score:.4f}",
    ]
    return "\n".join(lines)


def format_full_report(expr: CronExpression, n: int = 5, from_dt: datetime | None = None) -> str:
    """Return a complete report combining explanation, rank, and next runs."""
    separator = "-" * 48
    sections = [
        format_explanation(expr),
        separator,
        format_rank(expr),
        separator,
        format_next_runs(expr, n=n, from_dt=from_dt),
    ]
    return "\n".join(sections)
