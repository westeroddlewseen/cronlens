"""Cron expression validator with detailed error reporting."""

from dataclasses import dataclass, field
from typing import List, Optional

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}

FIELD_NAMES = list(FIELD_RANGES.keys())


@dataclass
class ValidationError:
    field: str
    segment: str
    message: str

    def __str__(self) -> str:
        return f"[{self.field}] '{self.segment}': {self.message}"


@dataclass
class ValidationResult:
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.valid

    def summary(self) -> str:
        if self.valid:
            return "Expression is valid."
        lines = ["Expression is invalid:"]
        for err in self.errors:
            lines.append(f"  - {err}")
        return "\n".join(lines)


def _validate_segment(segment: str, field_name: str, lo: int, hi: int) -> Optional[ValidationError]:
    """Validate a single segment (value, range, or step) for a field."""
    if segment == "*":
        return None

    if "/" in segment:
        parts = segment.split("/", 1)
        step_str = parts[1]
        if not step_str.isdigit():
            return ValidationError(field_name, segment, f"step '{step_str}' is not a valid integer")
        step = int(step_str)
        if step < 1:
            return ValidationError(field_name, segment, f"step must be >= 1, got {step}")
        base = parts[0]
        if base != "*":
            if not base.isdigit():
                return ValidationError(field_name, segment, f"base '{base}' is not a valid integer")
            val = int(base)
            if not (lo <= val <= hi):
                return ValidationError(field_name, segment, f"base value {val} out of range [{lo}-{hi}]")
        return None

    if "-" in segment:
        parts = segment.split("-", 1)
        if not parts[0].isdigit() or not parts[1].isdigit():
            return ValidationError(field_name, segment, "range must be two integers separated by '-'")
        start, end = int(parts[0]), int(parts[1])
        if not (lo <= start <= hi):
            return ValidationError(field_name, segment, f"range start {start} out of range [{lo}-{hi}]")
        if not (lo <= end <= hi):
            return ValidationError(field_name, segment, f"range end {end} out of range [{lo}-{hi}]")
        if start > end:
            return ValidationError(field_name, segment, f"range start {start} > end {end}")
        return None

    if not segment.isdigit():
        return ValidationError(field_name, segment, f"'{segment}' is not a valid integer")
    val = int(segment)
    if not (lo <= val <= hi):
        return ValidationError(field_name, segment, f"value {val} out of range [{lo}-{hi}]")
    return None


def validate(expression: str) -> ValidationResult:
    """Validate a cron expression string and return a ValidationResult."""
    parts = expression.strip().split()
    if len(parts) != 5:
        err = ValidationError(
            "expression", expression,
            f"expected 5 fields, got {len(parts)}"
        )
        return ValidationResult(valid=False, errors=[err])

    errors: List[ValidationError] = []
    for part, field_name in zip(parts, FIELD_NAMES):
        lo, hi = FIELD_RANGES[field_name]
        for segment in part.split(","):
            err = _validate_segment(segment, field_name, lo, hi)
            if err:
                errors.append(err)

    return ValidationResult(valid=len(errors) == 0, errors=errors)
