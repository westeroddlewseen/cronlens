"""CLI commands for the digest/summarizer feature."""

from typing import List
from cronlens.parser import CronExpression
from cronlens.summarizer import summarize, DigestReport
from cronlens.aliases import resolve_alias


def format_digest(report: DigestReport) -> str:
    lines = []
    lines.append("=" * 52)
    lines.append("  CRON DIGEST REPORT")
    lines.append("=" * 52)

    for i, s in enumerate(report.summaries, 1):
        lines.append(f"\n[{i}] {s.expression}")
        lines.append(f"    Human : {s.human}")
        lines.append(f"    Tags  : {', '.join(s.tags) if s.tags else 'none'}")
        lines.append(f"    Freq  : {s.frequency_per_day:.1f} runs/day")
        lines.append(f"    Score : {s.score:.2f}")

    lines.append("\n" + "-" * 52)
    lines.append("SUMMARY")
    lines.append(f"  Expressions   : {len(report.summaries)}")
    lines.append(f"  Avg frequency : {report.average_frequency:.1f} runs/day")
    lines.append(f"  Avg score     : {report.average_score:.2f}")
    lines.append(f"  Most frequent : {report.most_frequent.expression}")
    lines.append(f"  Least frequent: {report.least_frequent.expression}")
    lines.append(f"  All tags      : {', '.join(report.unique_tags) if report.unique_tags else 'none'}")

    tag_counts = report.tag_counts()
    if tag_counts:
        lines.append("\nTAG BREAKDOWN")
        for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {tag:<20} {count}x")

    lines.append("=" * 52)
    return "\n".join(lines)


def cmd_digest(args) -> None:
    """Handle the 'digest' CLI subcommand."""
    raw_expressions: List[str] = args.expressions
    parsed = []
    for raw in raw_expressions:
        resolved = resolve_alias(raw)
        try:
            parsed.append(CronExpression(resolved))
        except Exception as e:
            print(f"Error parsing '{raw}': {e}")
            return

    report = summarize(parsed)
    print(format_digest(report))
