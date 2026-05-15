"""Standalone entry point for the export subcommand."""

from __future__ import annotations

import argparse
import sys

from cronlens.cli_exporter import build_export_parser, cmd_export


def build_standalone_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cronlens-export",
        description="Export cron expressions to JSON, CSV, or Markdown.",
    )
    subparsers = parser.add_subparsers(dest="command")
    build_export_parser(subparsers)
    return parser


def run_export_command(args: argparse.Namespace) -> None:
    if not hasattr(args, "func"):
        build_standalone_parser().print_help()
        sys.exit(0)
    args.func(args)


def register_export_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register export subcommand into an existing subparsers group."""
    build_export_parser(subparsers)


def main(argv: list[str] | None = None) -> None:
    parser = build_standalone_parser()
    # Make 'export' the default command when running standalone
    raw = argv if argv is not None else sys.argv[1:]
    if raw and raw[0] != "export":
        raw = ["export"] + raw
    args = parser.parse_args(raw)
    run_export_command(args)


if __name__ == "__main__":
    main()
