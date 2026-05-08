"""Cron expression parser with alias support."""

from dataclasses import dataclass, field
from typing import List, Optional
from cronlens.aliases import resolve_alias, is_alias

DAY_NAMES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}
MONTH_NAMES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

FIELD_RANGES = [
    ("minute", 0, 59),
    ("hour", 0, 23),
    ("day_of_month", 1, 31),
    ("month", 1, 12),
    ("day_of_week", 0, 6),
]


@dataclass
class CronField:
    name: str
    raw: str
    values: List[int]
    min_val: int
    max_val: int


def is_wildcard(raw: str) -> bool:
    return raw.strip() == "*"


def _resolve_names(token: str, names: dict) -> str:
    for name, val in names.items():
        token = token.lower().replace(name, str(val))
    return token


def _expand_field(raw: str, min_val: int, max_val: int, names: Optional[dict] = None) -> List[int]:
    values = set()
    token = raw.strip()
    if names:
        token = _resolve_names(token, names)

    for part in token.split(","):
        if part == "*":
            values.update(range(min_val, max_val + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            if base == "*":
                start = min_val
                end = max_val
            elif "-" in base:
                start, end = map(int, base.split("-", 1))
            else:
                start = int(base)
                end = max_val
            values.update(range(start, end + 1, step))
        elif "-" in part:
            start, end = map(int, part.split("-", 1))
            values.update(range(start, end + 1))
        else:
            values.add(int(part))

    return sorted(values)


@dataclass
class CronExpression:
    raw: str
    resolved: str
    fields: List[CronField]
    from_alias: bool = False

    def __getattr__(self, name: str) -> CronField:
        for f in self.fields:
            if f.name == name:
                return f
        raise AttributeError(f"No field: {name}")


def parse(expression: str) -> CronExpression:
    """Parse a cron expression string (or alias) into a CronExpression."""
    original = expression.strip()
    from_alias = is_alias(original)
    resolved = resolve_alias(original)

    parts = resolved.split()
    if len(parts) != 5:
        raise ValueError(f"Expected 5 fields, got {len(parts)}: {resolved!r}")

    fields = []
    name_maps = [None, None, None, MONTH_NAMES, DAY_NAMES]
    for (fname, fmin, fmax), raw_part, names in zip(FIELD_RANGES, parts, name_maps):
        vals = _expand_field(raw_part, fmin, fmax, names)
        fields.append(CronField(name=fname, raw=raw_part, values=vals, min_val=fmin, max_val=fmax))

    return CronExpression(raw=original, resolved=resolved, fields=fields, from_alias=from_alias)
