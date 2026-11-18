"""
column_normalization.py

Phase 3.1:
- Normalize column names using embedding similarity
- Assign confidence scores
- Apply only safe renames
"""

from difflib import SequenceMatcher #This algorithms comparing pairs of sequences. Compares: Characters, Order, Length, Unicode differences, Extra spaces

def similarity_score(a: str, b: str) -> float:
    """
   We compare two column names (for example Genrë¨ and Genre) and calculate how similar they look.
   The similarity score tells us how confident we are that they represent the same column.
   Genre vs Genrë¨ → very similar → high score | Genre vs Income → very different → low score.
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

#Threshold:“How sure do I need to be before auto-fixing?” threshold = 0.85. If ≥ 0.85 → very sure → auto rename, 0.60–0.85 → somewhat sure → suggest only, < 0.60 → not sure → do nothing. This prevents dangerous auto-changes.
def normalize_columns(df, schema_columns, threshold=0.85):
    """
    Normalize dataset column names using string similarity.

    - Compares each dataset column with schema columns
    - Auto-renames only when confidence is high
    - Suggests rename when confidence is medium
    - Avoids risky changes when confidence is low
    """

    rename_map = {}
    actions = []

    #Loop through each column in the dataset
    for col in df.columns:
        best_match = None #No match
        best_score = 0.0  #Zero confidence

        #Compare with every schema-defined column
        for schema_col in schema_columns:
            score = similarity_score(col, schema_col) #This returns a number between 0 and 1. 1.00 → identical, 0.90 → almost same, 0.50 → weak similarity, 0.10 → unrelated

            #Keep track of the closest match(best similarity)
            if score > best_score:
                best_score = score
                best_match = schema_col

        #High confidence → safe to auto-rename : “I’m confident enough AND the column name is different → fix it automatically.”
        if best_score >= threshold and col != best_match:
            rename_map[col] = best_match
            #Store rename instruction, Log what we did (for audit & explainability).
            actions.append({
                "original": col,
                "normalized": best_match,
                "confidence": round(best_score, 2),
                "auto_applied": True
            })

        #Medium confidence → suggest only (human review)
        elif best_score >= 0.6:
            actions.append({
                "original": col,
                "suggested": best_match,
                "confidence": round(best_score, 2),
                "auto_applied": False
            })

        #Low confidence → ignore (no action)

    #Apply only safe, high-confidence renames
    df = df.rename(columns=rename_map)

    return df, actions
#cleaned dataframe, audit trail (what changed, what was suggested).