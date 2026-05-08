"""Tests for cronlens.aliases module."""

import pytest
from cronlens.aliases import (
    resolve_alias,
    register_alias,
    is_alias,
    list_aliases,
    alias_description,
    BUILTIN_ALIASES,
    _custom_aliases,
)


def setup_function():
    """Clear custom aliases before each test."""
    _custom_aliases.clear()


def test_resolve_builtin_alias():
    assert resolve_alias("@daily") == "0 0 * * *"


def test_resolve_yearly_alias():
    assert resolve_alias("@yearly") == "0 0 1 1 *"


def test_resolve_unknown_returns_original():
    expr = "*/5 * * * *"
    assert resolve_alias(expr) == expr


def test_resolve_alias_case_insensitive():
    assert resolve_alias("@DAILY") == "0 0 * * *"
    assert resolve_alias("@Daily") == "0 0 * * *"


def test_is_alias_true_for_builtin():
    assert is_alias("@hourly") is True


def test_is_alias_false_for_expression():
    assert is_alias("0 * * * *") is False


def test_register_and_resolve_custom_alias():
    register_alias("@deploy", "0 2 * * 1")
    assert resolve_alias("@deploy") == "0 2 * * 1"


def test_register_alias_adds_at_prefix():
    register_alias("backup", "0 3 * * *")
    assert resolve_alias("@backup") == "0 3 * * *"


def test_is_alias_true_for_custom():
    register_alias("@myalias", "*/10 * * * *")
    assert is_alias("@myalias") is True


def test_list_aliases_includes_builtins():
    aliases = list_aliases()
    assert "@daily" in aliases
    assert "@hourly" in aliases
    assert "@yearly" in aliases


def test_list_aliases_includes_custom():
    register_alias("@custom", "5 4 * * *")
    aliases = list_aliases()
    assert "@custom" in aliases


def test_alias_description_known():
    desc = alias_description("@daily")
    assert desc is not None
    assert "midnight" in desc.lower()


def test_alias_description_unknown_returns_none():
    assert alias_description("@nonexistent") is None


def test_resolve_alias_strips_whitespace():
    assert resolve_alias("  @weekly  ") == "0 0 * * 0"


def test_all_builtins_resolvable():
    for alias in BUILTIN_ALIASES:
        assert resolve_alias(alias) == BUILTIN_ALIASES[alias]
