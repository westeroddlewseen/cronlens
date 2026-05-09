"""Rank and score cron expressions by frequency and predictability."""

from dataclasses import dataclass
from typing import List

from cronlens.parser import CronExpression


@dataclass
class CronRank:
    expression: str
    frequency_score: float   # runs per day (higher = more frequent)
    regularity_score: float  # 0.0 (chaotic) to 1.0 (perfectly regular)
    complexity_score: float  # 0.0 (simple) to 1.0 (complex)
    label: str               # human-readable tier label

    @property
    def overall_score(self) -> float:
        """Composite score: frequent + regular - complex."""
        return round(self.frequency_score * self.regularity_score - self.complexity_score, 4)


def _frequency_per_day(expr: CronExpression) -> float:
    """Estimate how many times the expression fires per day."""
    minutes = len(expr.minute)
    hours = len(expr.hour)
    days_of_month = len(expr.day_of_month)
    days_of_week = len(expr.day_of_week)

    # Effective days per week
    active_days_per_week = min(days_of_month / 31 * 7, days_of_week)
    active_days_fraction = active_days_per_week / 7

    runs_per_active_day = minutes * hours
    return round(runs_per_active_day * active_days_fraction, 4)


def _regularity(expr: CronExpression) -> float:
    """Score how evenly spaced the minute/hour values are (1.0 = perfectly even)."""
    scores = []
    for values in (expr.minute, expr.hour):
        if len(values) <= 1:
            scores.append(1.0)
            continue
        sorted_vals = sorted(values)
        gaps = [sorted_vals[i + 1] - sorted_vals[i] for i in range(len(sorted_vals) - 1)]
        avg_gap = sum(gaps) / len(gaps)
        if avg_gap == 0:
            scores.append(0.0)
            continue
        variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)
        # Normalise: lower variance → higher regularity
        score = 1.0 / (1.0 + variance / (avg_gap ** 2))
        scores.append(round(score, 4))
    return round(sum(scores) / len(scores), 4)


def _complexity(expr: CronExpression) -> float:
    """Score how complex the expression is based on field cardinality."""
    total_values = (
        len(expr.minute) + len(expr.hour) +
        len(expr.day_of_month) + len(expr.month) + len(expr.day_of_week)
    )
    max_values = 60 + 24 + 31 + 12 + 7
    return round(total_values / max_values, 4)


def _label(freq: float, regularity: float) -> str:
    if freq >= 60:
        return "high-frequency"
    if freq >= 1:
        return "regular" if regularity >= 0.8 else "irregular"
    if freq >= 1 / 7:
        return "weekly"
    return "rare"


def rank(expr: CronExpression) -> CronRank:
    """Compute a CronRank for a single parsed expression."""
    freq = _frequency_per_day(expr)
    reg = _regularity(expr)
    comp = _complexity(expr)
    return CronRank(
        expression=expr.expression,
        frequency_score=freq,
        regularity_score=reg,
        complexity_score=comp,
        label=_label(freq, reg),
    )


def rank_many(expressions: List[CronExpression]) -> List[CronRank]:
    """Rank a list of expressions, sorted by overall_score descending."""
    ranked = [rank(e) for e in expressions]
    return sorted(ranked, key=lambda r: r.overall_score, reverse=True)
