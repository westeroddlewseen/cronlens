"""CLI entry point for cronlens."""

import argparse
import sys
from datetime import datetime

from cronlens.parser import CronExpression
from cronlens.scheduler import CronScheduler
from cronlens.humanizer import humanize
from cronlens.explainer import explain
from cronlens.formatter import format_explanation, format_next_runs, format_full_report
from cronlens.validator import validate
from cronlens.visualizer import format_schedule_table, format_minute_heatmap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronlens",
        description="Human-readable cron expression parser and schedule visualizer.",
    )
    parser.add_argument("expression", help="Cron expression (5 fields, quoted)")
    parser.add_argument(
        "--next", type=int, default=5, metavar="N",
        help="Show next N scheduled runs (default: 5)"
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="Validate the expression and exit"
    )
    parser.add_argument(
        "--explain", action="store_true",
        help="Show detailed field-by-field explanation"
    )
    parser.add_argument(
        "--heatmap", action="store_true",
        help="Show minute heatmap for the current hour"
    )
    parser.add_argument(
        "--table", action="store_true",
        help="Show upcoming schedule as a table"
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Show full report (explanation + next runs)"
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Always validate first
    result = validate(args.expression)
    if not result:
        print(result.summary(), file=sys.stderr)
        return 1

    if args.validate:
        print(result.summary())
        return 0

    expr = CronExpression.parse(args.expression)
    scheduler = CronScheduler(expr)
    now = datetime.now()

    if args.full:
        print(format_full_report(expr, scheduler, now, count=args.next))
        return 0

    if args.explain:
        exp = explain(expr)
        print(format_explanation(exp))

    if args.table:
        runs = scheduler.next_runs(now, count=args.next)
        print(format_schedule_table(runs))
    elif args.heatmap:
        print(format_minute_heatmap(expr))
    elif not args.explain:
        # Default: human summary + next runs
        print(f"Schedule: {humanize(expr)}")
        runs = scheduler.next_runs(now, count=args.next)
        print(format_next_runs(runs))

    return 0


if __name__ == "__main__":
    sys.exit(main())
