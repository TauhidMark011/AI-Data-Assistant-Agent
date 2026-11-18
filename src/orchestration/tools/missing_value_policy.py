
"""
Shared missing-value policy for deterministic data-quality tools.

The policy identifies genuinely missing values without treating
arbitrary text such as ERROR or UNKNOWN as missing.
"""

import pandas as pd


# Explicit default representations of missing values.
# Matching is case-insensitive and ignores surrounding whitespace.
MISSING_VALUE_TOKENS = frozenset(
    {
        "",
        "NAN",
        "NULL",
        "NONE",
        "N/A",
    }
)


def missing_value_mask(series: pd.Series) -> pd.Series:
    """
    Return a Boolean mask identifying missing values.

    Recognised values:
        - Actual Pandas/NumPy null values
        - Empty strings
        - Whitespace-only strings
        - NAN, NULL, NONE, and N/A (case-insensitive)

    Values such as ERROR, UNKNOWN, Not Applicable, and "-"
    are deliberately not classified as missing.

    The input Series is never modified.
    """

    normalized_values = (
        series.astype("string")
        .str.strip()
        .str.upper()
    )

    token_mask = normalized_values.isin(
        MISSING_VALUE_TOKENS
    )

    return (
        series.isna()
        | token_mask
    )
