import unittest
from unittest.mock import patch

from src.rag.context_builder import build_grounded_context


class TestContextLimit(unittest.TestCase):

    @patch("src.rag.context_builder.retrieve_relevant_nodes")
    def test_context_does_not_exceed_maximum(self, mock_retrieve):
        mock_retrieve.return_value = {
            "ids": [["test-record-1"]],
            "documents": [["X" * 500]],
            "metadatas": [[{
                "source_path": "test/test.md",
                "category": "test",
            }]],
            "distances": [[0.1]],
        }

        result = build_grounded_context(
            query="Test context limit",
            top_k=1,
            max_context_chars=100,
            max_chunk_chars=500,
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["evidence_count"], 1)
        self.assertLessEqual(result["context_characters"], 100)
        self.assertLessEqual(len(result["context_text"]), 100)
        mock_retrieve.assert_called_once()

    @patch("src.rag.context_builder.retrieve_relevant_nodes")
    def test_empty_retrieval_returns_no_results(self, mock_retrieve):
        mock_retrieve.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }

        result = build_grounded_context(
            query="Test empty retrieval",
            top_k=1,
        )

        self.assertEqual(result["status"], "no_results")
        self.assertEqual(result["evidence_count"], 0)
        self.assertEqual(result["context_text"], "")
        mock_retrieve.assert_called_once()

    def test_empty_query_is_rejected(self):
        with self.assertRaises(ValueError):
            build_grounded_context(query="")

    def test_zero_context_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            build_grounded_context(
                query="Test query",
                max_context_chars=0,
            )


if __name__ == "__main__":
    unittest.main()
