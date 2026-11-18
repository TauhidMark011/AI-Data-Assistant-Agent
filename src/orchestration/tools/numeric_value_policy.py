
"""
Shared numeric value interpretation and validation policy.

Responsibilities:
    - Recognise standard integer values.
    - Recognise standard decimal values.
    - Recognise dot-separated thousands grouping.
    - Identify ambiguous decimal/grouping representations.
    - Preserve decimal precision using Decimal.
    - Reject malformed numeric representations.

Important:
    - Does not modify original dataset values.
    - Does not classify missing values.
    - Missing-value classification remains the responsibility
      of missing_value_policy.py.
"""

import re
from decimal import Decimal, InvalidOperation


INTEGER_PATTERN = re.compile(
    r"^[+-]?\d+$"
)

DECIMAL_PATTERN = re.compile(
    r"^[+-]?\d+\.\d+$"
)

DOT_GROUPED_INTEGER_PATTERN = re.compile(
    r"^[+-]?\d{1,3}(?:\.\d{3})+$"
)


def parse_numeric_value(value: str) -> dict:
    """
    Interpret a numeric value without guessing ambiguous formats.

    Returns:
        A dictionary containing:
            status:
                valid, ambiguous, or invalid

            parsed_value:
                Parsed integer or Decimal when unambiguous;
                otherwise None.

            format:
                Recognised numeric representation;
                otherwise None.
    """

    normalized_value = str(value).strip()

    invalid_result = {
        "status": "invalid",
        "parsed_value": None,
        "format": None,
    }

    if not normalized_value:
        return invalid_result

    # Standard integer representation.
    if INTEGER_PATTERN.fullmatch(normalized_value):
        return {
            "status": "valid",
            "parsed_value": int(normalized_value),
            "format": "integer",
        }

    # Check both decimal and dot-grouped interpretations.
    is_decimal = bool(
        DECIMAL_PATTERN.fullmatch(normalized_value)
    )

    is_dot_grouped = bool(
        DOT_GROUPED_INTEGER_PATTERN.fullmatch(
            normalized_value
        )
    )

    # A value such as 668.473 could represent either:
    #   668.473
    #   668473
    if is_decimal and is_dot_grouped:
        return {
            "status": "ambiguous",
            "parsed_value": None,
            "format": None,
        }

    # Standard decimal representation.
    if is_decimal:
        try:
            parsed_decimal = Decimal(normalized_value)
        except InvalidOperation:
            return invalid_result

        if not parsed_decimal.is_finite():
            return invalid_result

        return {
            "status": "valid",
            "parsed_value": parsed_decimal,
            "format": "decimal",
        }

    # Dot-separated thousands representation.
    if is_dot_grouped:
        parsed_integer = int(
            normalized_value.replace(".", "")
        )

        return {
            "status": "valid",
            "parsed_value": parsed_integer,
            "format": "dot_grouped_integer",
        }

    return invalid_result
