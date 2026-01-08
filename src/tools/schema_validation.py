#(Schema-Aware Validation Tool) This is where Unnamed: 8 becomes a structural violation, not just a null stat. (Deterministic rule checks)
import json

def validate_schema(df):
    """
    Phase 2: Schema-aware validation

    Responsibilities:
    - Load schema definition
    - Check for missing required columns
    - Detect unexpected / malformed columns
    """

    # Load schema definition
    with open("src/schemas/imdb_schema.json", "r", encoding="utf-8") as f:
        schema = json.load(f)

    issues = []

    required_columns = set(schema["required_columns"])
    df_columns = set(df.columns)

    # Missing required columns
    missing = required_columns - df_columns
    if missing:
        issues.append(f"Missing required columns: {missing}")

    # Extra / unexpected columns
    extra = df_columns - required_columns
    for col in extra:
        if col.startswith("Unnamed"):
            issues.append(
                "Extra empty column detected due to malformed CSV rows"
            )
        else:
            issues.append(f"Unexpected column detected: {col}")

    return issues
