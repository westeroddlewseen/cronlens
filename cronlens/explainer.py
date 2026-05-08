"""Explains cron expressions in structured, human-readable detail."""

from cronlens.parser import CronExpression


DAY_NAMES = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
}

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def _ordinal(n: int) -> str:
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10 if n % 100 not in (11, 12, 13) else 0, "th")
    return f"{n}{suffix}"


def _explain_field(values: list[int], field: str, name_map: dict = None) -> str:
    """Return a human-readable explanation for a single cron field."""
    if name_map:
        named = [name_map[v] for v in values if v in name_map]
    else:
        named = [str(v) for v in values]

    if len(values) == 1:
        return f"at {field} {named[0]}"
    if len(values) <= 4:
        return f"at {field}s: {', '.join(named)}"
    step = values[1] - values[0] if len(values) > 1 else None
    if step and all(values[i] - values[i - 1] == step for i in range(1, len(values))):
        return f"every {step} {field}(s) starting at {named[0]}"
    return f"at {len(values)} specific {field}s"


def explain(expr: CronExpression) -> dict:
    """Return a structured explanation of a CronExpression."""
    minutes = sorted(expr.fields["minute"])
    hours = sorted(expr.fields["hour"])
    days_of_month = sorted(expr.fields["day_of_month"])
    months = sorted(expr.fields["month"])
    days_of_week = sorted(expr.fields["day_of_week"])

    return {
        "minute": _explain_field(minutes, "minute"),
        "hour": _explain_field(hours, "hour"),
        "day_of_month": _explain_field(days_of_month, "day of month"),
        "month": _explain_field(months, "month", MONTH_NAMES),
        "day_of_week": _explain_field(days_of_week, "day of week", DAY_NAMES),
        "summary": _build_summary(minutes, hours, days_of_month, months, days_of_week),
    }


def _build_summary(minutes, hours, doms, months, dows) -> str:
    parts = []

    if len(minutes) == 60 and len(hours) == 24:
        parts.append("every minute")
    elif len(minutes) == 60:
        hour_str = ", ".join(str(h) for h in hours[:3])
        parts.append(f"every minute during hour(s) {hour_str}")
    else:
        time_parts = [f"{h:02d}:{m:02d}" for h in hours for m in minutes]
        if len(time_parts) <= 4:
            parts.append("at " + ", ".join(time_parts))
        else:
            parts.append(f"at {len(time_parts)} time(s) per day")

    if len(months) < 12:
        parts.append("in " + ", ".join(MONTH_NAMES[m] for m in months[:3]))

    if len(dows) < 7:
        parts.append("on " + ", ".join(DAY_NAMES[d] for d in dows))
    elif len(doms) < 31:
        parts.append("on day(s) " + ", ".join(_ordinal(d) for d in doms[:3]))

    return "; ".join(parts) if parts else "every minute"
