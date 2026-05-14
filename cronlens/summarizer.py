"""Summarize and compare multiple cron expressions into a human-readable digest."""

from dataclasses import dataclass, field
from typing import List, Dict
from cronlens.parser import CronExpression
from cronlens.humanizer import humanize
from cronlens.ranker import CronRank
from cronlens.tagger import tag


@dataclass
class ExpressionSummary:
    expression: str
    human: str
    tags: List[str]
    frequency_per_day: float
    score: float


@dataclass
class DigestReport:
    summaries: List[ExpressionSummary]
    most_frequent: ExpressionSummary
    least_frequent: ExpressionSummary
    unique_tags: List[str]
    average_frequency: float
    average_score: float

    def tag_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for s in self.summaries:
            for t in s.tags:
                counts[t] = counts.get(t, 0) + 1
        return counts


def summarize(expressions: List[CronExpression]) -> DigestReport:
    """Build a DigestReport from a list of CronExpression objects."""
    if not expressions:
        raise ValueError("At least one expression is required")

    summaries = []
    for expr in expressions:
        rank = CronRank(expr)
        tag_result = tag(expr)
        summaries.append(
            ExpressionSummary(
                expression=str(expr),
                human=humanize(expr),
                tags=list(tag_result.tags),
                frequency_per_day=rank._frequency_per_day(),
                score=rank.overall_score(),
            )
        )

    most_frequent = max(summaries, key=lambda s: s.frequency_per_day)
    least_frequent = min(summaries, key=lambda s: s.frequency_per_day)

    all_tags: List[str] = []
    for s in summaries:
        for t in s.tags:
            if t not in all_tags:
                all_tags.append(t)

    avg_freq = sum(s.frequency_per_day for s in summaries) / len(summaries)
    avg_score = sum(s.score for s in summaries) / len(summaries)

    return DigestReport(
        summaries=summaries,
        most_frequent=most_frequent,
        least_frequent=least_frequent,
        unique_tags=all_tags,
        average_frequency=avg_freq,
        average_score=avg_score,
    )
