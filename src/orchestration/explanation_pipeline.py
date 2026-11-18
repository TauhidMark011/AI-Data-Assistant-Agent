
"""Grounded explanation pipeline for deterministic data-quality findings.

This module validates deterministic recommendations, retrieves supporting
knowledge, and generates one validated explanation.

It does not analyse or modify datasets and does not make decisions.
"""

from src.rag.context_builder import build_grounded_context
from src.rag.generation import generate_explanation


def build_generation_findings(decision_result: dict) -> dict:
    """Validate and preserve the original Decision Engine result."""

    if not isinstance(decision_result, dict):
        raise TypeError("decision_result must be a dictionary.")

    recommendations = decision_result.get("recommendations")

    if not isinstance(recommendations, list) or not recommendations:
        raise ValueError(
            "decision_result must contain a non-empty recommendations list."
        )

    seen_ids = set()

    for index, item in enumerate(recommendations):
        if not isinstance(item, dict):
            raise ValueError(
                f"Recommendation at index {index} must be a dictionary."
            )

        recommendation_id = item.get("recommendation_id")
        issue_type = item.get("issue_type")
        approval_required = item.get("human_approval_required")
        recommendation = item.get("recommendation")

        if not isinstance(recommendation_id, str) or not recommendation_id.strip():
            raise ValueError(
                f"Recommendation at index {index} has an invalid recommendation_id."
            )

        if recommendation_id in seen_ids:
            raise ValueError(
                f"Duplicate recommendation_id: {recommendation_id}"
            )

        seen_ids.add(recommendation_id)

        if not isinstance(issue_type, str) or not issue_type.strip():
            raise ValueError(
                f"Recommendation at index {index} has an invalid issue_type."
            )

        if not isinstance(approval_required, bool):
            raise ValueError(
                f"Recommendation at index {index} has an invalid "
                "human_approval_required value."
            )

        if not isinstance(recommendation, str) or not recommendation.strip():
            raise ValueError(
                f"Recommendation at index {index} has an invalid recommendation."
            )

    # Preserve the canonical Decision Engine contract.
    # Do not rename fields or construct a lossy adapter.
    return decision_result


def run_explanation_pipeline(
    decision_result: dict,
    top_k: int = 3,
) -> dict:
    """Retrieve grounded knowledge and generate one validated explanation."""

    generation_findings = build_generation_findings(decision_result)

    issue_types = [
        item["issue_type"]
        for item in generation_findings["recommendations"]
    ]

    query = (
        "Explain the data-quality findings and recommended actions for "
        f"these issue types: {', '.join(issue_types)}. "
        "Use the relevant data-quality guidance and explain when "
        "human review or approval is required."
    )

    grounded_context = build_grounded_context(
        query=query,
        top_k=top_k,
    )

    # Fail closed if retrieval cannot provide usable knowledge.
    # This avoids silently generating an explanation without grounding.
    if (
        grounded_context.get("status") != "ok"
        or not grounded_context.get("sources")
        or not isinstance(grounded_context.get("context_text"), str)
        or not grounded_context["context_text"].strip()
    ):
        raise RuntimeError(
            "Grounded explanation stopped: no usable RAG context was returned."
        )

    # The only generation call in this module.
    explanation = generate_explanation(
        deterministic_findings=generation_findings,
        grounded_context=grounded_context,
    )

    return {
        "generation_findings": generation_findings,
        "grounded_context": grounded_context,
        "explanation": explanation,
        "generation_calls_requested": 1,
    }
