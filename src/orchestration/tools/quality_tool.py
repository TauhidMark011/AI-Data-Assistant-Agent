"""
Deterministic Data Quality Tool.

Responsibilities:
    - Detect missing values using the shared missing-value policy.
    - Detect invalid values in potential numeric columns.
    - Detect exact duplicate records.
    - Detect date-like columns.
    - Detect numerical relationship breaches.
    - Detect numerical outliers using the IQR method.
    - Produce evidence-only JSON.

Important:
    - Python is the source of truth.
    - This tool does not use an LLM.
    - Original dataset values are never modified.
"""

import json
from itertools import permutations
from pathlib import Path
from typing import Optional

import pandas as pd
from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

from .missing_value_policy import missing_value_mask
from .numeric_value_policy import parse_numeric_value
from .numeric_analysis_policy import (
    assess_float64_eligibility,
)

class QualityInput(BaseModel):
    """Input schema for the quality-check tool."""

    file_path: Optional[str] = Field(
        default=None,
        description="Path to the CSV file",
    )


class QualityCheckTool(BaseTool):
    """
    Deterministic data-quality analysis tool.

    Python performs all calculations and produces the evidence.
    """

    name: str = "quality_check_tool"

    description: str = (
        "Deterministic data-quality analysis tool. "
        "Detects missing values, invalid numeric values, duplicates, "
        "numerical relationship breaches, and statistical outliers."
    )

    args_schema: type[BaseModel] = QualityInput

    _default_path: str = str(
        Path(__file__).resolve().parents[2]
        / "data"
        / "dirty_cafe_sales.csv"
    )

    def _run(
        self,
        file_path: Optional[str] = None,
        **_: object,
    ) -> str:
        """
        Load the dataset and perform deterministic analysis.

        keep_default_na=False prevents Pandas from silently applying
        its own default NA-token list. Missing-value classification
        is delegated to the shared policy instead.
        """

        resolved_path = self._resolve_path(file_path)

        try:
            df = pd.read_csv(
                 resolved_path,
                 low_memory=False,
                 keep_default_na=False,
                 skip_blank_lines=False,
            )

            return self._analyse(
                df=df,
                resolved_path=resolved_path,
            )

        except Exception as exc:
            return json.dumps(
                {
                    "critical_system_failure": str(exc),
                }
            )

    def _resolve_path(
        self,
        file_path: Optional[str],
    ) -> str:
        """
        Normalize the path supplied by CrewAI.

        Supports:
            - None
            - Normal string path
            - JSON string containing file_path
            - Dictionary containing file_path
        """

        if not file_path:
            return self._default_path

        if isinstance(file_path, str):
            stripped_path = file_path.strip()

            if stripped_path.startswith("{"):
                try:
                    parsed = json.loads(stripped_path)

                    if isinstance(parsed, dict):
                        return str(
                            parsed.get(
                                "file_path",
                                self._default_path,
                            )
                        )

                except json.JSONDecodeError:
                    pass

            return stripped_path

        if isinstance(file_path, dict):
            return str(
                file_path.get(
                    "file_path",
                    self._default_path,
                )
            )

        return str(file_path)

    def _analyse(
        self,
        df: pd.DataFrame,
        resolved_path: str,
    ) -> str:
        """Generate deterministic data-quality evidence."""

        total_rows = len(df)

        # ============================================================
        # 1. SHARED MISSING-VALUE DETECTION
        # ============================================================

        # Apply the same missing-value policy to every column.
        # The returned masks do not modify the original DataFrame.
        missing_masks = {
            column: missing_value_mask(df[column])
            for column in df.columns
        }

        missing_value_matrix = {
            column: int(mask.sum())
            for column, mask in missing_masks.items()
        }

        total_missing_values = sum(
            missing_value_matrix.values()
        )

        # ============================================================
        # 2. DATE DETECTION
        # ============================================================

        date_columns = []

        for column in df.select_dtypes(
            include=["object", "string"]
        ).columns:

            # Exclude recognised missing values before date parsing.
            sample = (
                df.loc[
                    ~missing_masks[column],
                    column,
                ]
                .head(10)
            )

            if sample.empty:
                continue

            try:
                pd.to_datetime(
                    sample,
                    format="mixed",
                    errors="raise",
                )

                date_columns.append(column)

            except (ValueError, TypeError, OverflowError):
                continue

        # ============================================================
        # 3. NUMERICAL COLUMN DETECTION
        # ============================================================
        potential_numeric_columns = []
        numeric_df = pd.DataFrame(index=range(total_rows))

        invalid_numeric_matrix = {}
        invalid_numeric_masks = {}
        invalid_numeric_samples = {}

        ambiguous_numeric_matrix = {}
        ambiguous_numeric_samples = {}
        restricted_numeric_matrix = {}
        restricted_numeric_samples = {}

        for column in df.columns:

            analysis_values = []
            invalid_values = []
            ambiguous_values = []
            restricted_values = []

            invalid_positions = []
            ambiguous_count = 0

            column_values = df[column].tolist()
            missing_values = missing_masks[column].tolist()

            for position, (value, is_missing) in enumerate(
                zip(column_values, missing_values)
            ):
                if is_missing:
                    analysis_values.append(float("nan"))
                    continue
                result = parse_numeric_value(value)

                if result["status"] == "valid":
                    eligibility = assess_float64_eligibility(
                        result["parsed_value"]
                    )
                    if eligibility["status"] == "eligible":
                        analysis_values.append(
                            eligibility["float_value"]
                        )
                    else:
                        analysis_values.append(float("nan"))
                        restricted_values.append(str(value))

                elif result["status"] == "ambiguous":
                    analysis_values.append(float("nan"))
                    ambiguous_values.append(str(value))
                    ambiguous_count += 1
                else:
                    analysis_values.append(float("nan"))
                    invalid_values.append(str(value))
                    invalid_positions.append(position)

            numeric_valid_count = (
                len(column_values)
                - sum(missing_values)
                - len(invalid_values)
                - ambiguous_count
            )

            # Retain the existing 40% numeric-candidate threshold.
            if (
                numeric_valid_count + ambiguous_count
                > total_rows * 0.4
            ):

                potential_numeric_columns.append(column)

                numeric_df[column] = pd.Series(
                    analysis_values,
                    index=range(total_rows),
                    dtype="float64",
                    )

                invalid_mask = pd.Series(
                    False,
                    index=range(total_rows),
                )

                if invalid_positions:
                    invalid_mask.iloc[invalid_positions] = True

                invalid_numeric_masks[column] = invalid_mask

                invalid_numeric_matrix[column] = len(
                    invalid_values
                )

                invalid_numeric_samples[column] = (
                    invalid_values[:5]
                )

                ambiguous_numeric_matrix[column] = (
                    ambiguous_count
                )

                ambiguous_numeric_samples[column] = (
                    ambiguous_values[:5]
                )

                restricted_numeric_matrix[column] = len(
                    restricted_values
                )

                restricted_numeric_samples[column] = (
                    restricted_values[:5]
                )

        total_invalid_numeric_values = sum(
            invalid_numeric_matrix.values()
        )

        # ============================================================
        # 4. NUMERICAL RELATIONSHIP CHECK
        # ============================================================

        logic_breaches = {}

        # Check possible multiplication relationships:
        #
        #     A * B == C
        #     B * A == C
        #
        # Sorting the operand pair prevents duplicate checks.

        checked_relationships = set()

        if len(potential_numeric_columns) >= 3:

            for first, second, target in permutations(
                potential_numeric_columns,
                3,
            ):

                operand_pair = tuple(
                    sorted([first, second])
                )

                relationship_key = (
                    f"{operand_pair[0]} * "
                    f"{operand_pair[1]} == {target}"
                )

                if relationship_key in checked_relationships:
                    continue

                checked_relationships.add(
                    relationship_key
                )

                difference = (
                    numeric_df[operand_pair[0]]
                    * numeric_df[operand_pair[1]]
                    - numeric_df[target]
                ).abs()

                match_mask = difference < 0.01

                valid_rows = (
                    numeric_df[operand_pair[0]].notna()
                    & numeric_df[operand_pair[1]].notna()
                    & numeric_df[target].notna()
                )

                valid_match_mask = (
                    match_mask & valid_rows
                )

                valid_row_count = int(
                    valid_rows.sum()
                )

                if valid_row_count == 0:
                    continue

                match_rate = (
                    valid_match_mask.sum()
                    / valid_row_count
                )

                if 0.60 < match_rate < 1.0:

                    error_count = int(
                        (
                            ~match_mask
                            & valid_rows
                        ).sum()
                    )

                    logic_breaches[
                        relationship_key
                    ] = error_count

        # ============================================================
        # 5. DUPLICATE RECORDS
        # ============================================================

        duplicate_records = int(
            df.duplicated().sum()
        )

        # ============================================================
        # 6. NUMERICAL OUTLIERS
        # ============================================================

        numerical_outliers = {}

        outlier_method = {
            "method": "IQR",
            "multiplier": 1.5,
            "columns": {},
        }

        for column in numeric_df.columns:

            series = numeric_df[column].dropna()

            if series.empty:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            iqr = q3 - q1

            lower_bound = q1 - (1.5 * iqr)
            upper_bound = q3 + (1.5 * iqr)

            outlier_mask = (
                (numeric_df[column] < lower_bound)
                | (numeric_df[column] > upper_bound)
            )

            outlier_count = int(
                outlier_mask.sum()
            )

            if outlier_count > 0:

                numerical_outliers[column] = (
                    outlier_count
                )

                outlier_method["columns"][
                    column
                ] = outlier_count

        # ============================================================
        # 7. ERROR SAMPLE INDICES
        # ============================================================

        # A row is included when it contains either:
        #   - A recognised missing value
        #   - An invalid value in a potential numeric column
        #
        # ERROR and UNKNOWN are not automatically missing.
        # They may still be invalid in a numeric candidate column.

        row_issue_mask = pd.Series(
            False,
            index=df.index,
        )

        for mask in missing_masks.values():
            row_issue_mask |= mask

        for mask in invalid_numeric_masks.values():
            # Align masks explicitly to prevent index mismatch issues
            # between df.index and range(total_rows) if df was filtered.
            row_issue_mask |= mask.values

        error_sample_indices = (
            df.index[row_issue_mask]
            .tolist()[:5]
        )

        # ============================================================
        # 8. EVIDENCE-LOCKED REPORT
        # ============================================================

        report = {
            "summary": {
                "total_records": total_rows,
                "duplicate_records": duplicate_records,
                "total_missing_values": total_missing_values,
                "total_invalid_numeric_values": (
                    total_invalid_numeric_values
                ),

                # Temporary backward-compatible field.
                # It now represents missing values only.
                "total_missing_dirty_values": (
                    total_missing_values
                ),
            },

            "dates_detected": date_columns,

            "missing_value_matrix": (
                missing_value_matrix
            ),

            # Temporary backward-compatible alias.
            # New consumers should use missing_value_matrix.
            "missing_dirty_matrix": (
                missing_value_matrix
            ),

            "invalid_numeric_matrix": (
                invalid_numeric_matrix
            ),

            "invalid_numeric_samples": (
                invalid_numeric_samples
            ),

            "ambiguous_numeric_matrix": (
                ambiguous_numeric_matrix
            ),

            "ambiguous_numeric_samples": (
                ambiguous_numeric_samples
            ),

            "restricted_numeric_matrix": (
                restricted_numeric_matrix
            ),

            "restricted_numeric_samples": (
                restricted_numeric_samples
            ),

            "logic_breaches": logic_breaches,

            "numerical_outliers": numerical_outliers,

            "outlier_detection": outlier_method,

            "error_sample_indices": (
                error_sample_indices
            ),
        }

        return json.dumps(
            report,
            indent=2,
        )