"""Cron expression parser for cronlens.

Parses standard 5-field cron expressions into structured components
and provides human-readable descriptions.
"""

from dataclasses import dataclass
from typing import Optional

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]
FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}

MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DAY_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    raw: str
    field: str
    values: list[int]

    @property
    def is_wildcard(self) -> bool:
        return self.raw == "*"


@dataclass
class CronExpression:
    raw: str
    minute: CronField
    hour: CronField
    day_of_month: CronField
    month: CronField
    day_of_week: CronField

    @property
    def fields(self) -> list[CronField]:
        return [self.minute, self.hour, self.day_of_month, self.month, self.day_of_week]


def _resolve_names(value: str, mapping: dict) -> str:
    for name, num in mapping.items():
        value = value.lower().replace(name, str(num))
    return value


def _parse_field(raw: str, field: str) -> CronField:
    min_val, max_val = FIELD_RANGES[field]
    name_map = MONTH_NAMES if field == "month" else (DAY_NAMES if field == "day_of_week" else {})
    token = _resolve_names(raw, name_map)

    values: list[int] = []

    if token == "*":
        values = list(range(min_val, max_val + 1))
    elif "," in token:
        for part in token.split(","):
            values.extend(_parse_field(part, field).values)
    elif "/" in token:
        base, step = token.split("/", 1)
        step = int(step)
        base_field = _parse_field(base if base != "*" else f"{min_val}-{max_val}", field)
        start = base_field.values[0]
        values = list(range(start, max_val + 1, step))
    elif "-" in token:
        start, end = token.split("-", 1)
        values = list(range(int(start), int(end) + 1))
    else:
        values = [int(token)]

    if not all(min_val <= v <= max_val for v in values):
        raise ValueError(f"Field '{field}' value out of range [{min_val}, {max_val}]: {raw}")

    return CronField(raw=raw, field=field, values=sorted(set(values)))


def parse(expression: str) -> CronExpression:
    """Parse a 5-field cron expression string into a CronExpression object."""
    parts = expression.strip().split()
    if len(parts) != 5:
        raise ValueError(f"Expected 5 fields, got {len(parts)}: '{expression}'")

    fields = {name: _parse_field(raw, name) for name, raw in zip(FIELD_NAMES, parts)}
    return CronExpression(raw=expression, **fields)
