"""Standalone entry-point and integration helpers for the annotator CLI."""

import argparse
import sys
from typing import List, Optional

from cronlens.cli_annotator import build_annotate_parser, cmd_annotate


def build_standalone_parser() -> argparse.ArgumentParser:
    """Build a standalone argument parser for the annotate command."""
    parser = argparse.ArgumentParser(
        prog="cronlens-annotate",
        description="Annotate cron expressions with notes and labels",
    )
    build_annotate_parser.__doc__  # noqa — ensure import is used
    # Re-use the same argument definitions via delegation
    parser.add_argument("expression", help="Cron expression to annotate (quote it)")
    parser.add_argument("--note", default=None, help="Human-readable note")
    parser.add_argument(
        "--label",
        dest="labels",
        action="append",
        metavar="LABEL",
        help="Attach a label (repeatable)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON alongside text")
    return parser


def register_annotate_commands(subparsers) -> None:
    """Register the 'annotate' subcommand onto an existing subparsers group."""
    build_annotate_parser(subparsers)


def run_annotate_command(argv: Optional[List[str]] = None) -> int:
    """Parse argv and run the annotate command. Returns exit code."""
    parser = build_standalone_parser()
    args = parser.parse_args(argv)
    try:
        cmd_annotate(args)
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 1


def main() -> None:  # pragma: no cover
    sys.exit(run_annotate_command())


if __name__ == "__main__":  # pragma: no cover
    main()
