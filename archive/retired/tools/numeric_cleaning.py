"""
numeric_cleaning.py

Phase 3.2:
- Detect numeric columns with symbols or units
- Clean values safely
- Assign confidence scores
"""

import re
import pandas as pd

NUMERIC_REGEX = re.compile(r"[^\d.\-]")

def clean_numeric_value(value):
    """
    Clean a single numeric value by removing symbols.
    Returns (cleaned_value, confidence).
    """
    if pd.isna(value):
        return value, 1.0

    original = str(value)

    # Remove currency symbols, commas, spaces, units
    cleaned = NUMERIC_REGEX.sub("", original)

    try:
        number = float(cleaned)
        confidence = 0.95 if cleaned != original else 1.0
        return number, confidence
    except ValueError:
        return value, 0.0  # Unsafe to convert


def clean_numeric_columns(df, columns):
    """
    Clean numeric columns safely.

    Returns:
    - updated DataFrame
    - list of actions with confidence
    """

    actions = []

    for col in columns:
        new_values = []
        confidences = []

        for v in df[col]:
            cleaned, conf = clean_numeric_value(v)
            new_values.append(cleaned)
            confidences.append(conf)

        avg_conf = round(sum(confidences) / len(confidences), 2)

        if avg_conf >= 0.85:
            df[col] = new_values
            actions.append({
                "column": col,
                "action": "numeric_cleaning",
                "confidence": avg_conf,
                "auto_applied": True
            })
        else:
            actions.append({
                "column": col,
                "action": "numeric_cleaning",
                "confidence": avg_conf,
                "auto_applied": False
            })

    return df, actions
