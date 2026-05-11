"""Cron expression linter — detects suspicious or potentially unintended patterns.

Goes beyond validation (is it syntactically correct?) to flag expressions that
are technically valid but likely wrong or inefficient in practice.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from cronlens.parser import CronExpression


@dataclass
class LintWarning:
    """A single lint warning for a cron expression."""

    code: str
    message: str
    field_name: str | None = None

    def __str__(self) -> str:
        location = f"[{self.field_name}] " if self.field_name else ""
        return f"{self.code}: {location}{self.message}"


@dataclass
class LintResult:
    """Collection of lint warnings for a single expression."""

    expression: str
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        """True when no warnings were found."""
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.clean:
            return f"✓ {self.expression!r} looks good — no issues found."
        lines = [f"{len(self.warnings)} warning(s) for {self.expression!r}:"]
        for w in self.warnings:
            lines.append(f"  • {w}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Individual lint checks
# ---------------------------------------------------------------------------

def _check_both_dom_and_dow(expr: CronExpression) -> List[LintWarning]:
    """Warn when both day-of-month and day-of-week are restricted.

    Most cron implementations use OR semantics for these two fields, which
    surprises many users who expect AND semantics.
    """
    dom_wild = set(expr.day_of_month) == set(range(1, 32))
    dow_wild = set(expr.day_of_week) == set(range(0, 7))
    if not dom_wild and not dow_wild:
        return [
            LintWarning(
                code="W001",
                message=(
                    "Both day-of-month and day-of-week are restricted. "
                    "Most cron daemons use OR logic between these fields, "
                    "which may fire more often than intended."
                ),
            )
        ]
    return []


def _check_high_frequency(expr: CronExpression) -> List[LintWarning]:
    """Warn when the expression fires more than once per minute (impossible)
    or at an unusually high rate that may overload a system."""
    runs_per_hour = len(expr.minute) * len(expr.hour)
    # More than 60 distinct minute+hour combos per day is fine; warn above 720
    runs_per_day = runs_per_hour * len(expr.day_of_month)
    if runs_per_day > 1440:
        return [
            LintWarning(
                code="W002",
                message=(
                    f"Expression may fire up to {runs_per_day} times per day. "
                    "Verify this high frequency is intentional."
                ),
            )
        ]
    return []


def _check_dom_31_in_short_months(expr: CronExpression) -> List[LintWarning]:
    """Warn when day 31 is specified — it will silently skip in shorter months."""
    if 31 in expr.day_of_month and set(expr.day_of_month) != set(range(1, 32)):
        return [
            LintWarning(
                code="W003",
                field_name="day-of-month",
                message=(
                    "Day 31 is specified explicitly. The job will not run in "
                    "months with fewer than 31 days (Apr, Jun, Sep, Nov, Feb)."
                ),
            )
        ]
    return []


def _check_feb_29(expr: CronExpression) -> List[LintWarning]:
    """Warn when day 29 is used — it only exists in February on leap years."""
    months_restricted = set(expr.month) != set(range(1, 13))
    if (
        29 in expr.day_of_month
        and set(expr.day_of_month) != set(range(1, 32))
        and not months_restricted
    ):
        return [
            LintWarning(
                code="W004",
                field_name="day-of-month",
                message=(
                    "Day 29 is specified without restricting the month. "
                    "This will only fire in February on leap years."
                ),
            )
        ]
    return []


def _check_redundant_step_one(raw: str) -> List[LintWarning]:
    """Warn about */1 patterns — equivalent to * but unnecessarily verbose."""
    warnings: List[LintWarning] = []
    for part in raw.split():
        if part == "*/1" or part.endswith("/1"):
            warnings.append(
                LintWarning(
                    code="W005",
                    message=(
                        f"Field value {part!r} uses a step of 1, "
                        "which is equivalent to '*' and can be simplified."
                    ),
                )
            )
    return warnings


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_CHECKS = [
    _check_both_dom_and_dow,
    _check_high_frequency,
    _check_dom_31_in_short_months,
    _check_feb_29,
]


def lint(expression: str) -> LintResult:
    """Run all lint checks against *expression* and return a :class:`LintResult`.

    Parameters
    ----------
    expression:
        A standard 5-field cron expression string.

    Returns
    -------
    LintResult
        Contains zero or more :class:`LintWarning` objects.
    """
    result = LintResult(expression=expression)

    # Structural checks that don't need a parsed object
    result.warnings.extend(_check_redundant_step_one(expression))

    try:
        expr = CronExpression.parse(expression)
    except Exception:
        # Parsing failed — let the validator handle syntax errors; bail out.
        return result

    for check in _CHECKS:
        result.warnings.extend(check(expr))

    return result
