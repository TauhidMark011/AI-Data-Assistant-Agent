
"""One controlled live Gemini generation test.

This test:
1. Creates controlled deterministic evidence.
2. Runs the actual Decision Engine.
3. Sends its recommendations to Gemini.
4. Validates the generated explanation.
5. Does not run RAG retrieval or modify a dataset.

This script makes one real Gemini API request.
"""

from src.orchestration.decision.decision_engine import DecisionEngine
from src.rag.generation import generate_explanation


def main():
    # 1. Create controlled evidence using the Decision Engine contract.
    evidence = {
        "summary": {
            "total_missing_dirty_values": 3,
            "duplicate_records": 0,
        },
        "missing_dirty_matrix": {
            "Customer_Name": 3,
        },
        "logic_breaches": {},
        "numerical_outliers": {},
    }

    # 2. Generate recommendations deterministically.
    decision_result = DecisionEngine().evaluate(evidence)

    if decision_result["decision_engine"]["llm_used"]:
        raise RuntimeError(
            "Decision Engine must not use an LLM."
        )

    if decision_result["decision_engine"]["dataset_modified"]:
        raise RuntimeError(
            "Decision Engine must not modify a dataset."
        )

    recommendations = decision_result["recommendations"]

    if not recommendations:
        raise RuntimeError(
            "Decision Engine returned no recommendations."
        )

    # 3. Supply controlled reference context.
    # This test does not execute RAG retrieval.
    grounded_context = {
        "status": "ok",
        "sources": [
            "remediation/remediation_guidance.md"
        ],
        "context_text": (
            "Missing values should not be replaced arbitrarily. "
            "The appropriate action depends on the field meaning "
            "and approved business rules. Human review is required "
            "before consequential remediation."
        ),
    }

    # 4. Make one real Gemini generation request.
    result = generate_explanation(
        deterministic_findings=decision_result,
        grounded_context=grounded_context,
    )

    # 5. Validate recommendation coverage.
    expected_ids = {
        item["recommendation_id"]
        for item in recommendations
    }

    actual_ids = [
        item["recommendation_id"]
        for item in result["recommendation_explanations"]
    ]

    if len(actual_ids) != len(set(actual_ids)):
        raise AssertionError(
            "Gemini returned duplicate recommendation explanations."
        )

    if set(actual_ids) != expected_ids:
        raise AssertionError(
            "Gemini explanation coverage does not match "
            "the deterministic recommendations."
        )

    expected_review = any(
        item["human_approval_required"]
        for item in recommendations
    )

    if result["human_review_required"] != expected_review:
        raise AssertionError(
            "Gemini changed the deterministic human-review requirement."
        )

    # 6. Display the validated result.
    print("=" * 70)
    print("LIVE GEMINI GENERATION TEST: PASS")
    print("=" * 70)

    print("\nDeterministic recommendations:")

    for item in recommendations:
        print(
            f"- {item['recommendation_id']}: "
            f"{item['issue_type']}"
        )

    print("\nGenerated summary:")
    print(result["summary"])

    for index, item in enumerate(
        result["recommendation_explanations"],
        start=1,
    ):
        print(f"\nExplanation {index}")
        print(f"Recommendation ID: {item['recommendation_id']}")
        print(f"Explanation: {item['explanation']}")
        print(f"Supporting sources: {item['supporting_sources']}")
        print(f"Limitations: {item['limitations']}")

    print(
        "\nHuman review required:",
        result["human_review_required"],
    )

    print("\nSafety note:")
    print(result["safety_note"])

    print("\nDataset modified: False")
    print("Gemini generation requests: 1")


if __name__ == "__main__":
    main()
