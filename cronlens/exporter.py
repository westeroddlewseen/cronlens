"""Export cron expressions and their metadata to various formats."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

from cronlens.parser import CronExpression
from cronlens.humanizer import humanize
from cronlens.tagger import tag, TagResult
from cronlens.scheduler import CronScheduler


@dataclass
class ExportRecord:
    expression: str
    human: str
    tags: list[str]
    next_runs: list[str]
    fields: dict[str, list[int]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _build_record(expr: CronExpression, count: int = 3) -> ExportRecord:
    scheduler = CronScheduler(expr)
    runs = [dt.isoformat() for dt in scheduler.next_runs(count)]
    tags_result: TagResult = tag(expr)
    return ExportRecord(
        expression=str(expr),
        human=humanize(expr),
        tags=list(tags_result.tags),
        next_runs=runs,
        fields={
            "minutes": sorted(expr.minutes),
            "hours": sorted(expr.hours),
            "days_of_month": sorted(expr.days_of_month),
            "months": sorted(expr.months),
            "days_of_week": sorted(expr.days_of_week),
        },
    )


def export_json(expressions: list[CronExpression], count: int = 3) -> str:
    records = [_build_record(e, count).to_dict() for e in expressions]
    return json.dumps(records, indent=2)


def export_csv(expressions: list[CronExpression], count: int = 3) -> str:
    header = "expression,human,tags,next_run_1,next_run_2,next_run_3"
    rows = [header]
    for expr in expressions:
        rec = _build_record(expr, count)
        tags_str = "|".join(rec.tags)
        runs = rec.next_runs + [""] * (3 - len(rec.next_runs))
        rows.append(f"{rec.expression},{rec.human},{tags_str},{runs[0]},{runs[1]},{runs[2]}")
    return "\n".join(rows)


def export_markdown(expressions: list[CronExpression], count: int = 3) -> str:
    lines = [
        "| Expression | Human | Tags | Next Run |",
        "| --- | --- | --- | --- |",
    ]
    for expr in expressions:
        rec = _build_record(expr, count)
        tags_str = ", ".join(rec.tags) if rec.tags else "—"
        next_run = rec.next_runs[0] if rec.next_runs else "—"
        lines.append(f"| `{rec.expression}` | {rec.human} | {tags_str} | {next_run} |")
    return "\n".join(lines)
