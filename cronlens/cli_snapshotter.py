"""CLI commands for snapshot management."""

from __future__ import annotations

import argparse
import sys
from datetime import timezone

from cronlens.snapshotter import (
    CronSnapshot,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
)


def format_diff(diff) -> str:
    lines = [f"Summary: {diff.summary()}"]
    if diff.added:
        lines.append("\nAdded:")
        for expr in diff.added:
            lines.append(f"  + {expr}")
    if diff.removed:
        lines.append("\nRemoved:")
        for expr in diff.removed:
            lines.append(f"  - {expr}")
    if diff.unchanged:
        lines.append(f"\nUnchanged: {len(diff.unchanged)} expression(s)")
    return "\n".join(lines)


def cmd_snapshot_save(args: argparse.Namespace) -> None:
    expressions = [e.strip() for e in args.expressions if e.strip()]
    if not expressions:
        print("Error: no valid expressions provided.", file=sys.stderr)
        sys.exit(1)
    snapshot = CronSnapshot(
        name=args.name,
        expressions=expressions,
        note=args.note,
    )
    save_snapshot(snapshot, args.output)
    print(f"Snapshot '{args.name}' saved to {args.output} ({len(expressions)} expression(s))")


def cmd_snapshot_diff(args: argparse.Namespace) -> None:
    try:
        before = load_snapshot(args.before)
        after = load_snapshot(args.after)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: invalid snapshot file — {e}", file=sys.stderr)
        sys.exit(1)

    diff = diff_snapshots(before, after)
    ts_before = before.captured_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    ts_after = after.captured_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"Comparing '{before.name}' ({ts_before}) \u2192 '{after.name}' ({ts_after})")
    print(format_diff(diff))


def build_snapshot_parser(subparsers) -> None:
    snap = subparsers.add_parser("snapshot", help="Manage cron expression snapshots")
    sub = snap.add_subparsers(dest="snapshot_cmd")

    save_p = sub.add_parser("save", help="Save a snapshot")
    save_p.add_argument("name", help="Snapshot name")
    save_p.add_argument("expressions", nargs="+", help="Cron expressions")
    save_p.add_argument("-o", "--output", required=True, help="Output JSON file")
    save_p.add_argument("--note", default=None, help="Optional note")
    save_p.set_defaults(func=cmd_snapshot_save)

    diff_p = sub.add_parser("diff", help="Diff two snapshots")
    diff_p.add_argument("before", help="Path to the older snapshot JSON")
    diff_p.add_argument("after", help="Path to the newer snapshot JSON")
    diff_p.set_defaults(func=cmd_snapshot_diff)
