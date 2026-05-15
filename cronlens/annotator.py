"""Annotator: attach human-readable notes and metadata to cron expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from cronlens.parser import CronExpression
from cronlens.humanizer import humanize
from cronlens.tagger import tag, TagResult


@dataclass
class Annotation:
    expression: str
    human: str
    tags: TagResult
    note: Optional[str] = None
    labels: List[str] = field(default_factory=list)

    def has_label(self, label: str) -> bool:
        return label in self.labels

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "human": self.human,
            "tags": list(self.tags.tags),
            "note": self.note,
            "labels": self.labels,
        }

    def __repr__(self) -> str:
        note_part = f", note={self.note!r}" if self.note else ""
        return f"Annotation({self.expression!r}{note_part})"


def annotate(
    expr: CronExpression,
    note: Optional[str] = None,
    labels: Optional[List[str]] = None,
) -> Annotation:
    """Create an Annotation for a parsed CronExpression."""
    human = humanize(expr)
    tags = tag(expr)
    return Annotation(
        expression=str(expr),
        human=human,
        tags=tags,
        note=note,
        labels=labels or [],
    )


def annotate_many(
    exprs: List[CronExpression],
    notes: Optional[List[Optional[str]]] = None,
    labels: Optional[List[List[str]]] = None,
) -> List[Annotation]:
    """Annotate a list of expressions, optionally pairing notes and labels."""
    notes = notes or [None] * len(exprs)
    labels = labels or [[] for _ in exprs]
    return [
        annotate(expr, note=n, labels=lb)
        for expr, n, lb in zip(exprs, notes, labels)
    ]
