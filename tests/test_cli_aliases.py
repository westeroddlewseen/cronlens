"""Integration tests for alias support in CLI and parser."""

import pytest
from unittest.mock import patch
from cronlens.aliases import _custom_aliases
from cronlens.parser import parse
from cronlens.cli import main


def setup_function():
    _custom_aliases.clear()


def test_parse_daily_alias():
    expr = parse("@daily")
    assert expr.from_alias is True
    assert expr.resolved == "0 0 * * *"
    assert expr.fields[0].values == [0]   # minute
    assert expr.fields[1].values == [0]   # hour


def test_parse_hourly_alias():
    expr = parse("@hourly")
    assert expr.resolved == "0 * * * *"
    assert expr.fields[0].values == [0]
    assert expr.fields[1].values == list(range(0, 24))


def test_parse_weekly_alias():
    expr = parse("@weekly")
    assert expr.resolved == "0 0 * * 0"
    assert expr.fields[4].values == [0]  # Sunday


def test_parse_non_alias_not_flagged():
    expr = parse("*/5 * * * *")
    assert expr.from_alias is False
    assert expr.resolved == "*/5 * * * *"


def test_cli_aliases_command(capsys):
    main(["aliases"])
    captured = capsys.readouterr()
    assert "@daily" in captured.out
    assert "@hourly" in captured.out


def test_cli_aliases_register(capsys):
    main(["aliases", "--register", "@mytest", "5 4 * * 1"])
    captured = capsys.readouterr()
    assert "@mytest" in captured.out
    # Now resolve it
    from cronlens.aliases import resolve_alias
    assert resolve_alias("@mytest") == "5 4 * * 1"


def test_cli_explain_alias(capsys):
    main(["explain", "@daily"])
    captured = capsys.readouterr()
    assert "0 0 * * *" in captured.out


def test_cli_next_alias(capsys):
    main(["next", "@hourly", "--count", "3"])
    captured = capsys.readouterr()
    assert captured.out.strip() != ""


def test_parse_yearly_alias():
    expr = parse("@yearly")
    assert expr.fields[2].values == [1]   # day 1
    assert expr.fields[3].values == [1]   # January


def test_parse_quarter_alias():
    expr = parse("@quarter")
    assert expr.fields[3].values == [1, 4, 7, 10]
