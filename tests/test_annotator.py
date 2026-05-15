"""Tests for cronlens.annotator."""

import pytest
from cronlens.parser import CronExpression
from cronlens.annotator import Annotation, annotate, annotate_many


def parse(expr: str) -> CronExpression:
    return CronExpression.parse(expr)


def test_annotate_returns_annotation():
    ann = annotate(parse("* * * * *"))
    assert isinstance(ann, Annotation)


def test_annotation_expression_matches_input():
    ann = annotate(parse("0 9 * * 1"))
    assert "0" in ann.expression
    assert "9" in ann.expression


def test_annotation_human_is_string():
    ann = annotate(parse("0 0 * * *"))
    assert isinstance(ann.human, str)
    assert len(ann.human) > 0


def test_annotation_tags_is_tag_result():
    from cronlens.tagger import TagResult
    ann = annotate(parse("* * * * *"))
    assert isinstance(ann.tags, TagResult)


def test_annotation_note_defaults_none():
    ann = annotate(parse("0 12 * * *"))
    assert ann.note is None


def test_annotation_note_stored():
    ann = annotate(parse("0 12 * * *"), note="daily noon job")
    assert ann.note == "daily noon job"


def test_annotation_labels_default_empty():
    ann = annotate(parse("*/5 * * * *"))
    assert ann.labels == []


def test_annotation_labels_stored():
    ann = annotate(parse("0 0 * * *"), labels=["prod", "billing"])
    assert "prod" in ann.labels
    assert "billing" in ann.labels


def test_has_label_true():
    ann = annotate(parse("0 0 * * *"), labels=["critical"])
    assert ann.has_label("critical")


def test_has_label_false():
    ann = annotate(parse("0 0 * * *"), labels=["critical"])
    assert not ann.has_label("staging")


def test_to_dict_keys():
    ann = annotate(parse("0 6 * * *"), note="morning", labels=["ops"])
    d = ann.to_dict()
    assert "expression" in d
    assert "human" in d
    assert "tags" in d
    assert "note" in d
    assert "labels" in d


def test_to_dict_note_value():
    ann = annotate(parse("0 6 * * *"), note="morning")
    assert ann.to_dict()["note"] == "morning"


def test_to_dict_tags_is_list():
    ann = annotate(parse("* * * * *"))
    assert isinstance(ann.to_dict()["tags"], list)


def test_annotate_many_length():
    exprs = [parse("* * * * *"), parse("0 0 * * *"), parse("0 9 * * 1")]
    result = annotate_many(exprs)
    assert len(result) == 3


def test_annotate_many_with_notes():
    exprs = [parse("* * * * *"), parse("0 0 * * *")]
    result = annotate_many(exprs, notes=["every min", "midnight"])
    assert result[0].note == "every min"
    assert result[1].note == "midnight"


def test_annotate_many_no_notes_defaults_none():
    exprs = [parse("*/10 * * * *"), parse("0 12 * * *")]
    result = annotate_many(exprs)
    assert all(a.note is None for a in result)


def test_repr_contains_expression():
    ann = annotate(parse("0 0 1 * *"))
    assert "0 0 1 * *" in repr(ann) or ann.expression in repr(ann)
