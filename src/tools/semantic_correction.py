"""
semantic_correction.py

Phase 3.5:
Semantic typo correction using embeddings + confidence scoring.

Purpose:
- Fix misspellings safely (e.g., "Advnture" → "adventure")
- Never guess blindly
- Always report confidence
"""
#Cosine similarity measures how similar two pieces of text are by comparing the angle between their embedding vectors, not their spelling.
#Output range: 0.0 → 1.0. 1.0 = identical meaning, 0.9+ = very similar meaning, 0.9+ = very similar meaning. It only compares vectors produced by an embedding model.
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def semantic_correct_column(
    df,
    column: str,
    allowed_values: list,
    embed_fn,
    auto_threshold: float = 0.90,
    suggest_threshold: float = 0.75
):
    """
    Parameters:
    - df: pandas DataFrame
    - column: column name to correct (e.g., 'genre')
    - allowed_values: canonical values from schema
    - embed_fn: function that returns embedding vector for a string
    - auto_threshold: confidence above which fix is auto-applied
    - suggest_threshold: confidence above which suggestion is given

    Returns:
    - updated DataFrame
    - list of actions taken (audit log)
    """

    actions = []

    #Precompute embeddings for schema values (once)
    schema_embeddings = {
        value: embed_fn(value) for value in allowed_values
    }

    def correct_value(value):
        """
        Correct a single cell value using semantic similarity.
        """

        if value is None or value not in df[column].values:
            return value

        #Get embedding for the value
        value_embedding = embed_fn(value)

        best_match = None
        best_score = 0.0

        #Compare with all schema values
        for schema_value, schema_emb in schema_embeddings.items():
            score = cosine_similarity(
                [value_embedding], [schema_emb]
            )[0][0]

            if score > best_score:
                best_score = score
                best_match = schema_value

        #Case 1: High confidence → auto-fix
        if best_score >= auto_threshold and value != best_match:
            actions.append({
                "column": column,
                "original": value,
                "corrected": best_match,
                "confidence": round(best_score, 2),
                "auto_applied": True
            })
            return best_match

        #Case 2: Medium confidence → suggest only
        elif best_score >= suggest_threshold:
            actions.append({
                "column": column,
                "original": value,
                "suggested": best_match,
                "confidence": round(best_score, 2),
                "auto_applied": False
            })
            return value

        #Case 3: Low confidence → do nothing
        return value

    #Apply correction to column
    df[column] = df[column].apply(correct_value)

    return df, actions
