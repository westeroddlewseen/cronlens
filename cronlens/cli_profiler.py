"""CLI integration for the cron expression profiler."""

import argparse
from cronlens.parser import CronExpression
from cronlens.profiler import profile
from cronlens.aliases import resolve_alias


def cmd_profile(args: argparse.Namespace) -> None:
    expressions = args.expressions
    verbose = getattr(args, "verbose", False)

    for raw in expressions:
        resolved = resolve_alias(raw)
        try:
            expr = CronExpression.parse(resolved)
        except ValueError as exc:
            print(f"[ERROR] '{raw}': {exc}")
            continue

        result = profile(expr)
        print("=" * 50)
        print(result.summary())

        if verbose:
            print(f"  weekday-only : {result.is_weekday_only}")
            print(f"  weekend-only : {result.is_weekend_only}")
            print(f"  specific DOM : {result.has_specific_dom}")
            print(f"  specific DOW : {result.has_specific_dow}")

        if result.clean:
            print("  [OK] No anomalies detected.")
        else:
            print(f"  [WARN] {len(result.anomalies)} anomaly(ies) found.")

    print("=" * 50)


def build_profile_parser(subparsers) -> argparse.ArgumentParser:
    p = subparsers.add_parser(
        "profile",
        help="Profile one or more cron expressions for patterns and anomalies",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Cron expression(s) or aliases to profile",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show additional boolean flags in output",
    )
    p.set_defaults(func=cmd_profile)
    return p


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cronlens-profile",
        description="Profile cron expressions for patterns and anomalies",
    )
    subparsers = parser.add_subparsers(dest="command")
    build_profile_parser(subparsers)
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
