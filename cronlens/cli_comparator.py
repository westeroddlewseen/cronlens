"""CLI integration for the cron comparator feature."""

import argparse
import sys

from cronlens.parser import CronExpression
from cronlens.aliases import resolve_alias
from cronlens.comparator import compare, format_comparison


def cmd_compare(args: argparse.Namespace) -> None:
    """Handle the 'compare' subcommand."""
    raw_a = resolve_alias(args.expr_a)
    raw_b = resolve_alias(args.expr_b)

    try:
        expr_a = CronExpression.parse(raw_a)
    except Exception as exc:
        print(f"Error parsing first expression '{args.expr_a}': {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        expr_b = CronExpression.parse(raw_b)
    except Exception as exc:
        print(f"Error parsing second expression '{args.expr_b}': {exc}", file=sys.stderr)
        sys.exit(1)

    report = compare(expr_a, expr_b)
    print(format_comparison(report))


def register_subcommand(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the 'compare' subcommand on an existing subparsers object."""
    parser = subparsers.add_parser(
        "compare",
        help="Compare two cron expressions side-by-side",
    )
    parser.add_argument(
        "expr_a",
        metavar="EXPR_A",
        help="First cron expression (or alias)",
    )
    parser.add_argument(
        "expr_b",
        metavar="EXPR_B",
        help="Second cron expression (or alias)",
    )
    parser.set_defaults(func=cmd_compare)


def build_compare_parser() -> argparse.ArgumentParser:
    """Standalone argument parser for the compare command (used in tests)."""
    p = argparse.ArgumentParser(prog="cronlens compare")
    p.add_argument("expr_a", metavar="EXPR_A")
    p.add_argument("expr_b", metavar="EXPR_B")
    p.set_defaults(func=cmd_compare)
    return p
