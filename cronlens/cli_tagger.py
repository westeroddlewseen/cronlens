"""CLI integration helpers for the tagger feature."""

from __future__ import annotations
from typing import List
from cronlens.parser import CronExpression
from cronlens.tagger import tag, TagResult
from cronlens.aliases import resolve_alias


def format_tags(result: TagResult) -> str:
    """Return a human-readable string listing all tags."""
    if not result.tags:
        return "No tags assigned."
    tag_list = ", ".join(f"[{t}]" for t in result.tags)
    return f"Tags: {tag_list}"


def tag_expressions(expressions: List[str]) -> List[dict]:
    """Parse and tag multiple cron expressions, returning structured results."""
    results = []
    for raw in expressions:
        resolved = resolve_alias(raw)
        try:
            expr = CronExpression.parse(resolved)
            result = tag(expr)
            results.append({
                "input": raw,
                "resolved": resolved,
                "tags": result.tags,
                "formatted": format_tags(result),
            })
        except Exception as exc:  # noqa: BLE001
            results.append({
                "input": raw,
                "resolved": resolved,
                "tags": [],
                "error": str(exc),
            })
    return results


def cmd_tag(args) -> None:  # pragma: no cover
    """CLI command handler: print tags for given cron expression(s)."""
    results = tag_expressions(args.expressions)
    for entry in results:
        print(f"Expression : {entry['input']}")
        if "error" in entry:
            print(f"  Error    : {entry['error']}")
        else:
            print(f"  {entry['formatted']}")
        print()
