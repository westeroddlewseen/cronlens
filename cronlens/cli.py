"""CLI entry point for cronlens."""

import argparse
import sys
from datetime import datetime

from cronlens.parser import parse
from cronlens.humanizer import humanize
from cronlens.scheduler import CronScheduler
from cronlens.explainer import explain
from cronlens.formatter import format_full_report, format_next_runs
from cronlens.validator import validate
from cronlens.aliases import list_aliases, alias_description, register_alias, BUILTIN_ALIASES


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cronlens",
        description="Human-readable cron expression parser and schedule visualizer.",
    )
    sub = p.add_subparsers(dest="command")

    # explain command
    exp_p = sub.add_parser("explain", help="Explain a cron expression")
    exp_p.add_argument("expression", help="Cron expression or alias (e.g. '*/5 * * * *' or @daily)")
    exp_p.add_argument("--next", type=int, default=5, metavar="N", help="Show next N run times")

    # validate command
    val_p = sub.add_parser("validate", help="Validate a cron expression")
    val_p.add_argument("expression", help="Cron expression to validate")

    # aliases command
    ali_p = sub.add_parser("aliases", help="List all known cron aliases")
    ali_p.add_argument("--register", nargs=2, metavar=("NAME", "EXPR"), help="Register a custom alias")

    # next command
    next_p = sub.add_parser("next", help="Show next run times")
    next_p.add_argument("expression", help="Cron expression or alias")
    next_p.add_argument("--count", type=int, default=5, help="Number of next runs to show")

    return p


def cmd_explain(args) -> None:
    expr = parse(args.expression)
    if expr.from_alias:
        print(f"Alias '{args.expression}' resolves to: {expr.resolved}")
        desc = alias_description(args.expression)
        if desc:
            print(f"Description: {desc}")
        print()
    report = format_full_report(expr, count=args.next)
    print(report)


def cmd_validate(args) -> None:
    result = validate(args.expression)
    if result:
        print(f"✓ Valid: {args.expression}")
    else:
        print(f"✗ Invalid: {args.expression}")
        print(result.summary())
        sys.exit(1)


def cmd_aliases(args) -> None:
    if args.register:
        name, expr = args.register
        register_alias(name, expr)
        print(f"Registered alias '{name}' -> '{expr}'")
        return
    aliases = list_aliases()
    print(f"{'Alias':<20} {'Expression':<20} Description")
    print("-" * 70)
    for alias, expr in sorted(aliases.items()):
        desc = alias_description(alias) or ""
        print(f"{alias:<20} {expr:<20} {desc}")


def cmd_next(args) -> None:
    expr = parse(args.expression)
    scheduler = CronScheduler(expr)
    runs = scheduler.next_runs(args.count)
    print(format_next_runs(runs))


def main(argv=None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "explain": cmd_explain,
        "validate": cmd_validate,
        "aliases": cmd_aliases,
        "next": cmd_next,
    }

    if args.command in handlers:
        try:
            handlers[args.command](args)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
