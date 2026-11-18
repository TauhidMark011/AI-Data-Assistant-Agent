
"""
Unit tests for the Gemini generation layer.

All tests use a fake Gemini client.
No real Gemini API requests are made.
"""

import json
import unittest

from src.orchestration.decision.decision_engine import DecisionEngine
from src.rag.generation import generate_explanation

class FakeResponse:
    """Simulate a Gemini API response."""

    def __init__(self, text):
        self.text = text


class FakeModels:
    """Simulate the Gemini models API."""

    def __init__(self, response_text):
        self.response_text = response_text
        self.call_count = 0
        self.last_prompt = None
        self.last_model = None

    def generate_content(self, model, contents, config):
        self.call_count += 1
        self.last_prompt = contents
        self.last_model = model
        return FakeResponse(self.response_text)


class FakeClient:
    """Provide a fake client for generation tests."""

    def __init__(self, response_text):
        self.models = FakeModels(response_text)

def valid_response(recommendation_ids):
    """Return a valid simulated Gemini response."""

    return {
        "summary": "The supplied findings need review.",
        "recommendation_explanations": [
            {
                "recommendation_id": recommendation_id,
                "explanation": (
                    "The deterministic findings identify an issue "
                    "that requires investigation."
                ),
                "supporting_sources": [
                    "remediation/remediation_guidance.md"
                ],
                "limitations": (
                    "The correct remediation cannot be established "
                    "from the available evidence alone."
                ),
            }
            for recommendation_id in recommendation_ids
        ],
        "human_review_required": True,
        "safety_note": (
            "This explanation is not approval or execution of remediation."
        ),
    }

class TestGeminiGeneration(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "summary": {
                "total_missing_dirty_values": 10,
                "duplicate_records": 0,
                },
                "missing_dirty_matrix": {
                    "Item": 10,
              },
              "logic_breaches": {},
              "numerical_outliers": {},
            }
        self.findings = DecisionEngine().evaluate(self.evidence)
        self.recommendation_ids = [
            item["recommendation_id"]
            for item in self.findings["recommendations"]
        ]

        self.context = {
            "status": "ok",
            "sources": [
                "remediation/remediation_guidance.md"
            ],
            "context_text": (
                "Missing values should not be replaced arbitrarily. "
                "Review the field meaning and approved business rules."
            ),
        }

    def test_valid_response_and_single_api_call(self):
        client = FakeClient(
            json.dumps(valid_response(self.recommendation_ids))
        )

        result = generate_explanation(
            deterministic_findings=self.findings,
            grounded_context=self.context,
            client=client,
            model_name="test-model",
        )

        self.assertEqual(
            result["summary"],
            "The supplied findings need review.",
        )
        self.assertTrue(result["human_review_required"])
        self.assertEqual(client.models.call_count, 1)
        self.assertEqual(client.models.last_model, "test-model")
        self.assertIn(
            "MISSING_DIRTY_VALUES",
            client.models.last_prompt,
        )
        self.assertIn(
            "remediation/remediation_guidance.md",
            client.models.last_prompt,
        )

    def test_empty_findings_fail_before_api_call(self):
        client = FakeClient(
            json.dumps(valid_response(self.recommendation_ids))
        )

        with self.assertRaisesRegex(ValueError, "must not be empty"):
            generate_explanation(
                deterministic_findings={},
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 0)

    def test_empty_context_is_allowed(self):
        response = valid_response(self.recommendation_ids)
        response["recommendation_explanations"][0]["supporting_sources"] = []

        client = FakeClient(json.dumps(response))
        empty_context = {
            "sources": [],
            "context_text": "",
        }

        result = generate_explanation(
            deterministic_findings=self.findings,
            grounded_context=empty_context,
            client=client,
        )

        self.assertEqual(
            result["summary"],
            "The supplied findings need review.",
        )
        self.assertEqual(client.models.call_count, 1)
        self.assertIn(
            "[No retrieved knowledge available.]",
            client.models.last_prompt,
        )

    def test_invalid_json_is_rejected(self):
        client = FakeClient("This is not JSON")

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            generate_explanation(
                deterministic_findings=self.findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 1)

    def test_missing_required_field_is_rejected(self):
        response = valid_response(self.recommendation_ids)
        del response["safety_note"]
        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(
            ValueError,
            "missing required fields",
        ):
            generate_explanation(
                deterministic_findings=self.findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 1)

    def test_invalid_boolean_type_is_rejected(self):
        response = valid_response(self.recommendation_ids)
        response["human_review_required"] = "yes"
        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(
            ValueError,
            "must be a boolean",
        ):
            generate_explanation(
                deterministic_findings=self.findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 1)

    def test_review_requirement_cannot_be_weakened(self):
        response = valid_response(self.recommendation_ids)
        response["human_review_required"] = False
        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(ValueError, "contradicts"):
            generate_explanation(
                deterministic_findings=self.findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 1)

    def test_unknown_recommendation_reference_is_rejected(self):
        response = valid_response(self.recommendation_ids)
        response["recommendation_explanations"][0]["recommendation_id"] = (
            "INVENTED-REC"
        )
        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(
            ValueError,
            "unknown recommendation IDs",
        ):
            generate_explanation(
                deterministic_findings=self.findings,
                grounded_context=self.context,
                client=client,
            )

    def test_unknown_source_path_is_rejected(self):
        response = valid_response(self.recommendation_ids)
        response["recommendation_explanations"][0]["supporting_sources"] = [
            "governance/fake_policy.md"
        ]
        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(ValueError, "unknown sources"):
            generate_explanation(
                deterministic_findings=self.findings,
                grounded_context=self.context,
                client=client,
            )


    def test_missing_approval_flag_is_rejected_before_api_call(self):
        findings = DecisionEngine().evaluate(self.evidence)

        del findings["recommendations"][0]["human_approval_required"]

        client = FakeClient(
            json.dumps(valid_response(self.recommendation_ids))
        )

        with self.assertRaisesRegex(
            ValueError,
            "must have a Boolean human_approval_required",
        ):
            generate_explanation(
                deterministic_findings=findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 0)

    def test_non_boolean_deterministic_review_status_is_rejected(self):
        findings = DecisionEngine().evaluate(self.evidence)

        findings["recommendations"][0]["human_approval_required"] = "yes"

        client = FakeClient(
            json.dumps(valid_response(self.recommendation_ids))
        )

        with self.assertRaisesRegex(
            ValueError,
            "must have a Boolean human_approval_required",
        ):
            generate_explanation(
                deterministic_findings=findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 0)

    def test_prompt_restricts_unsupported_dataset_wide_claims(self):
        client = FakeClient(
            json.dumps(valid_response(self.recommendation_ids))
        )

        generate_explanation(
            deterministic_findings=self.findings,
            grounded_context=self.context,
            client=client,
            model_name="test-model",
        )

        self.assertIn(
            "Do not claim that the entire dataset was analysed",
            client.models.last_prompt,
        )
        self.assertIn(
            "Do not present a test example or sample finding",
            client.models.last_prompt,
        )

    def test_summary_can_describe_supplied_findings_without_overclaiming(self):
        response = valid_response(self.recommendation_ids)
        response["summary"] = (
            "The supplied findings identify missing values that need review."
        )

        client = FakeClient(json.dumps(response))

        result = generate_explanation(
            deterministic_findings=self.findings,
            grounded_context=self.context,
            client=client,
            model_name="test-model",
        )

        self.assertEqual(
            result["summary"],
            "The supplied findings identify missing values that need review.",
        )

    def test_missing_recommendation_explanation_is_rejected(self):
        findings = DecisionEngine().evaluate({
            "summary": {
                "total_missing_dirty_values": 10,
                "duplicate_records": 5,
            },
            "missing_dirty_matrix": {"Item": 10},
            "logic_breaches": {},
            "numerical_outliers": {},
        })

        recommendations = findings["recommendations"]

        response = valid_response([
            recommendations[0]["recommendation_id"]
        ])

        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(
            ValueError,
            "missing recommendations",
        ):
            generate_explanation(
                deterministic_findings=findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 1)

    def test_duplicate_recommendation_explanation_is_rejected(self):
        findings = DecisionEngine().evaluate({
            "summary": {
                "total_missing_dirty_values": 10,
                "duplicate_records": 5,
            },
            "missing_dirty_matrix": {"Item": 10},
            "logic_breaches": {},
            "numerical_outliers": {},
        })

        recommendations = findings["recommendations"]
        first_id = recommendations[0]["recommendation_id"]

        response = valid_response([
            first_id,
            first_id,
        ])

        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(
            ValueError,
            "Duplicate recommendation_id",
        ):
            generate_explanation(
                deterministic_findings=findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 1)

    def test_empty_recommendation_explanation_is_rejected(self):
        response = valid_response(self.recommendation_ids)
        response["recommendation_explanations"][0]["explanation"] = "   "

        client = FakeClient(json.dumps(response))

        with self.assertRaisesRegex(
            ValueError,
            "non-empty string",
        ):
            generate_explanation(
                deterministic_findings=self.findings,
                grounded_context=self.context,
                client=client,
            )

        self.assertEqual(client.models.call_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
