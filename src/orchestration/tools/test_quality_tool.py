
"""Regression tests for the deterministic Quality Check Tool."""

import json

import pandas as pd
from pandas.testing import assert_frame_equal

from src.orchestration.tools.missing_value_policy import (
    missing_value_mask,
)
from src.orchestration.tools.quality_tool import (
    QualityCheckTool,
)


def test_shared_policy_identifies_only_configured_missing_values():
    """Only explicitly configured representations count as missing."""

    series = pd.Series(
        [
            None,
            "",
            "   ",
            "NaN",
            " NULL ",
            "none",
            "n/a",
            "ERROR",
            "UNKNOWN",
            "Not Applicable",
            "-",
        ]
    )

    actual = missing_value_mask(series).tolist()

    expected = [
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        False,
    ]

    assert actual == expected


def test_quality_tool_separates_missing_and_invalid_numeric_values():
    """Missing tokens and invalid numeric values must be counted separately."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "300",
                "400",
                "500",
                "",
                "NaN",
                "ERROR",
                "UNKNOWN",
                "Not Applicable",
                "-",
            ]
        }
    )

    tool = QualityCheckTool()

    result = tool._analyse(
        df=df,
        resolved_path="test_dataset.csv",
    )

    report = json.loads(result)

    assert report["summary"]["total_records"] == 11

    assert (
        report["summary"]["total_missing_values"]
        == 2
    )

    assert (
        report["summary"]["total_invalid_numeric_values"]
        == 4
    )

    assert report["missing_value_matrix"]["amount"] == 2

    assert report["invalid_numeric_matrix"]["amount"] == 4


def test_error_and_unknown_are_not_classified_as_missing():
    """ERROR and UNKNOWN remain present values under the default policy."""

    df = pd.DataFrame(
        {
            "status": [
                "ERROR",
                "UNKNOWN",
                "Not Applicable",
                "-",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["summary"]["total_missing_values"] == 0

    assert report["missing_value_matrix"]["status"] == 0


def test_quality_tool_does_not_modify_original_dataframe():
    """Quality analysis must never alter the original dataset."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "",
                "ERROR",
                "UNKNOWN",
            ],
            "category": [
                "A",
                "B",
                "C",
                "D",
                "E",
            ],
        }
    )

    original_df = df.copy(deep=True)

    tool = QualityCheckTool()

    tool._analyse(
        df=df,
        resolved_path="test_dataset.csv",
    )

    assert_frame_equal(df, original_df)


def test_quality_tool_reads_csv_using_shared_missing_policy(tmp_path):
    """CSV loading must not silently apply Pandas' default NA-token rules."""

    csv_path = tmp_path / "missing_policy_test.csv"

    df = pd.DataFrame(
        {
            "status": [
                "UNKNOWN",
                "ERROR",
                "NULL",
                "",
            ]
        }
    )

    df.to_csv(csv_path, index=False)

    tool = QualityCheckTool()

    result = tool._run(
        file_path=str(csv_path)
    )

    report = json.loads(result)

    assert report["summary"]["total_records"] == 4

    assert report["summary"]["total_missing_values"] == 2

    assert report["missing_value_matrix"]["status"] == 2

def test_quality_tool_uses_shared_numeric_policy():
    """Numeric profiling must follow the shared interpretation policy."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "2.278.845",
                "668.473",
                "9,.0",
                "",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["summary"]["total_records"] == 6

    assert report["missing_value_matrix"]["amount"] == 1

    assert report["invalid_numeric_matrix"]["amount"] == 1

    assert report["ambiguous_numeric_matrix"]["amount"] == 1

    assert report["ambiguous_numeric_samples"]["amount"] == [
        "668.473"
    ]

    assert report["invalid_numeric_samples"]["amount"] == [
        "9,.0"
    ]

def test_quality_tool_separates_ambiguous_numeric_values():
    """Ambiguous values must be reported separately from invalid values."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "300",
                "668.473",
                "12.345",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["ambiguous_numeric_matrix"]["amount"] == 2

    assert report["invalid_numeric_matrix"]["amount"] == 0

    assert report["ambiguous_numeric_samples"]["amount"] == [
        "668.473",
        "12.345",
    ]

def test_quality_tool_reports_original_invalid_numeric_samples():
    """Invalid samples must retain their original representations."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "300",
                "9,.0",
                "8,9f",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["invalid_numeric_matrix"]["amount"] == 2

    assert report["invalid_numeric_samples"]["amount"] == [
        "9,.0",
        "8,9f",
    ]

    assert report["ambiguous_numeric_matrix"]["amount"] == 0

def test_quality_tool_handles_duplicate_dataframe_indexes():
    """Numeric classification must work with duplicate DataFrame indexes."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "2.278.845",
                "9,.0",
                "200",
            ]
        },
        index=[0, 0, 1, 1],
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["invalid_numeric_matrix"]["amount"] == 1

    assert report["invalid_numeric_samples"]["amount"] == [
        "9,.0"
    ]

def test_quality_tool_excludes_ambiguous_values_from_relationship_checks():
    """Ambiguous values must not participate in numeric relationships."""

    df = pd.DataFrame(
        {
            "quantity": [
                "2",
                "3",
                "4",
                "5",
                "6",
            ],
            "price": [
                "10",
                "10",
                "10",
                "10",
                "10",
            ],
            "total": [
                "20",
                "30",
                "40",
                "50",
                "668.473",
            ],
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["ambiguous_numeric_matrix"]["total"] == 1

    assert report["invalid_numeric_matrix"]["total"] == 0

    assert "quantity * price == total" not in (
        report["logic_breaches"]
    )

def test_quality_tool_excludes_ambiguous_values_from_iqr_outlier_detection():
    """Ambiguous values must not affect IQR outlier calculations."""

    df = pd.DataFrame(
        {
            "amount": [
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "668.473",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["ambiguous_numeric_matrix"]["amount"] == 1

    assert report["invalid_numeric_matrix"]["amount"] == 0

    assert "amount" not in report["numerical_outliers"]

    assert "amount" not in report["outlier_detection"]["columns"]

def test_quality_tool_separates_valid_but_precision_restricted_values():
    """Valid numeric values restricted from float64 analysis remain valid."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "300",
                "123456789.123456789",
                "9007199254740993",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["invalid_numeric_matrix"]["amount"] == 0

    assert report["ambiguous_numeric_matrix"]["amount"] == 0

    assert report["restricted_numeric_matrix"]["amount"] == 2

    assert report["restricted_numeric_samples"]["amount"] == [
        "123456789.123456789",
        "9007199254740993",
    ]

def test_quality_tool_keeps_exactly_representable_large_integers_eligible():
    """Exactly representable large integers remain eligible for analysis."""

    df = pd.DataFrame(
        {
            "amount": [
                "100",
                "200",
                "300",
                "9007199254740992",
                "9007199254740994",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["invalid_numeric_matrix"]["amount"] == 0
    assert report["ambiguous_numeric_matrix"]["amount"] == 0
    assert report["restricted_numeric_matrix"]["amount"] == 0

def test_quality_tool_excludes_precision_restricted_values_from_relationship_checks():
    """Precision-restricted values must not participate in numeric relationships."""

    df = pd.DataFrame(
        {
            "quantity": [
                "2",
                "3",
                "4",
                "5",
                "6",
            ],
            "price": [
                "10",
                "10",
                "10",
                "10",
                "10",
            ],
            "total": [
                "20",
                "30",
                "40",
                "50",
                "9007199254740993",
            ],
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["restricted_numeric_matrix"]["total"] == 1

    assert report["invalid_numeric_matrix"]["total"] == 0

    assert report["ambiguous_numeric_matrix"]["total"] == 0

    assert "quantity * price == total" not in (
        report["logic_breaches"]
    )

def test_quality_tool_excludes_precision_restricted_values_from_iqr():
    """Precision-restricted values must not affect IQR outlier calculations."""

    df = pd.DataFrame(
        {
            "amount": [
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "9007199254740993",
            ]
        }
    )

    tool = QualityCheckTool()

    report = json.loads(
        tool._analyse(
            df=df,
            resolved_path="test_dataset.csv",
        )
    )

    assert report["restricted_numeric_matrix"]["amount"] == 1

    assert report["invalid_numeric_matrix"]["amount"] == 0

    assert report["ambiguous_numeric_matrix"]["amount"] == 0

    assert "amount" not in report["numerical_outliers"]

    assert "amount" not in report["outlier_detection"]["columns"]