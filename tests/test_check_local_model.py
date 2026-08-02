"""Unit tests for the local Ollama smoke-test helpers."""

from __future__ import annotations

import unittest

from scripts.check_local_model import (
    SMOKE_CASES,
    answer_is_valid,
    result_summary,
)
from scripts.ollama_client import installed_model_names


class LocalModelSmokeTestHelpers(unittest.TestCase):
    def test_installed_model_names_ignores_incomplete_entries(self) -> None:
        response = {
            "models": [
                {"name": "qwen3.5:9b"},
                {"model": "without-name"},
            ]
        }
        self.assertEqual(installed_model_names(response), {"qwen3.5:9b"})

    def test_evidence_answer_requires_content_and_citation(self) -> None:
        evidence_case = SMOKE_CASES[0]
        self.assertTrue(
            answer_is_valid(
                evidence_case,
                "Abre de 8:00 a 16:00 [F1].",
            )
        )
        self.assertFalse(
            answer_is_valid(
                evidence_case,
                "Abre de 8:00 a 16:00.",
            )
        )

    def test_abstention_answer_is_exact(self) -> None:
        abstention_case = SMOKE_CASES[1]
        self.assertTrue(
            answer_is_valid(
                abstention_case,
                "No encontrado en el contexto.",
            )
        )
        self.assertFalse(
            answer_is_valid(abstention_case, "No lo sé.")
        )

    def test_result_summary_calculates_tokens_per_second(self) -> None:
        response = {
            "message": {
                "content": "Abre de 8:00 a 16:00 [F1].",
            },
            "total_duration": 2_000_000_000,
            "load_duration": 500_000_000,
            "prompt_eval_count": 100,
            "eval_count": 20,
            "eval_duration": 400_000_000,
        }
        summary = result_summary(SMOKE_CASES[0], response)
        self.assertTrue(summary["passed"])
        self.assertEqual(summary["total_seconds"], 2.0)
        self.assertEqual(summary["tokens_per_second"], 50.0)


if __name__ == "__main__":
    unittest.main()
