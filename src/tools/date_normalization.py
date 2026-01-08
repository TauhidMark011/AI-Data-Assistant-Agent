"""
date_normalization.py

Phase 3.3:
- Detect and normalize date columns
- Handle multiple date formats
- Enforce a single canonical format (ISO: YYYY-MM-DD)
- Apply fixes only when confidence is high
"""

import pandas as pd
from dateutil import parser
from datetime import datetime


def parse_date_safe(value):
    """
    Attempt to parse a single date value safely.

    Returns:
    - parsed_date (string in YYYY-MM-DD) OR original value
    - confidence score (0.0 to 1.0)

    Why confidence?
    - Some dates are ambiguous (01/02/03)
    - Some values are not dates at all
    """

    # Ifvalue is missing, keep it as-is (not an error here)
    if pd.isna(value):
        return value, 1.0

    try:
        #dateutil.parser can handle many real-world formats
        parsed = parser.parse(
            str(value),
            dayfirst=False,   # explicit: avoid locale ambiguity
            yearfirst=False,
            fuzzy=False       # do NOT guess wildly
        )

        #Convert to ISO standard format
        normalized = parsed.strftime("%Y-%m-%d")

        #If conversion changes the value, assign slightly lower confidence
        confidence = 0.95 if str(value) != normalized else 1.0

        return normalized, confidence

    except Exception:
        #Could not parse date safely
        return value, 0.0


def normalize_date_columns(df, date_columns, threshold=0.85):
    """
    Normalize date columns in a DataFrame.

    Parameters:
    - df: pandas DataFrame
    - date_columns: list of column names expected to contain dates
    - threshold: minimum confidence required to auto-apply fixes

    Returns:
    - updated DataFrame
    - list of actions (audit-friendly)
    """

    actions = []

    for col in date_columns:
        cleaned_values = []
        confidences = []

        #Process each value in the column
        for value in df[col]:
            parsed_value, confidence = parse_date_safe(value)
            cleaned_values.append(parsed_value)
            confidences.append(confidence)

        #Average confidence for the entire column
        avg_confidence = round(sum(confidences) / len(confidences), 2)

        if avg_confidence >= threshold:
            #Safe to apply normalization
            df[col] = cleaned_values
            actions.append({
                "column": col,
                "action": "date_normalization",
                "format": "YYYY-MM-DD",
                "confidence": avg_confidence,
                "auto_applied": True
            })
        else:
            #Too risky to auto-fix
            actions.append({
                "column": col,
                "action": "date_normalization",
                "format": "YYYY-MM-DD",
                "confidence": avg_confidence,
                "auto_applied": False,
                "note": "Manual review recommended due to ambiguity"
            })

    return df, actions
