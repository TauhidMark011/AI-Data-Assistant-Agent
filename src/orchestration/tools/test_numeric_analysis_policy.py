
"""Tests for precision-aware statistical conversion policy."""

from decimal import Decimal

import pytest

from src.orchestration.tools.numeric_analysis_policy import (
    assess_float64_eligibility,
)


@pytest.mark.parametrize(
    ("value", "expected_status"),
    [
        (100, "eligible"),
        (-250, "eligible"),
        (Decimal("9.3"), "eligible"),
        (Decimal("123456789.123456"), "eligible"),
        (Decimal("123456789.123456789"), "restricted"),
        (Decimal("12345678901234567890"), "restricted"),
        (9007199254740993, "restricted"),
        (9007199254740992, "eligible"),
    ],
)
def test_assess_float64_eligibility(
    value,
    expected_status,
):
    result = assess_float64_eligibility(value)

    assert result["status"] == expected_status


def test_eligible_values_return_float_value():
    result = assess_float64_eligibility(Decimal("9.3"))

    assert result["status"] == "eligible"
    assert isinstance(result["float_value"], float)
    assert result["float_value"] == 9.3


def test_restricted_values_preserve_exact_value():
    original_value = Decimal(
        "123456789.123456789123456789"
    )

    result = assess_float64_eligibility(original_value)

    assert result["status"] == "restricted"
    assert result["float_value"] is None
    assert result["exact_value"] == original_value


@pytest.mark.parametrize(
    "value",
    [
        Decimal("1E+10000"),
        Decimal("1E-10000"),
    ],
)
def test_reject_float_overflow_and_underflow(value):
    result = assess_float64_eligibility(value)

    assert result["status"] == "restricted"
    assert result["float_value"] is None

@pytest.mark.parametrize(
    ("value", "expected_status"),
    [
        (Decimal("9.3000"), "eligible"),
        (Decimal("NaN"), "restricted"),
        (Decimal("Infinity"), "restricted"),
        (Decimal("-Infinity"), "restricted"),
        (9007199254740994, "eligible"),
        (9007199254740995, "restricted"),
    ],
)
def test_numeric_analysis_edge_cases(value, expected_status):
    result = assess_float64_eligibility(value)

    assert result["status"] == expected_status

    if expected_status == "restricted":
        assert result["float_value"] is None
        if isinstance(value, Decimal) and value.is_nan():
            assert result["exact_value"].is_nan()
        else:
            assert result["exact_value"] == value
    else:
        assert isinstance(result["float_value"], float)
        assert result["exact_value"] == value

def test_boolean_is_rejected():
    with pytest.raises(TypeError):
        assess_float64_eligibility(True)


@pytest.mark.parametrize(
    "value",
    [
        9.3,
        "123",
        None,
    ],
)
def test_unsupported_input_types_are_rejected(value):
    with pytest.raises(TypeError):
        assess_float64_eligibility(value)
