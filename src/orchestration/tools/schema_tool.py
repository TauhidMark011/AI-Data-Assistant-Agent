"""
Schema inference and observational data profiling.

This tool identifies physical data types, candidate semantic types,
and basic value-quality statistics without modifying source values.

Classification is based primarily on observed value patterns and
distributions rather than predefined dataset-specific column names.
"""

import json
import re
from pathlib import Path
from .missing_value_policy import missing_value_mask
from .numeric_value_policy import parse_numeric_value

import pandas as pd
from datetime import datetime
from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Semantic classification constants
# ---------------------------------------------------------

# Recognised Boolean representations.
BOOLEAN_VALUES = {
    "true",
    "false",
    "yes",
    "no",
    "y",
    "n",
    "on",
    "off",
}

# Currency symbols and ISO-style currency codes.
CURRENCY_SYMBOLS = r"[$€£₹¥]"
CURRENCY_CODES = r"(?:USD|EUR|GBP|INR|JPY|CAD|AUD)"

CURRENCY_PATTERN = re.compile(
    rf"""
    ^\s*
    (?:
        [-+]?\s*{CURRENCY_SYMBOLS}\s*
        |
        [-+]?\s*{CURRENCY_CODES}\s*
        |
        \(\s*{CURRENCY_SYMBOLS}\s*
    )
    (?:\d{{1,3}}(?:,\d{{3}})+|\d+)(?:\.\d+)?
    \s*
    (?:{CURRENCY_CODES})?
    \s*\)?\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

# Percentage values.
PERCENTAGE_PATTERN = re.compile(
    r"^[+-]?\d+(?:,\d{3})*(?:\.\d+)?\s*%$"
)

# Alphanumeric identifier patterns.
IDENTIFIER_PATTERN = re.compile(
    r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z0-9_-]+$"
)

# Recognised date structures.
DATE_PATTERNS = [
    re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$"),
    re.compile(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}$"),
    re.compile(r"^\d{1,2}\s+\d{1,2}\s+\d{4}$"),
    re.compile(r"^\d{1,2}\s+[A-Za-z]+\s+\d{4}$"),
    re.compile(r"^[A-Za-z]+\s+\d{1,2},?\s+\d{4}$"),
]

class SchemaInput(BaseModel):
    """Input contract for schema inference."""

    file_path: str = Field(..., description="Path to the CSV file")


class SchemaInferenceTool(BaseTool):
    """Infer physical schema and candidate semantic types."""

    name: str = "schema_inference_tool"
    description: str = (
        "Infers column data types, candidate semantic types, "
        "and basic data-quality statistics from a CSV file."
    )
    args_schema: type[BaseModel] = SchemaInput

    _default_path: str = str(
        Path(__file__).resolve().parents[2]
        / "data"
        / "dirty_cafe_sales.csv"
    )

    @staticmethod
    def _get_non_missing_values(series: pd.Series) -> pd.Series:
        """Return values excluded by the shared missing-value policy."""
        mask = missing_value_mask(series)
        return series.loc[~mask]

    @staticmethod
    #'ambiguous' means that a value has more than one possible meaning, making it impossible for a computer or a
    #person to know the exact number without extra context.
    def _parse_date(value: str) -> dict:
        """
        Parse supported date representations and identify ambiguity.

        Two-digit year policy:
            00-49 -> 2000-2049
            50-99 -> 1950-1999

        Returns:
            status:
                valid      - exactly one distinct date interpretation
                ambiguous  - multiple distinct date interpretations
                invalid    - no supported interpretation

            parsed_date:
                ISO date string when unambiguous; otherwise None.

            candidate_dates:
                All distinct valid date interpretations.

            matched_formats:
                Date formats that successfully matched.
        """

        value = str(value).strip()

        invalid_result = {
            "status": "invalid",
            "parsed_date": None,
            "candidate_dates": [],
            "matched_formats": [],
        }

        if not value:
            return invalid_result

        # Reject mixed separators such as 01/16-03.
        if "/" in value and "-" in value:
            return invalid_result

        # Reject repeated or malformed separators.
        compact_value = re.sub(r"\s+", "", value)

        if re.search(r"[/.-]{2}", compact_value):
            return invalid_result

        # Remove ordinal suffixes: 1st, 2nd, 3rd, 23rd, etc.
        normalized_value = re.sub(
            r"(?<=\d)(st|nd|rd|th)\b",
            "",
            value,
            flags=re.IGNORECASE,
        )

        # Normalize expressions such as "December of 1966".
        normalized_value = re.sub(
            r"\bof\b",
            " ",
            normalized_value,
            flags=re.IGNORECASE,
        )

        # Normalize spaces around date separators.
        normalized_value = re.sub(
            r"\s*([/-])\s*",
            r"\1",
            normalized_value,
        )

        normalized_value = re.sub(
            r"\s+",
            " ",
            normalized_value,
        ).strip()

        # Apply the existing two-digit numeric year policy.
        numeric_two_digit_year = re.fullmatch(
            r"(\d{1,2})-(\d{1,2})-(\d{2})",
            normalized_value,
        )

        if numeric_two_digit_year:
            first, second, year = numeric_two_digit_year.groups()

            expanded_year = (
                f"20{year}" if int(year) <= 49
                else f"19{year}"
            )

            normalized_value = (
                f"{first}-{second}-{expanded_year}"
            )

        # Apply the existing two-digit text-based year policy.
        text_two_digit_year = re.fullmatch(
            r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{2})",
            normalized_value,
        )

        if text_two_digit_year:
            day, month, year = text_two_digit_year.groups()

            expanded_year = (
                f"20{year}" if int(year) <= 49
                else f"19{year}"
            )

            normalized_value = (
                f"{day} {month} {expanded_year}"
            )

        supported_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d %m %Y",
            "%m %d %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]

        # Store each distinct interpretation and its matching formats.
        candidate_formats = {}

        for date_format in supported_formats:
            try:
                parsed_date = datetime.strptime(
                    normalized_value,
                    date_format,
                ).date()

                iso_date = parsed_date.isoformat()

                candidate_formats.setdefault(
                    iso_date,
                    [],
                ).append(date_format)

            except ValueError:
                continue

        candidate_dates = sorted(candidate_formats.keys())

        matched_formats = [
            date_format
            for formats in candidate_formats.values()
            for date_format in formats
        ]

        if not candidate_dates:
            return invalid_result

        if len(candidate_dates) > 1:
            return {
                "status": "ambiguous",
                "parsed_date": None,
                "candidate_dates": candidate_dates,
                "matched_formats": matched_formats,
            }

        return {
            "status": "valid",
            "parsed_date": candidate_dates[0],
            "candidate_dates": candidate_dates,
            "matched_formats": matched_formats,
        }

    @staticmethod
    def _is_valid_date(value: str) -> bool:
        """
        Return True only when a date has exactly one valid interpretation.

        Ambiguous dates are not treated as safely validated dates.
        """

        result = SchemaInferenceTool._parse_date(value)

        return result["status"] == "valid"

    @staticmethod
    def _is_currency(value: str) -> bool:
        """Check whether a value follows a currency representation."""

        return bool(CURRENCY_PATTERN.fullmatch(value))

    @staticmethod
    def _is_percentage(value: str) -> bool:
        """Check whether a value follows a percentage representation."""

        return bool(PERCENTAGE_PATTERN.fullmatch(value))

    @staticmethod
    def _is_identifier(value: str) -> bool:
        """Check whether a value resembles an alphanumeric identifier."""

        return bool(IDENTIFIER_PATTERN.fullmatch(value))

    @staticmethod
    def _is_boolean(value: str) -> bool:
        """Check whether a value matches a recognised Boolean token."""

        return value.lower() in BOOLEAN_VALUES

    @staticmethod
    def _calculate_ratio(
        valid_count: int,
        total_count: int,
    ) -> float:
        """Calculate the proportion of valid values."""

        if total_count == 0:
            return 0.0

        return valid_count / total_count

    def _profile_column(
        self,
        column_name: str,
        series: pd.Series,
        physical_type: str,
    ) -> dict:
        """Generate observational statistics for one column."""

        total_records = len(series)
        # Apply the shared missing-value policy.
        missing_mask = missing_value_mask(series)
        missing_values = int(missing_mask.sum())

        # Exclude only values recognised by the shared policy.
        non_missing = self._get_non_missing_values(series)

        #Use a temporary string representation for profiling.
        #The original DataFrame and source values remain unchanged.
        values = non_missing.astype(str).str.strip()

        non_missing_count = len(values)
        #Initialise numeric ambiguity tracking.
        ambiguous_numeric_count = 0

        ambiguous_numeric_mask = pd.Series(
            False,
            index=values.index,
            dtype=bool,
        )

        #Initialise the default classification.
        semantic_type = "text_candidate"

        #An empty column has no usable non-missing values.
        if non_missing_count == 0:
            semantic_type = "empty_candidate"
            valid_mask = pd.Series(
                False,
                index=values.index,
                dtype=bool,
            )

        else:
            #Boolean profiling.
            boolean_mask = values.map(self._is_boolean)
            boolean_valid_count = int(boolean_mask.sum())

            boolean_ratio = self._calculate_ratio(
                boolean_valid_count,
                non_missing_count,
            )

            #Currency profiling.
            currency_mask = values.map(self._is_currency)
            currency_valid_count = int(currency_mask.sum())

            currency_ratio = self._calculate_ratio(
                currency_valid_count,
                non_missing_count,
            )

            #Percentage profiling.
            percentage_mask = values.map(self._is_percentage)
            percentage_valid_count = int(percentage_mask.sum())

            percentage_ratio = self._calculate_ratio(
                percentage_valid_count,
                non_missing_count,
            )

            #Identifier profiling.
            identifier_mask = values.map(self._is_identifier)
            identifier_valid_count = int(identifier_mask.sum())

            identifier_ratio = self._calculate_ratio(
                identifier_valid_count,
                non_missing_count,
            )

            distinct_ratio = (
                values.nunique(dropna=True) / non_missing_count
            )

            #Date profiling.
            date_results = values.map(self._parse_date)
            date_status = date_results.map(
                lambda result: result["status"]
            )

            date_mask = date_status.eq("valid")
            ambiguous_date_mask = date_status.eq("ambiguous")

            date_valid_count = int(date_mask.sum())
            ambiguous_date_count = int(ambiguous_date_mask.sum())

            date_ratio = self._calculate_ratio(
                date_valid_count,
                non_missing_count,
            )
            #having more than one possible meaning for a date is not a valid date.
            ambiguous_date_samples = (
                values[ambiguous_date_mask]
                .head(5)
                .tolist()
            )

            #Numeric profiling.
            #First, recognise conventional numeric values.
            # Numeric profiling using the shared numeric policy.
            numeric_results = values.map(parse_numeric_value)

            numeric_status = numeric_results.map(
                lambda result: result["status"]
            )

            numeric_valid_mask = numeric_status.eq("valid")
            ambiguous_numeric_mask = numeric_status.eq("ambiguous")

            numeric_valid_count = int(
                numeric_valid_mask.sum()
            )

            ambiguous_numeric_count = int(
                ambiguous_numeric_mask.sum()
            )

            numeric_evidence_count = (
                numeric_valid_count + ambiguous_numeric_count
            )

            numeric_ratio = self._calculate_ratio(
                numeric_evidence_count,
                non_missing_count,
            )

#Classification precedence matters because some semantic types can overlap in their representations.
            if boolean_ratio >= 0.5:
                semantic_type = "boolean_candidate"
                valid_mask = boolean_mask

            elif currency_ratio >= 0.5:
                semantic_type = "currency_candidate"
                valid_mask = currency_mask

            elif percentage_ratio >= 0.5:
                semantic_type = "percentage_candidate"
                valid_mask = percentage_mask

            elif (
                identifier_ratio >= 0.8
                and distinct_ratio >= 0.8
            ):
                semantic_type = "identifier_candidate"
                valid_mask = identifier_mask

            elif date_ratio >= 0.5:
                semantic_type = "date_candidate"
                valid_mask = date_mask

            elif numeric_ratio >= 0.5:
                semantic_type = "numeric_candidate"
                valid_mask = numeric_valid_mask

            else:
                # Use observed cardinality rather than column names
                # to identify potential categorical columns.
                unique_count = values.nunique(dropna=True)

                if (
                    unique_count <= 20
                    and distinct_ratio <= 0.8
                ):
                    semantic_type = "categorical_candidate"
                else:
                    semantic_type = "text_candidate"

                # Categorical and free-text values are not invalid
                # merely because they are not numeric or date-like.
                valid_mask = pd.Series(
                    True,
                    index=values.index,
                    dtype=bool,
                )

        #Calculate valid and invalid values separately for date columns.
        if semantic_type == "date_candidate":
            valid_values = date_valid_count
            invalid_mask = date_status.eq("invalid")

        elif semantic_type == "numeric_candidate":
            valid_values = numeric_valid_count
            invalid_mask = numeric_status.eq("invalid")

        else:
            valid_values = int(valid_mask.sum())
            invalid_mask = ~valid_mask

        invalid_values = int(invalid_mask.sum())
        invalid_samples = (
            values[invalid_mask]
            .head(5)
            .tolist()
        )

        return {
            "type": physical_type,
            "nullable": missing_values > 0,
            "semantic_type": semantic_type,
            "total_records": total_records,
            "missing_values": missing_values,
            "valid_values": valid_values,
            "invalid_values": invalid_values,
            "invalid_samples": invalid_samples,
            "ambiguous_date_values": (
                ambiguous_date_count
                if semantic_type == "date_candidate"
                else 0
            ),
            "ambiguous_date_samples": (
                ambiguous_date_samples
                if semantic_type == "date_candidate"
                else []
            ),
            "ambiguous_numeric_values": (
                ambiguous_numeric_count
                if semantic_type == "numeric_candidate"
                else 0
            ),
            "ambiguous_numeric_samples": (
                values[ambiguous_numeric_mask].head(5).tolist()
                if semantic_type == "numeric_candidate"
                else []
            ),
        }

    def _run(
        self,
        file_path: str = None,
        **_: object,
    ) -> str:
        """Infer schema and profile values without changing the CSV."""

        resolved = file_path or self._default_path

        if isinstance(resolved, dict):
            resolved = resolved.get(
                "file_path",
                self._default_path,
            )

        try:
            #Read original CSV values as strings for accurate profiling.
            #This prevents Pandas from silently converting representations
            #such as "9." into 9.0 or changing "Inf" into "inf".
            raw_df = pd.read_csv(
                resolved,
                dtype=str,
                keep_default_na=False,
                na_filter=False,
                skip_blank_lines=False,
            )

            #Read separately to retain Pandas-inferred physical types.
            inferred_df = pd.read_csv(
                resolved,
                keep_default_na=False,
                skip_blank_lines=False,
            )

            #Ensure both reads have consistent columns and record counts.
            if (
                not raw_df.columns.equals(inferred_df.columns)
                or len(raw_df) != len(inferred_df)
            ):
                raise ValueError(
                    "Raw and inferred CSV data structures do not match."
                )

            schema = {
                column: self._profile_column(
                    column_name=column,
                    series=raw_df[column],
                    physical_type=str(inferred_df[column].dtype),
                )
                for column in raw_df.columns
            }

            return (
                "Inferred schema:\n"
                f"{json.dumps(schema, indent=2)}"
            )

        except Exception as exc:
            return f"Error inferring schema: {str(exc)}"