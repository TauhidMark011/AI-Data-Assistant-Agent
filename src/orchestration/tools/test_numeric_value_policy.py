
"""Regression tests for shared numeric interpretation policy."""

import pytest

from decimal import Decimal
from src.orchestration.tools.numeric_value_policy import (
    parse_numeric_value,
)

@pytest.mark.parametrize(
    ("value", "expected_value", "expected_format"),
    [
        ("100", 100, "integer"),
        ("-250", -250, "integer"),
        ("9.3", Decimal("9.3"), "decimal"),
        ("-12.75", Decimal("-12.75"), "decimal"),
        ("2.278.845", 2278845, "dot_grouped_integer"),
        ("1.572.674", 1572674, "dot_grouped_integer"),
        ("0", 0, "integer"),
        ("+0", 0, "integer"),
        ("-0", 0, "integer"),
        ("-2.278.845", -2278845, "dot_grouped_integer"),
        ("1234.567", Decimal("1234.567"), "decimal"),
    ],
)
def test_parse_valid_numeric_values(
    value,
    expected_value,
    expected_format,
):
    result = parse_numeric_value(value)

    assert result["status"] == "valid"
    assert result["parsed_value"] == expected_value
    assert result["format"] == expected_format

@pytest.mark.parametrize(
    "value",
    [
        "668.473",
        "12.345",
    ],
)
def test_identify_ambiguous_numeric_values(value):
    result = parse_numeric_value(value)

    assert result["status"] == "ambiguous"
    assert result["parsed_value"] is None
    assert result["format"] is None


@pytest.mark.parametrize(
    "value",
    [
        "9,.0",
        "8,9f",
        "8..8",
        "++8.7",
        "12.34.567",
        ".5",
        "1e3",
    ],
)
def test_reject_malformed_numeric_values(value):
    result = parse_numeric_value(value)

    assert result["status"] == "invalid"
    assert result["parsed_value"] is None
    assert result["format"] is None


def test_parse_numeric_value_with_surrounding_whitespace():
    result = parse_numeric_value(" 100 ")

    assert result["status"] == "valid"
    assert result["parsed_value"] == 100
    assert result["format"] == "integer"


@pytest.mark.parametrize(
    "value",
    [
        "",
        " ",
        "\t",
    ],
)
def test_reject_empty_numeric_values(value):
    result = parse_numeric_value(value)

    assert result["status"] == "invalid"
    assert result["parsed_value"] is None
    assert result["format"] is None


from decimal import Decimal

@pytest.mark.parametrize(
    ("value", "expected_value"),
    [
        (
            "9007199254740993",
            9007199254740993,
        ),
        (
            "123456789012345678901234567890",
            123456789012345678901234567890,
        ),
    ],
)
def test_preserve_large_integer_precision(value, expected_value):
    result = parse_numeric_value(value)

    assert result["status"] == "valid"
    assert result["parsed_value"] == expected_value
    assert result["format"] == "integer"


def test_preserve_high_precision_decimal():
    result = parse_numeric_value("123456789.123456789123456789")

    assert result["status"] == "valid"
    assert result["parsed_value"] == Decimal(
        "123456789.123456789123456789"
    )
    assert result["format"] == "decimal"
