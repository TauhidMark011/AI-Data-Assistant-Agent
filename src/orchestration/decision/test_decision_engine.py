#D:\DataAssistant_AI-Agent\src\orchestration\decision\test_decision_engine.py

"""
Phase 4B — Step 3A
Deterministic test suite for the Decision & Recommendation Engine.

Purpose:
- Verify deterministic decision behavior.
- Verify severity and priority assignment.
- Verify HITL requirements.
- Verify evidence preservation.
- Verify that the engine never modifies the dataset.
- Verify that the engine never uses an LLM.

The Decision Engine must be tested independently from CrewAI,
Gemini, Streamlit, and remediation logic.
"""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2]

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from orchestration.decision.decision_engine import DecisionEngine

def test_missing_dirty_values_requires_review() -> None:
    """Missing/dirty values must produce a high-priority review."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 10,
            "duplicate_records": 0,
        },
        "missing_dirty_matrix": {
            "Item": 6,
            "Location": 4,
        },
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    recommendation = result["recommendations"][0]

    assert recommendation["issue_type"] == "MISSING_DIRTY_VALUES"
    assert recommendation["severity"] == "HIGH"
    assert recommendation["priority"] == 1
    assert recommendation["action"] == "REVIEW_REQUIRED"
    assert recommendation["human_approval_required"] is True

    assert recommendation["evidence"]["total_count"] == 10
    assert recommendation["evidence"]["by_column"] == {
        "Item": 6,
        "Location": 4,
    }


def test_duplicate_records_requires_review() -> None:
    """Duplicate records must produce a medium-priority review."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 0,
            "duplicate_records": 5,
        },
        "missing_dirty_matrix": {},
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    recommendation = result["recommendations"][0]

    assert recommendation["issue_type"] == "DUPLICATE_RECORDS"
    assert recommendation["severity"] == "MEDIUM"
    assert recommendation["priority"] == 2
    assert recommendation["action"] == "REVIEW_REQUIRED"
    assert recommendation["human_approval_required"] is True

    assert recommendation["evidence"]["duplicate_records"] == 5


def test_logic_breaches_require_high_priority_review() -> None:
    """Logic breaches must be treated as high-priority review items."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 0,
            "duplicate_records": 0,
        },
        "missing_dirty_matrix": {},
        "logic_breaches": {
            "Quantity * Price Per Unit == Total Spent": 3,
        },
        "numerical_outliers": {},
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    recommendation = result["recommendations"][0]

    assert recommendation["issue_type"] == "LOGIC_BREACH"
    assert recommendation["severity"] == "HIGH"
    assert recommendation["priority"] == 1
    assert recommendation["action"] == "REVIEW_REQUIRED"
    assert recommendation["human_approval_required"] is True

    assert recommendation["evidence"]["total_breaches"] == 3


def test_numerical_outliers_require_review() -> None:
    """Numerical outliers must produce a medium-priority review."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 0,
            "duplicate_records": 0,
        },
        "missing_dirty_matrix": {},
        "logic_breaches": {},
        "numerical_outliers": {
            "Total Spent": 259,
        },
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    recommendation = result["recommendations"][0]

    assert recommendation["issue_type"] == "NUMERICAL_OUTLIERS"
    assert recommendation["severity"] == "MEDIUM"
    assert recommendation["priority"] == 2
    assert recommendation["action"] == "REVIEW_REQUIRED"
    assert recommendation["human_approval_required"] is True

    assert recommendation["evidence"]["total_outliers"] == 259


def test_clean_dataset_requires_no_action() -> None:
    """Clean deterministic evidence must produce NO_ACTION."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 0,
            "duplicate_records": 0,
        },
        "missing_dirty_matrix": {},
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["issue_type"] == "NO_ACTION_REQUIRED"
    assert recommendation["severity"] == "LOW"
    assert recommendation["priority"] == 3
    assert recommendation["action"] == "NO_ACTION"
    assert recommendation["human_approval_required"] is False

    assert result["summary"]["review_required"] == 0


def test_multiple_quality_issues_are_preserved() -> None:
    """Multiple evidence categories must produce separate recommendations."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 12,
            "duplicate_records": 4,
        },
        "missing_dirty_matrix": {
            "Item": 8,
            "Location": 4,
        },
        "logic_breaches": {
            "Quantity * Price Per Unit == Total Spent": 2,
        },
        "numerical_outliers": {
            "Total Spent": 5,
        },
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    recommendations = result["recommendations"]

    assert len(recommendations) == 4

    issue_types = {
        item["issue_type"]
        for item in recommendations
    }

    assert issue_types == {
        "MISSING_DIRTY_VALUES",
        "DUPLICATE_RECORDS",
        "LOGIC_BREACH",
        "NUMERICAL_OUTLIERS",
    }

    assert result["summary"]["total_recommendations"] == 4
    assert result["summary"]["review_required"] == 4


def test_recommendations_are_human_approval_gated() -> None:
    """The Decision Engine must never auto-apply remediation."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 20,
            "duplicate_records": 10,
        },
        "missing_dirty_matrix": {
            "Item": 20,
        },
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    assert result["human_in_the_loop"]["enabled"] is True
    assert result["human_in_the_loop"]["approval_required"] is True

    assert result["human_in_the_loop"]["approved_recommendations"] == []
    assert result["human_in_the_loop"]["rejected_recommendations"] == []

    for recommendation in result["recommendations"]:
        assert recommendation["action"] == "REVIEW_REQUIRED"
        assert recommendation["human_approval_required"] is True


def test_source_evidence_is_preserved() -> None:
    """Original deterministic evidence must remain available for auditing."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 7,
            "duplicate_records": 2,
        },
        "missing_dirty_matrix": {
            "Item": 7,
        },
        "logic_breaches": {},
        "numerical_outliers": {
            "Total Spent": 3,
        },
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    assert result["source_evidence"] == evidence


def test_decision_engine_is_deterministic() -> None:
    """Identical evidence must always produce identical decisions."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 7,
            "duplicate_records": 2,
        },
        "missing_dirty_matrix": {
            "Item": 7,
        },
        "logic_breaches": {
            "Quantity * Price Per Unit == Total Spent": 2,
        },
        "numerical_outliers": {
            "Total Spent": 3,
        },
    }

    engine = DecisionEngine()

    first_result = engine.evaluate(evidence)
    second_result = engine.evaluate(evidence)

    assert first_result == second_result


def test_decision_engine_does_not_modify_evidence() -> None:
    """Decision evaluation must not mutate the supplied evidence."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 5,
            "duplicate_records": 1,
        },
        "missing_dirty_matrix": {
            "Item": 5,
        },
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    original_evidence = {
        "summary": {
            "total_missing_dirty_values": 5,
            "duplicate_records": 1,
        },
        "missing_dirty_matrix": {
            "Item": 5,
        },
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    engine = DecisionEngine()
    engine.evaluate(evidence)

    assert evidence == original_evidence


def test_decision_engine_metadata_is_correct() -> None:
    """Verify the architectural guarantees of Phase 4B."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 0,
            "duplicate_records": 0,
        },
        "missing_dirty_matrix": {},
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    engine = DecisionEngine()
    result = engine.evaluate(evidence)

    metadata = result["decision_engine"]

    assert metadata["version"] == "1.0"
    assert metadata["mode"] == "DETERMINISTIC"
    assert metadata["llm_used"] is False
    assert metadata["dataset_modified"] is False

def test_critical_system_failure_must_not_produce_no_action() -> None:
    """A critical analysis failure must never be treated as a clean dataset."""

    import pytest

    evidence = {
        "critical_system_failure": "Quality analysis failed: test failure"
    }

    engine = DecisionEngine()

    with pytest.raises(ValueError, match="(?i)critical"):
        engine.evaluate(evidence)


def test_every_recommendation_has_a_unique_non_empty_id() -> None:
    """Every generated recommendation must have a unique ID."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 10,
            "duplicate_records": 5,
        },
        "missing_dirty_matrix": {"Item": 10},
        "logic_breaches": {"Quantity * Price == Total": 2},
        "numerical_outliers": {"Amount": 3},
    }

    result = DecisionEngine().evaluate(evidence)
    recommendations = result["recommendations"]

    recommendation_ids = [
        item["recommendation_id"]
        for item in recommendations
    ]

    assert all(
        isinstance(item, str) and item.strip()
        for item in recommendation_ids
    )
    assert len(recommendation_ids) == len(set(recommendation_ids))


def test_recommendation_ids_are_deterministic() -> None:
    """Identical evidence must produce identical recommendation IDs."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 10,
            "duplicate_records": 5,
        },
        "missing_dirty_matrix": {"Item": 10},
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    engine = DecisionEngine()

    first_result = engine.evaluate(evidence)
    second_result = engine.evaluate(evidence)

    first_ids = [
        item["recommendation_id"]
        for item in first_result["recommendations"]
    ]
    second_ids = [
        item["recommendation_id"]
        for item in second_result["recommendations"]
    ]

    assert first_ids == second_ids


def test_recommendation_id_matches_issue_type() -> None:
    """Recommendation IDs must follow the canonical naming convention."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 10,
            "duplicate_records": 5,
        },
        "missing_dirty_matrix": {"Item": 10},
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    result = DecisionEngine().evaluate(evidence)

    for recommendation in result["recommendations"]:
        expected_id = f"REC-{recommendation['issue_type']}"

        assert recommendation["recommendation_id"] == expected_id


def test_no_action_recommendation_has_stable_id() -> None:
    """NO_ACTION_REQUIRED must also have a recommendation ID."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 0,
            "duplicate_records": 0,
        },
        "missing_dirty_matrix": {},
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    result = DecisionEngine().evaluate(evidence)

    recommendation = result["recommendations"][0]

    assert recommendation["issue_type"] == "NO_ACTION_REQUIRED"
    assert (
        recommendation["recommendation_id"]
        == "REC-NO_ACTION_REQUIRED"
    )
    assert recommendation["human_approval_required"] is False
