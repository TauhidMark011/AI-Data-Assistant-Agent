
"""Regression tests for CSV upload parsing."""

from src.api.upload_service import parse_and_normalize_csv


def test_parse_and_normalize_csv_preserves_blank_records():
    """Verify that blank CSV records are not silently discarded."""

    content = (
        b"name,value\n"
        b"A,100\n"
        b"\n"
        b"B,200\n"
    )

    df, normalized_content = parse_and_normalize_csv(content)

    assert len(df) == 3

    assert df.iloc[0].tolist() == ["A", "100"]
    assert df.iloc[1].tolist() == ["", ""]
    assert df.iloc[2].tolist() == ["B", "200"]

    assert isinstance(normalized_content, bytes)