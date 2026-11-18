
"""
Integration test for the deterministic data-quality, RAG, and Gemini pipeline.

This test:
1. Creates a temporary CSV.
2. Runs deterministic quality analysis.
3. Generates deterministic recommendations.
4. Calls the reusable RAG + Gemini explanation pipeline.
5. Validates the explanation and confirms the CSV was not modified.
"""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import pytest

import pandas as pd

from src.orchestration.tools.quality_tool import QualityCheckTool
from src.orchestration.decision.decision_engine import DecisionEngine
from src.orchestration.explanation_pipeline import (
    run_explanation_pipeline,
)


class TestPipelineIntegration(unittest.TestCase):

    @pytest.mark.live
    def test_deterministic_rag_gemini_pipeline(self):
        # 1. Create a controlled test dataset.
        test_df = pd.DataFrame(
            {
                "Order_ID": ["A001", "A002", "A003", "A004", "A005"],
                "Quantity": [2, 3, 1, 4, 2],
                "Unit_Price": [10.0, 20.0, 15.0, 12.0, 10.0],
                "Total_Spent": [20.0, 60.0, 15.0, 48.0, 20.0],
                "Payment_Method": [
                    "Cash",
                    "Card",
                    "None",
                    "Cash",
                    "Card",
                ],
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "integration_test.csv"
            test_df.to_csv(csv_path, index=False)

            original_hash = hashlib.sha256(
                csv_path.read_bytes()
            ).hexdigest()

            # 2. Run deterministic quality analysis.
            quality_tool = QualityCheckTool()
            evidence_text = quality_tool._run(
                file_path=str(csv_path)
            )
            evidence = json.loads(evidence_text)

            self.assertNotIn(
                "critical_system_failure",
                evidence,
                msg=f"Quality tool failed: {evidence}",
            )

            self.assertGreater(
                evidence["summary"]["total_missing_dirty_values"],
                0,
            )

            # 3. Generate deterministic recommendations.
            decision_result = DecisionEngine().evaluate(evidence)

            self.assertFalse(
                decision_result["decision_engine"]["llm_used"]
            )
            self.assertFalse(
                decision_result["decision_engine"]["dataset_modified"]
            )
            self.assertTrue(decision_result["recommendations"])

            # 4. Run the reusable RAG + Gemini explanation pipeline.
            pipeline_result = run_explanation_pipeline(
                decision_result=decision_result,
                top_k=3,
            )

            generation_findings = pipeline_result["generation_findings"]
            grounded_context = pipeline_result["grounded_context"]
            result = pipeline_result["explanation"]

            self.assertEqual(
                pipeline_result["generation_calls_requested"],
                1,
            )

            self.assertEqual(
                grounded_context["status"],
                "ok",
                msg="RAG retrieval returned no usable evidence.",
            )
            self.assertTrue(grounded_context["sources"])
            self.assertTrue(grounded_context["context_text"].strip())

            # 5. Validate the generated explanation.
            self.assertIsInstance(result, dict)
            self.assertIsInstance(result["summary"], str)
            self.assertTrue(result["summary"].strip())

            expected_review = any(
                item["human_approval_required"]
                for item in generation_findings["recommendations"]
            )

            self.assertEqual(
                result["human_review_required"],
                expected_review,
            )

            allowed_sources = set(grounded_context["sources"])
            allowed_references = {
                item["recommendation_id"]
                for item in generation_findings["recommendations"]
            }

            for explanation in result["recommendation_explanations"]:
                self.assertIn(
                    explanation["recommendation_id"],
                    allowed_references,
                )
                self.assertTrue(
                    set(explanation["supporting_sources"]).issubset(
                        allowed_sources
                    )
                )

            actual_references = [
                item["recommendation_id"]
                for item in result["recommendation_explanations"]
            ]

            self.assertCountEqual(
                actual_references,
                allowed_references,
                msg="Every deterministic recommendation must have exactly one explanation.",
            )

            # 6. Confirm the original CSV bytes are unchanged.
            final_hash = hashlib.sha256(
                csv_path.read_bytes()
            ).hexdigest()

            self.assertEqual(
                original_hash,
                final_hash,
                msg="The pipeline modified the test CSV.",
            )

            print("\nPIPELINE INTEGRATION TEST: PASS")
            print(
                "Deterministic recommendations:",
                len(decision_result["recommendations"]),
            )
            print("RAG sources:", grounded_context["sources"])
            print(
                "Human review required:",
                result["human_review_required"],
            )
            print("Dataset modified: False")


if __name__ == "__main__":
    unittest.main(verbosity=2)