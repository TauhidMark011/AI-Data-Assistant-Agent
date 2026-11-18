
"""Precision-aware policy for float64 statistical analysis."""

import math
from decimal import Decimal


MAX_DECIMAL_SIGNIFICANT_DIGITS = 15


def _restricted_result(value: int | Decimal) -> dict:
    """Return a result that preserves the original exact value."""
    return {
        "status": "restricted",
        "float_value": None,
        "exact_value": value,
    }


def assess_float64_eligibility(value: int | Decimal) -> dict:
    """
    Assess whether an exact numeric value can enter float64 analysis.

    Policy:
    - Integers must round-trip exactly through float64.
    - Decimals must have no more than 15 coefficient digits.
    - Float conversion must remain finite.
    - Non-zero values must not underflow to zero.
    - The original exact value is always preserved.
    """
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise TypeError(
            "value must be an integer or Decimal instance"
        )

    if isinstance(value, Decimal) and not value.is_finite():
        return _restricted_result(value)

    try:
        float_value = float(value)
    except (OverflowError, ValueError):
        return _restricted_result(value)

    if not math.isfinite(float_value):
        return _restricted_result(value)

    if value != 0 and float_value == 0.0:
        return _restricted_result(value)

    if isinstance(value, int):
        # An integer is eligible only when float64 conversion
        # preserves its exact integer value.
        if int(float_value) != value:
            return _restricted_result(value)

    elif isinstance(value, Decimal):
        # Use the Decimal coefficient digit count.
        # This is deliberately conservative and includes trailing zeros.
        significant_digits = len(value.as_tuple().digits)

        if significant_digits > MAX_DECIMAL_SIGNIFICANT_DIGITS:
            return _restricted_result(value)

    return {
        "status": "eligible",
        "float_value": float_value,
        "exact_value": value,
    }
