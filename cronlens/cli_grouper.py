"""CLI integration for the cron expression grouper."""

from __future__ import annotations

import argparse
from typing import List

from cronlens.grouper import group_expressions, GroupReport


def format_group_report(report: GroupReport) -> str:
    """Format a GroupReport as a human-readable string."""
    lines: List[str] = []

    if not report.groups and not report.ungrouped:
        return "No expressions provided."

    for label in sorted(report.groups):
        group = report.groups[label]
        lines.append(f"[{label.upper()}]  ({len(group)} expression(s))")
        for expr in group.expressions:
            lines.append(f"  {expr}")
        lines.append("")

    if report.ungrouped:
        lines.append(f"[INVALID]  ({len(report.ungrouped)} expression(s))")
        for expr in report.ungrouped:
            lines.append(f"  {expr}")
        lines.append("")

    return "\n".join(lines).rstrip()


def cmd_group(args: argparse.Namespace) -> None:
    """Handle the 'group' subcommand."""
    report = group_expressions(args.expressions)
    print(format_group_report(report))


def build_group_parser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'group' subcommand."""
    p = subparsers.add_parser(
        "group",
        help="Group cron expressions by schedule type (daily, hourly, etc.)",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="One or more cron expressions to group",
    )
    p.set_defaults(func=cmd_group)
