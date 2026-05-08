"""Named cron expression aliases and preset management."""

from typing import Dict, Optional

BUILTIN_ALIASES: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@every_minute": "* * * * *",
    "@weekdays": "0 9 * * 1-5",
    "@weekends": "0 10 * * 6,0",
    "@noon": "0 12 * * *",
    "@midnight_utc": "0 0 * * *",
    "@quarter": "0 0 1 1,4,7,10 *",
}

_custom_aliases: Dict[str, str] = {}


def resolve_alias(expression: str) -> str:
    """Return the raw cron string for a given alias, or the expression itself."""
    key = expression.strip().lower()
    if key in _custom_aliases:
        return _custom_aliases[key]
    if key in BUILTIN_ALIASES:
        return BUILTIN_ALIASES[key]
    return expression


def register_alias(name: str, expression: str) -> None:
    """Register a custom alias for a cron expression."""
    if not name.startswith("@"):
        name = f"@{name}"
    _custom_aliases[name.lower()] = expression


def is_alias(expression: str) -> bool:
    """Return True if the expression is a known alias."""
    key = expression.strip().lower()
    return key in BUILTIN_ALIASES or key in _custom_aliases


def list_aliases() -> Dict[str, str]:
    """Return all known aliases (builtin + custom)."""
    combined = dict(BUILTIN_ALIASES)
    combined.update(_custom_aliases)
    return combined


def alias_description(alias: str) -> Optional[str]:
    """Return a human-readable description for a builtin alias."""
    descriptions: Dict[str, str] = {
        "@yearly": "Once a year, at midnight on January 1st",
        "@annually": "Once a year, at midnight on January 1st",
        "@monthly": "Once a month, at midnight on the 1st",
        "@weekly": "Once a week, at midnight on Sunday",
        "@daily": "Once a day, at midnight",
        "@midnight": "Once a day, at midnight",
        "@hourly": "Once an hour, at the start of the hour",
        "@every_minute": "Every minute",
        "@weekdays": "Weekdays at 9:00 AM",
        "@weekends": "Weekends at 10:00 AM",
        "@noon": "Every day at noon",
        "@midnight_utc": "Every day at midnight UTC",
        "@quarter": "First day of each quarter at midnight",
    }
    return descriptions.get(alias.strip().lower())
