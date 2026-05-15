"""CLI interface for the annotator module."""

import argparse
from typing import List

from cronlens.parser import CronExpression
from cronlens.annotator import Annotation, annotate


def format_annotation(ann: Annotation) -> str:
    lines = [
        f"Expression : {ann.expression}",
        f"Human      : {ann.human}",
        f"Tags       : {', '.join(sorted(ann.tags.tags)) or 'none'}",
    ]
    if ann.note:
        lines.append(f"Note       : {ann.note}")
    if ann.labels:
        lines.append(f"Labels     : {', '.join(ann.labels)}")
    return "\n".join(lines)


def cmd_annotate(args: argparse.Namespace) -> None:
    expr = CronExpression.parse(args.expression)
    labels: List[str] = args.labels or []
    ann = annotate(expr, note=args.note, labels=labels)
    print(format_annotation(ann))
    if args.json:
        import json
        print(json.dumps(ann.to_dict(), indent=2))


def build_annotate_parser(subparsers=None) -> argparse.ArgumentParser:
    desc = "Annotate a cron expression with notes and labels"
    if subparsers is not None:
        p = subparsers.add_parser("annotate", help=desc)
    else:
        p = argparse.ArgumentParser(prog="cronlens annotate", description=desc)
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument("--note", default=None, help="Attach a human note")
    p.add_argument(
        "--label",
        dest="labels",
        action="append",
        metavar="LABEL",
        help="Add a label (repeatable)",
    )
    p.add_argument("--json", action="store_true", help="Also output JSON")
    p.set_defaults(func=cmd_annotate)
    return p


def main() -> None:
    parser = build_annotate_parser()
    args = parser.parse_args()
    cmd_annotate(args)


if __name__ == "__main__":
    main()
