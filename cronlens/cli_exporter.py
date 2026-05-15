"""CLI interface for exporting cron expressions."""

from __future__ import annotations

import argparse
import sys

from cronlens.parser import CronExpression
from cronlens.aliases import resolve_alias
from cronlens.exporter import export_json, export_csv, export_markdown


def _parse_expressions(raw: list[str]) -> list[CronExpression]:
    results = []
    for r in raw:
        resolved = resolve_alias(r)
        try:
            results.append(CronExpression.parse(resolved))
        except Exception as exc:
            print(f"[warn] Skipping invalid expression '{r}': {exc}", file=sys.stderr)
    return results


def cmd_export(args: argparse.Namespace) -> None:
    expressions = _parse_expressions(args.expressions)
    if not expressions:
        print("No valid expressions to export.", file=sys.stderr)
        sys.exit(1)

    fmt = args.format.lower()
    count = args.count

    if fmt == "json":
        output = export_json(expressions, count)
    elif fmt == "csv":
        output = export_csv(expressions, count)
    elif fmt == "markdown":
        output = export_markdown(expressions, count)
    else:
        print(f"Unknown format: {fmt}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(output)
        print(f"Exported {len(expressions)} expression(s) to {args.output}")
    else:
        print(output)


def build_export_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("export", help="Export cron expressions to JSON, CSV or Markdown")
    p.add_argument("expressions", nargs="+", help="Cron expressions or aliases")
    p.add_argument("-f", "--format", default="json", choices=["json", "csv", "markdown"],
                   help="Output format (default: json)")
    p.add_argument("-n", "--count", type=int, default=3,
                   help="Number of next runs to include (default: 3)")
    p.add_argument("-o", "--output", default=None, help="Write output to file instead of stdout")
    p.set_defaults(func=cmd_export)
