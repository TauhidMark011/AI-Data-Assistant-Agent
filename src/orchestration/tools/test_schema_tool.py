
"""
Unit tests for SchemaInferenceTool.

These tests establish the current schema inference behaviour
before adding semantic-type detection and data profiling.
"""

import json

import pandas as pd

from src.orchestration.tools.schema_tool import SchemaInferenceTool

def test_schema_tool_infers_basic_column_types(tmp_path):
    """Verify that the tool reports Pandas-inferred column types."""

    csv_path = tmp_path / "basic_dataset.csv"

    df = pd.DataFrame(
        {
            "movie_id": ["tt001", "tt002"],
            "duration": [120, 150],
            "score": [8.5, 9.0],
        }
    )

    df.to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))

    assert result.startswith("Inferred schema:")

    schema = json.loads(result.split("\n", 1)[1])

    assert schema["movie_id"]["type"] == "object"
    assert schema["duration"]["type"] in ("int64", "int32")
    assert schema["score"]["type"] == "float64"

def test_schema_tool_detects_nullable_columns(tmp_path):
    """Verify that columns containing missing values are nullable."""

    csv_path = tmp_path / "nullable_dataset.csv"

    df = pd.DataFrame(
        {
            "movie": ["Movie A", "Movie B"],
            "score": [8.5, None],
        }
    )

    df.to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))

    schema = json.loads(result.split("\n", 1)[1])

    assert schema["movie"]["nullable"] is False
    assert schema["score"]["nullable"] is True

def test_schema_tool_accepts_custom_uploaded_file(tmp_path):
    """Verify that the tool processes a supplied CSV path."""

    csv_path = tmp_path / "uploaded_dataset.csv"

    pd.DataFrame(
        {
            "movie": ["Movie A", "Movie B"],
            "score": [8.5, 9.0],
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))

    assert result.startswith("Inferred schema:")
    assert "movie" in result
    assert "score" in result

def test_schema_tool_handles_missing_file(tmp_path):
    """Verify that a missing file produces a readable error."""

    missing_path = tmp_path / "missing_dataset.csv"

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(missing_path))

    assert result.startswith("Error inferring schema:")

def test_schema_tool_detects_numeric_candidate_with_invalid_values(tmp_path):
    """Identify numeric-looking columns containing malformed values."""

    csv_path = tmp_path / "numeric_dataset.csv"

    pd.DataFrame(
        {
            "score": ["8.5", "9.0", "7.5", "9,.0", "8,9f"],
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    score = schema["score"]

    assert score["semantic_type"] == "numeric_candidate"
    assert score["total_records"] == 5
    assert score["valid_values"] == 3
    assert score["invalid_values"] == 2
    assert score["invalid_samples"] == ["9,.0", "8,9f"]

def test_schema_tool_detects_date_candidate_with_mixed_formats(tmp_path):
    """Identify date-like columns containing multiple date formats."""

    csv_path = tmp_path / "date_dataset.csv"

    pd.DataFrame(
        {
            "release_date": [
                "1995-02-10",
                "09 21 1972",
                "23-07-2008",
                "not-a-date",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    release_date = schema["release_date"]

    assert release_date["semantic_type"] == "date_candidate"
    assert release_date["total_records"] == 4
    assert release_date["valid_values"] == 3
    assert release_date["invalid_values"] == 1
    assert release_date["invalid_samples"] == ["not-a-date"]

def test_schema_tool_identifies_categorical_candidate(tmp_path):
    """Identify categorical columns without enforcing an enum."""

    csv_path = tmp_path / "category_dataset.csv"

    pd.DataFrame(
        {
            "country": [
                "USA",
                "UK",
                "India",
                "USA",
                "UnknownCountry",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    country = schema["country"]

    assert country["semantic_type"] == "categorical_candidate"
    assert country["total_records"] == 5
    assert country["valid_values"] == 5
    assert country["invalid_values"] == 0

def test_schema_tool_does_not_modify_original_values(tmp_path):
    """Verify profiling does not modify the source CSV values."""

    csv_path = tmp_path / "preserve_values.csv"

    original_df = pd.DataFrame(
        {
            "score": ["8.5", "9,.0", "8,9f"],
            "income": ["$ 1000", "$ 4o8,035", "$ 2000"],
        }
    )

    original_df.to_csv(csv_path, index=False)

    original_content = csv_path.read_bytes()

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))

    assert result.startswith("Inferred schema:")

    # The source file must remain byte-for-byte unchanged.
    assert csv_path.read_bytes() == original_content

    # Original malformed values must still exist in the source.
    reloaded_df = pd.read_csv(csv_path, dtype=str)

    assert reloaded_df["score"].tolist() == [
        "8.5",
        "9,.0",
        "8,9f",
    ]

    assert reloaded_df["income"].tolist() == [
        "$ 1000",
        "$ 4o8,035",
        "$ 2000",
    ]

def test_schema_tool_detects_currency_candidate(tmp_path):
    """Identify currency values and malformed entries."""

    csv_path = tmp_path / "currency_dataset.csv"

    pd.DataFrame(
        {
            "income": [
                "$1,000",
                "$2,500",
                "$3,000",
                "not disclosed",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    income = schema["income"]

    assert income["semantic_type"] == "currency_candidate"
    assert income["valid_values"] == 3
    assert income["invalid_values"] == 1

def test_schema_tool_detects_percentage_candidate(tmp_path):
    """Identify percentage values and malformed entries."""

    csv_path = tmp_path / "percentage_dataset.csv"

    pd.DataFrame(
        {
            "completion": [
                "85%",
                "90%",
                "75%",
                "invalid",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    completion = schema["completion"]

    assert completion["semantic_type"] == "percentage_candidate"
    assert completion["valid_values"] == 3
    assert completion["invalid_values"] == 1

def test_schema_tool_detects_identifier_candidate(tmp_path):
    """Identify unique identifier-like values."""

    csv_path = tmp_path / "identifier_dataset.csv"

    pd.DataFrame(
        {
            "record_reference": [
                "tt0111161",
                "tt0068646",
                "tt0468569",
                "tt0109830",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    reference = schema["record_reference"]

    assert reference["semantic_type"] == "identifier_candidate"
    assert reference["valid_values"] == 4
    assert reference["invalid_values"] == 0

def test_schema_tool_detects_boolean_candidate(tmp_path):
    """Identify Boolean values with different representations."""

    csv_path = tmp_path / "boolean_dataset.csv"

    pd.DataFrame(
        {
            "active": [
                "True",
                "False",
                "Yes",
                "No",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    active = schema["active"]

    assert active["semantic_type"] == "boolean_candidate"
    assert active["valid_values"] == 4
    assert active["invalid_values"] == 0

def test_schema_tool_identifies_completely_empty_column(tmp_path):
    """Identify columns containing no non-missing values."""

    csv_path = tmp_path / "empty_dataset.csv"

    pd.DataFrame(
        {
            "empty_column": [None, None, None],
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    empty_column = schema["empty_column"]

    assert empty_column["semantic_type"] == "empty_candidate"
    assert empty_column["total_records"] == 3
    assert empty_column["missing_values"] == 3
    assert empty_column["valid_values"] == 0
    assert empty_column["invalid_values"] == 0

def test_schema_tool_does_not_misclassify_numeric_scores_as_dates(tmp_path):
    """Prefer numeric classification for decimal score values."""

    csv_path = tmp_path / "ambiguous_score_dataset.csv"

    pd.DataFrame(
        {
            "score": [
                "9.3",
                "8.7",
                "7.5",
                "6.8",
                "9.1",
                "8.4",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    score = schema["score"]

    assert score["semantic_type"] == "numeric_candidate"
    assert score["valid_values"] == 6
    assert score["invalid_values"] == 0

def test_schema_tool_detects_currency_with_different_number_formats(tmp_path):
    """Recognise valid currency formats and reject malformed amounts."""

    csv_path = tmp_path / "currency_formats_dataset.csv"

    pd.DataFrame(
        {
            "income": [
                "$1000",
                "$ 28815245",
                "$1,000",
                "$ 1,000.50",
                "$ 4o8,035,783",
                "Not Applicable",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    income = schema["income"]

    assert income["semantic_type"] == "currency_candidate"
    assert income["total_records"] == 6
    assert income["valid_values"] == 4
    assert income["invalid_values"] == 2
    assert income["invalid_samples"] == [
        "$ 4o8,035,783",
        "Not Applicable",
    ]


def test_schema_tool_detects_dot_separated_thousands(tmp_path):
    """Recognise numbers using periods as thousands separators."""

    csv_path = tmp_path / "dot_separated_numbers.csv"

    pd.DataFrame(
        {
            "votes": [
                "2.278.845",
                "1.572.674",
                "1.098.714",
                "668.473",
                "invalid",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    votes = schema["votes"]

    assert votes["semantic_type"] == "numeric_candidate"
    assert votes["total_records"] == 5
    assert votes["valid_values"] == 3
    assert votes["ambiguous_numeric_values"] == 1
    assert votes["ambiguous_numeric_samples"] == ["668.473"]
    assert votes["invalid_values"] == 1
    assert votes["invalid_samples"] == ["invalid"]

def test_schema_tool_preserves_decimal_numeric_values(tmp_path):
    """Ensure decimal numbers are not interpreted as grouped integers."""

    csv_path = tmp_path / "decimal_numbers.csv"

    pd.DataFrame(
        {
            "score": ["9.3", "8.7", "7.5", "6.8"]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    score = schema["score"]

    assert score["semantic_type"] == "numeric_candidate"
    assert score["valid_values"] == 4
    assert score["invalid_values"] == 0


def test_schema_tool_uses_shared_missing_value_policy(tmp_path):
    """Verify that schema profiling follows the shared missing-value policy."""

    csv_path = tmp_path / "shared_missing_policy.csv"

    df = pd.DataFrame(
        {
            "status": [
                "",
                "   ",
                "NaN",
                "NULL",
                "NONE",
                "N/A",
                "ERROR",
                "UNKNOWN",
                "Not Applicable",
                "-",
            ]
        }
    )

    df.to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()

    result = tool._run(
        file_path=str(csv_path)
    )

    schema = json.loads(result.split("\n", 1)[1])

    status_column = schema["status"]

    assert status_column["nullable"] is True
    assert status_column["total_records"] == 10

    # Six values are recognised as missing.
    assert status_column["missing_values"] == 6

    # The remaining four text values are retained.
    assert status_column["valid_values"] == 4
    assert status_column["invalid_values"] == 0


def test_schema_tool_recognises_extended_date_formats():
    """Recognise common date formats with varied separators and notation."""

    tool = SchemaInferenceTool()

    valid_dates = [
        "23 -07-2008",
        "22 Feb 04",
        "10-29-99",
        "23rd December of 1966",
    ]

    for value in valid_dates:
        assert tool._is_valid_date(value), (
            f"Expected a valid date representation: {value}"
        )


def test_schema_tool_rejects_ambiguous_mixed_separator_date():
    """Reject dates containing inconsistent separators."""

    tool = SchemaInferenceTool()

    ambiguous_dates = [
        "01/16-03",
        "2020/-12-15",
        "31//12/2020",
        "not-a-date",
    ]

    for value in ambiguous_dates:
        assert not tool._is_valid_date(value), (
            f"Unexpectedly accepted an ambiguous or invalid date: {value}"
        )

def test_schema_tool_identifies_ambiguous_date_formats():
    """Identify dates that have multiple valid interpretations."""

    tool = SchemaInferenceTool()

    ambiguous_dates = [
        "01-02-2020",
        "01/02/2020",
        "03-04-2021",
    ]

    for value in ambiguous_dates:
        result = tool._parse_date(value)

        assert result["status"] == "ambiguous", (
            f"Expected ambiguous date: {value}"
        )


def test_schema_tool_identifies_unambiguous_date_formats():
    """Identify dates that have only one valid interpretation."""

    tool = SchemaInferenceTool()

    unambiguous_dates = [
        "23-07-2008",
        "09 21 1972",
        "10-29-99",
        "1995-02-10",
    ]

    for value in unambiguous_dates:
        result = tool._parse_date(value)

        assert result["status"] == "valid", (
            f"Expected unambiguous date: {value}"
        )

        assert result["parsed_date"] is not None


def test_schema_tool_rejects_impossible_calendar_dates():
    """Reject values that resemble dates but are invalid calendar dates."""

    tool = SchemaInferenceTool()

    invalid_dates = [
        "2020-02-30",
        "31-04-2020",
        "29-02-2021",
        "2020-13-10",
    ]

    for value in invalid_dates:
        result = tool._parse_date(value)

        assert result["status"] == "invalid", (
            f"Expected invalid calendar date: {value}"
        )

def test_schema_tool_reports_ambiguous_dates_separately(tmp_path):
    """Report valid, ambiguous, and invalid dates separately."""

    csv_path = tmp_path / "ambiguous_dates.csv"

    csv_path.write_text(
        "event_date\n"
        "23-07-2008\n"
        "1995-02-10\n"
        "01-02-2020\n"
        "2020-02-30\n",
        encoding="utf-8",
    )

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))

    import json

    schema_text = result.replace("Inferred schema:\n", "")
    schema = json.loads(schema_text)

    profile = schema["event_date"]

    assert profile["semantic_type"] == "date_candidate"
    assert profile["valid_values"] == 2
    assert profile["ambiguous_date_values"] == 1
    assert profile["invalid_values"] == 1

    assert profile["ambiguous_date_samples"] == ["01-02-2020"]
    assert profile["invalid_samples"] == ["2020-02-30"]

def test_schema_tool_keeps_date_fields_neutral_for_non_date_columns(
    tmp_path,
):
    """Date-specific profiling fields must not affect other columns."""

    csv_path = tmp_path / "non_date_columns.csv"

    csv_path.write_text(
        "amount,category,empty_column\n"
        "100,Food,\n"
        "200,Travel,\n"
        "300,Food,\n",
        encoding="utf-8",
    )

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))

    import json

    schema_text = result.replace("Inferred schema:\n", "")
    schema = json.loads(schema_text)

    for column in ("amount", "category", "empty_column"):
        profile = schema[column]

        assert profile["ambiguous_date_values"] == 0
        assert profile["ambiguous_date_samples"] == []

def test_schema_tool_rejects_non_finite_numeric_values(tmp_path):
    """Reject positive and negative infinity as numeric values."""

    csv_path = tmp_path / "non_finite_numbers.csv"

    pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "300",
                "Inf",
                "-Inf",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    amount = schema["amount"]

    assert amount["semantic_type"] == "numeric_candidate"
    assert amount["valid_values"] == 3
    assert amount["ambiguous_numeric_values"] == 0
    assert amount["invalid_values"] == 2
    assert amount["invalid_samples"] == ["Inf", "-Inf"]

def test_schema_tool_rejects_trailing_decimal_separator(tmp_path):
    """Reject numeric values with a trailing decimal separator."""

    csv_path = tmp_path / "trailing_decimal.csv"

    pd.DataFrame(
        {
            "score": [
                "8.5",
                "9.2",
                "7.8",
                "9.",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    score = schema["score"]

    assert score["semantic_type"] == "numeric_candidate"
    assert score["valid_values"] == 3
    assert score["ambiguous_numeric_values"] == 0
    assert score["invalid_values"] == 1
    assert score["invalid_samples"] == ["9."]

def test_schema_tool_separates_valid_ambiguous_and_invalid_numbers(
    tmp_path,
):
    """Keep all three numeric classifications separate."""

    csv_path = tmp_path / "mixed_numeric_values.csv"

    pd.DataFrame(
        {
            "amount": [
                "100",
                "250",
                "668.473",
                "invalid",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    amount = schema["amount"]

    assert amount["semantic_type"] == "numeric_candidate"
    assert amount["valid_values"] == 2
    assert amount["ambiguous_numeric_values"] == 1
    assert amount["ambiguous_numeric_samples"] == ["668.473"]
    assert amount["invalid_values"] == 1
    assert amount["invalid_samples"] == ["invalid"]

    assert (
        amount["valid_values"]
        + amount["ambiguous_numeric_values"]
        + amount["invalid_values"]
        == amount["total_records"] - amount["missing_values"]
    )

def test_schema_tool_does_not_report_numeric_ambiguity_for_text(
    tmp_path,
):
    """Do not report numeric ambiguity for text columns."""

    csv_path = tmp_path / "text_values.csv"

    pd.DataFrame(
        {
            "description": [
                "Product A",
                "Product B",
                "668.473",
                "Product C",
            ]
        }
    ).to_csv(csv_path, index=False)

    tool = SchemaInferenceTool()
    result = tool._run(file_path=str(csv_path))
    schema = json.loads(result.split("\n", 1)[1])

    description = schema["description"]

    assert description["semantic_type"] == "text_candidate"
    assert description["ambiguous_numeric_values"] == 0
    assert description["ambiguous_numeric_samples"] == []
