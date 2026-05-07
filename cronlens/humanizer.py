"""Converts cron expressions into human-readable descriptions."""

from cronlens.parser import CronExpression

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

WEEKDAY_NAMES = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
]


def _describe_values(values: set, names: list = None, all_count: int = None) -> str:
    """Turn a set of integers into a readable string."""
    sorted_vals = sorted(values)
    if all_count and len(sorted_vals) == all_count:
        return "every"
    if names:
        labeled = [names[v] for v in sorted_vals if 0 <= v < len(names)]
        return ", ".join(labeled)
    return ", ".join(str(v) for v in sorted_vals)


def humanize(expression: CronExpression) -> str:
    """Return a human-readable description of the cron expression."""
    fields = expression.fields

    minute_desc = _describe_values(fields["minute"], all_count=60)
    hour_desc = _describe_values(fields["hour"], all_count=24)
    day_desc = _describe_values(fields["day"], all_count=31)
    month_desc = _describe_values(fields["month"], names=MONTH_NAMES, all_count=12)
    weekday_vals = {w % 7 for w in fields["weekday"]}
    weekday_desc = _describe_values(weekday_vals, names=WEEKDAY_NAMES, all_count=7)

    parts = []

    if minute_desc == "every" and hour_desc == "every":
        parts.append("every minute")
    elif minute_desc == "every":
        parts.append(f"every minute of hour {hour_desc}")
    else:
        time_str = f"at minute {minute_desc}"
        if hour_desc != "every":
            time_str += f" past hour {hour_desc}"
        parts.append(time_str)

    if day_desc != "every":
        parts.append(f"on day {day_desc} of the month")

    if month_desc != "every":
        parts.append(f"in {month_desc}")

    if weekday_desc != "every":
        parts.append(f"on {weekday_desc}")

    return ", ".join(parts) if parts else "every minute"
