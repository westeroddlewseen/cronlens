"""Command-line interface for cronlens."""

import argparse
from datetime import datetime

from cronlens.formatter import format_full_report
from cronlens.visualizer import format_schedule_table, format_minute_heatmap
from cronlens.parser import CronExpression


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronlens",
        description="Human-readable cron expression parser and schedule visualizer",
    )
    p.add_argument("expression", help="Cron expression (quoted), e.g. '*/5 9-17 * * 1-5'")
    p.add_argument(
        "--from",
        dest="from_dt",
        metavar="DATETIME",
        default=None,
        help="Start datetime ISO format YYYY-MM-DDTHH:MM (default: now)",
    )
    p.add_argument(
        "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of next runs to display (default: 5)",
    )
    p.add_argument(
        "--heatmap",
        action="store_true",
        help="Show minute-of-day heatmap",
    )
    p.add_argument(
        "--table",
        action="store_true",
        help="Show 24-hour schedule table",
    )
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    from_dt = datetime.now().replace(second=0, microsecond=0)
    if args.from_dt:
        from_dt = datetime.fromisoformat(args.from_dt)

    try:
        expr = CronExpression(args.expression)
    except ValueError as e:
        parser.error(str(e))
        return

    print(format_full_report(args.expression, from_dt, args.count))

    if args.table:
        print("\nSchedule Table:")
        print(format_schedule_table(expr))

    if args.heatmap:
        print("\nMinute Heatmap:")
        print(format_minute_heatmap(expr))


if __name__ == "__main__":
    main()
