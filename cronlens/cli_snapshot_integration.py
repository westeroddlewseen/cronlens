"""Integration helper: register snapshot subcommands into the main CLI."""

from __future__ import annotations

import argparse
import sys

from cronlens.cli_snapshotter import build_snapshot_parser


def register_snapshot_commands(main_subparsers) -> None:
    """Attach snapshot save/diff commands to an existing subparser group."""
    build_snapshot_parser(main_subparsers)


def run_snapshot_command(args: argparse.Namespace) -> int:
    """Dispatch a parsed snapshot sub-command; returns exit code."""
    if not hasattr(args, "snapshot_cmd") or args.snapshot_cmd is None:
        print("Usage: cronlens snapshot {save,diff} ...", file=sys.stderr)
        return 1
    if not hasattr(args, "func"):
        print(f"Unknown snapshot command: {args.snapshot_cmd}", file=sys.stderr)
        return 1
    try:
        args.func(args)
        return 0
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        return 2


def build_standalone_parser() -> argparse.ArgumentParser:
    """Build a standalone argument parser for snapshot commands (useful for testing)."""
    parser = argparse.ArgumentParser(
        prog="cronlens-snapshot",
        description="Manage cron expression snapshots",
    )
    subparsers = parser.add_subparsers(dest="snapshot_cmd")
    build_snapshot_parser(subparsers)
    return parser


def main(argv=None) -> int:  # pragma: no cover
    parser = build_standalone_parser()
    args = parser.parse_args(argv)
    return run_snapshot_command(args)
