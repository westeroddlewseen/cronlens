"""Compare two cron expressions and produce a human-readable comparison report."""

from dataclasses import dataclass, field
from typing import List

from cronlens.parser import CronExpression
from cronlens.humanizer import humanize
from cronlens.ranker import CronRank
from cronlens.differ import CronDiff


@dataclass
class ComparisonReport:
    expr_a: str
    expr_b: str
    human_a: str
    human_b: str
    score_a: float
    score_b: float
    freq_a: float
    freq_b: float
    changed_fields: List[str]
    is_identical: bool
    more_frequent: str  # 'a', 'b', or 'equal'
    more_complex: str   # 'a', 'b', or 'equal'


def compare(expr_a: CronExpression, expr_b: CronExpression) -> ComparisonReport:
    """Compare two CronExpression objects and return a ComparisonReport."""
    human_a = humanize(expr_a)
    human_b = humanize(expr_b)

    rank_a = CronRank(expr_a)
    rank_b = CronRank(expr_b)

    score_a = rank_a.overall_score()
    score_b = rank_b.overall_score()

    freq_a = rank_a._frequency_per_day()
    freq_b = rank_b._frequency_per_day()

    diff = CronDiff(expr_a, expr_b)
    changed_fields = [fd.field for fd in diff.changed_fields()]
    is_identical = diff.is_identical()

    if freq_a > freq_b:
        more_frequent = "a"
    elif freq_b > freq_a:
        more_frequent = "b"
    else:
        more_frequent = "equal"

    complexity_a = rank_a._complexity()
    complexity_b = rank_b._complexity()

    if complexity_a > complexity_b:
        more_complex = "a"
    elif complexity_b > complexity_a:
        more_complex = "b"
    else:
        more_complex = "equal"

    return ComparisonReport(
        expr_a=str(expr_a),
        expr_b=str(expr_b),
        human_a=human_a,
        human_b=human_b,
        score_a=score_a,
        score_b=score_b,
        freq_a=freq_a,
        freq_b=freq_b,
        changed_fields=changed_fields,
        is_identical=is_identical,
        more_frequent=more_frequent,
        more_complex=more_complex,
    )


def format_comparison(report: ComparisonReport) -> str:
    """Render a ComparisonReport as a human-readable string."""
    lines = [
        "=== Cron Comparison ===",
        f"  A: {report.expr_a}",
        f"     {report.human_a}",
        f"  B: {report.expr_b}",
        f"     {report.human_b}",
        "",
        f"  Identical : {'yes' if report.is_identical else 'no'}",
    ]

    if not report.is_identical:
        fields_str = ", ".join(report.changed_fields) if report.changed_fields else "none"
        lines.append(f"  Changed   : {fields_str}")

    lines += [
        "",
        f"  Freq/day  : A={report.freq_a:.1f}  B={report.freq_b:.1f}  "
        f"(more frequent: {report.more_frequent.upper()})",
        f"  Score     : A={report.score_a:.2f}  B={report.score_b:.2f}  "
        f"(more complex: {report.more_complex.upper()})",
    ]

    return "\n".join(lines)
