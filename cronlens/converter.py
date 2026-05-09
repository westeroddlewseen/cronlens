"""Convert cron expressions between different formats and representations."""

from cronlens.parser import CronExpression
from cronlens.aliases import resolve_alias, is_alias, alias_description

# Map of well-known cron patterns to their alias equivalents
_PATTERN_TO_ALIAS = {
    "0 0 * * *": "@daily",
    "0 0 * * 0": "@weekly",
    "0 0 1 * *": "@monthly",
    "0 0 1 1 *": "@yearly",
    "* * * * *": "@every_minute",
    "0 * * * *": "@hourly",
}


def to_alias(expression: str) -> str | None:
    """Return a named alias for the expression if one exists, else None."""
    normalized = " ".join(expression.strip().split())
    return _PATTERN_TO_ALIAS.get(normalized)


def to_quartz(expression: str) -> str:
    """Convert a standard 5-field cron expression to a Quartz 6-field format.

    Quartz cron prepends a seconds field (fixed to '0').
    """
    resolved = resolve_alias(expression)
    parts = resolved.strip().split()
    if len(parts) != 5:
        raise ValueError(
            f"Expected a 5-field cron expression, got {len(parts)} fields: {expression!r}"
        )
    return "0 " + " ".join(parts)


def from_quartz(expression: str) -> str:
    """Strip the leading seconds field from a Quartz 6-field cron expression."""
    parts = expression.strip().split()
    if len(parts) != 6:
        raise ValueError(
            f"Expected a 6-field Quartz expression, got {len(parts)} fields: {expression!r}"
        )
    return " ".join(parts[1:])


def to_dict(expression: str) -> dict:
    """Parse a cron expression into a labelled dictionary of field values."""
    resolved = resolve_alias(expression)
    cron = CronExpression(resolved)
    return {
        "minute": sorted(cron.minute),
        "hour": sorted(cron.hour),
        "day_of_month": sorted(cron.day_of_month),
        "month": sorted(cron.month),
        "day_of_week": sorted(cron.day_of_week),
    }


def from_dict(fields: dict) -> str:
    """Build a cron expression string from a labelled field dictionary.

    Each value may be a list of ints or a single string like '*'.
    """
    def _render(values) -> str:
        if isinstance(values, str):
            return values
        unique = sorted(set(int(v) for v in values))
        if not unique:
            raise ValueError("Field must contain at least one value.")
        return ",".join(str(v) for v in unique)

    keys = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    parts = [_render(fields.get(k, "*")) for k in keys]
    return " ".join(parts)
