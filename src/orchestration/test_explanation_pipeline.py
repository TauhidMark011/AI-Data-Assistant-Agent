
"""Unit tests for the grounded explanation pipeline."""

from copy import deepcopy
from unittest.mock import patch

import pytest

from src.orchestration.decision.decision_engine import DecisionEngine
from src.orchestration.explanation_pipeline import (
    build_generation_findings,
    run_explanation_pipeline,
)


@pytest.fixture
def decision_result():
    """Create valid recommendations using the real Decision Engine."""

    evidence = {
        "summary": {
            "total_missing_dirty_values": 3,
            "total_duplicate_records": 0,
            "total_logic_breaches": 0,
            "total_numerical_outliers": 0,
        },
        "missing_dirty_values": {
            "count": 3,
            "columns": ["Customer_Name"],
        },
        "duplicate_records": {"count": 0},
        "logic_breaches": {"count": 0},
        "numerical_outliers": {"count": 0},
    }

    return DecisionEngine().evaluate(evidence)


def test_original_decision_result_is_preserved(decision_result):
    result = build_generation_findings(decision_result)

    assert result is decision_result
    assert result["recommendations"] == decision_result["recommendations"]


def test_recommendation_fields_are_not_renamed(decision_result):
    result = build_generation_findings(decision_result)

    for recommendation in result["recommendations"]:
        assert "recommendation_id" in recommendation
        assert "human_approval_required" in recommendation
        assert "recommendation" in recommendation

        assert "review_required" not in recommendation
        assert "recommended_action" not in recommendation


def test_missing_recommendation_id_is_rejected(decision_result):
    decision_result["recommendations"][0].pop("recommendation_id")

    with pytest.raises(ValueError, match="recommendation_id"):
        build_generation_findings(decision_result)


def test_duplicate_recommendation_ids_are_rejected(decision_result):
    recommendations = decision_result["recommendations"]

    if len(recommendations) < 2:
        pytest.skip("Decision Engine returned fewer than two recommendations.")

    recommendations[1]["recommendation_id"] = (
        recommendations[0]["recommendation_id"]
    )

    with pytest.raises(ValueError, match="Duplicate recommendation_id"):
        build_generation_findings(decision_result)


def test_invalid_approval_flag_is_rejected(decision_result):
    decision_result["recommendations"][0][
        "human_approval_required"
    ] = "True"

    with pytest.raises(ValueError, match="human_approval_required"):
        build_generation_findings(decision_result)


def test_invalid_decision_result_is_rejected():
    with pytest.raises(TypeError):
        build_generation_findings(None)


def test_empty_recommendations_are_rejected():
    with pytest.raises(ValueError, match="non-empty recommendations"):
        build_generation_findings({"recommendations": []})


def test_pipeline_passes_original_decision_result_to_generation(
    decision_result,
):
    original_result = deepcopy(decision_result)

    grounded_context = {
        "status": "ok",
        "sources": ["remediation/remediation_guidance.md"],
        "context_text": "Relevant remediation guidance.",
    }

    expected_explanation = {
        "summary": "Explanation generated successfully.",
        "recommendation_explanations": [],
        "human_review_required": True,
        "safety_note": "Human approval is required.",
    }

    with (
        patch(
            "src.orchestration.explanation_pipeline.build_grounded_context",
            return_value=grounded_context,
        ),
        patch(
            "src.orchestration.explanation_pipeline.generate_explanation",
            return_value=expected_explanation,
        ) as mock_generation,
    ):
        result = run_explanation_pipeline(
            decision_result=decision_result,
            top_k=3,
        )

    assert mock_generation.call_count == 1

    actual_findings = mock_generation.call_args.kwargs[
        "deterministic_findings"
    ]

    assert actual_findings is decision_result
    assert result["generation_findings"] is decision_result
    assert result["explanation"] == expected_explanation
    assert result["generation_calls_requested"] == 1
    assert decision_result == original_result


def test_pipeline_stops_when_rag_context_is_unavailable(decision_result):
    with (
        patch(
            "src.orchestration.explanation_pipeline.build_grounded_context",
            return_value={
                "status": "empty",
                "sources": [],
                "context_text": "",
            },
        ),
        patch(
            "src.orchestration.explanation_pipeline.generate_explanation",
        ) as mock_generation,
    ):
        with pytest.raises(RuntimeError, match="no usable RAG context"):
            run_explanation_pipeline(decision_result)

    mock_generation.assert_not_called()
