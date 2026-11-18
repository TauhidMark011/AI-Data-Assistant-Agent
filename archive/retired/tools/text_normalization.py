"""
Phase 3.4 — Text & Categorical Normalization

Purpose:
- Normalize text fields to a standard, comparable format
- Reduce noise before schema enforcement & similarity matching
- Increase confidence for automated fixes
"""

import unicodedata
import pandas as pd
import re

def normalize_text(value: str) -> str:
    """
    Normalize a single text value safely.

    Steps:
    1. Convert to string
    2. Strip leading/trailing whitespace
    3. Convert to lowercase
    4. Remove accents (é → e, ü → u)
    5. Collapse multiple spaces
    """
    #If the value is missing (NaN), don’t touch it
    if pd.isna(value):
        return value

    value = str(value).strip().lower()

    #Remove accents and special characters using Unicode normalization. "Genrë¨" → "genre" 
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("utf-8")

    #Replace multiple spaces with single space
    value = re.sub(r"\s+", " ", value)

    return value #Return the cleaned value

def normalize_categorical_columns(df: pd.DataFrame, categorical_columns: list):
    """
    Normalize categorical/text columns in a DataFrame.
    (Takes: full dataset list of columns like ["genre", "country", "content rating"])
    Returns:
    - cleaned DataFrame
    - list of normalization actions for auditability
    """

    actions = []
    #Loop through only text-like columns
    for col in categorical_columns:
        if col not in df.columns:
            continue

        original_values = df[col].copy()
    #Apply the normalize_text() function to every row 
        df[col] = df[col].apply(normalize_text)

        #Track changes for audit trail, Detect which rows were actually modified
        changed = original_values != df[col]
        if changed.any():
            actions.append({
                "column": col,
                "changes_detected": int(changed.sum()),
                "auto_applied": True
            })
    #Store audit info. “We changed 42 values in genre safely.”
    return df, actions

#This handles messy rows like your IMDb dataset
def normalize_multivalue_column(df: pd.DataFrame, column: str, separator_pattern=r"[|;/]"): #Operates on ONE column (e.g., genre)
    """
    Normalize multi-valued categorical fields.

    Example:
    - "Drama | Crime" → ["drama", "crime"]
    - "Drama;Crime" → ["drama", "crime"]
    """

    actions = []

    if column not in df.columns:
        return df, actions
    #Inner function to process one row at a time
    def normalize_cell(cell):
        if pd.isna(cell):
            return cell
    #Split values using ; | /  Example: "Drama;Crime" → ["Drama", "Crime"]
        parts = re.split(separator_pattern, str(cell))
        parts = [normalize_text(p) for p in parts if p.strip()] #Normalize each value: ["Drama", "Crime"] → ["drama", "crime"]
        return parts #Store as a list, not a messy string
    
    df[column] = df[column].apply(normalize_cell) #Apply to entire column

    actions.append({
        "column": column,
        "multi_value_normalized": True,
        "auto_applied": True
    })

    return df, actions
