"""Unit tests for complete-RAG evaluation metrics and artifacts."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.evaluate_rag import (
    generation_gold_metrics,
    lexical_overlap,
    normalized_tokens,
    prepare_output_dir,
    retrieval_gold_metrics,
    summarize_records,
)
from scripts.generation import GroundedAnswer


def example_question(*, answerable: bool = True) -> dict:
    return {
        "question_id": "q-example",
        "question": "¿Cuál es el plazo?",
        "question_type": "direct" if answerable else "unanswerable",
        "category": "evaluación" if answerable else "fuera_del_corpus",
        "answerable": answerable,
        "expected_answer": (
            "El plazo es de tres días hábiles."
            if answerable
            else "La información no se encuentra en el corpus."
        ),
        "supporting_record_ids": ["record-a"] if answerable else [],
        "document_ids": ["document-a"] if answerable else [],
    }


def example_sources() -> list[dict]:
    return [
        {
            "source_id": "F1",
            "record_id": "record-a",
            "citation_label": "Reglamento, Artículo 1",
            "source_url": "https://www.tec.ac.cr/example",
        },
        {
            "source_id": "F2",
            "record_id": "record-b",
            "citation_label": "Reglamento, Artículo 2",
            "source_url": "https://www.tec.ac.cr/example",
        },
    ]


class LexicalMetricTests(unittest.TestCase):
    def test_normalization_removes_accents_and_citation_tokens(self) -> None:
        self.assertEqual(
            normalized_tokens("Tres días hábiles [F2]."),
            ["tres", "dias", "habiles"],
        )

    def test_identical_words_have_full_overlap(self) -> None:
        metrics = lexical_overlap(
            "Tres días hábiles.",
            "Tres días hábiles [F1].",
        )
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["f1"], 1.0)


class GoldMetricTests(unittest.TestCase):
    def test_retrieval_detects_expected_record(self) -> None:
        metrics = retrieval_gold_metrics(
            example_question(),
            example_sources(),
        )
        self.assertTrue(metrics["retrieval_hit"])
        self.assertTrue(metrics["retrieval_complete_evidence"])
        self.assertEqual(metrics["retrieval_evidence_recall"], 1.0)

    def test_generation_resolves_citation_to_gold_record(self) -> None:
        metrics = generation_gold_metrics(
            example_question(),
            GroundedAnswer(
                status="answered",
                answer="El plazo es de tres días hábiles [F1].",
                citations=("F1",),
            ),
            example_sources(),
        )
        self.assertTrue(metrics["status_correct"])
        self.assertTrue(metrics["citation_hit"])
        self.assertTrue(metrics["citation_complete_expected_evidence"])
        self.assertEqual(metrics["citation_precision_against_gold"], 1.0)

    def test_unanswerable_status_is_scored_without_citation_metrics(
        self,
    ) -> None:
        metrics = generation_gold_metrics(
            example_question(answerable=False),
            GroundedAnswer(
                status="not_found",
                answer="No encontrado en el contexto.",
                citations=(),
            ),
            example_sources(),
        )
        self.assertTrue(metrics["status_correct"])
        self.assertIsNone(metrics["citation_hit"])
        self.assertIsNone(metrics["lexical_overlap"])


class SummaryTests(unittest.TestCase):
    @staticmethod
    def record(
        *,
        answerable: bool,
        status_correct: bool,
        citation_hit: bool | None,
    ) -> dict:
        question = example_question(answerable=answerable)
        return {
            "gold": {
                "answerable": answerable,
                "question_type": question["question_type"],
                "category": question["category"],
            },
            "retrieval": {"search_ms": 10.0},
            "generation": {
                "request_latency_ms": 1000.0,
                "tokens_per_second": 50.0,
            },
            "result": {
                "status": (
                    "answered"
                    if answerable
                    else "not_found"
                )
            },
            "evaluation": {
                "status_correct": status_correct,
                "retrieval_hit": True if answerable else None,
                "retrieval_complete_evidence": (
                    True if answerable else None
                ),
                "retrieval_evidence_recall": (
                    1.0 if answerable else None
                ),
                "citation_hit": citation_hit,
                "citation_complete_expected_evidence": citation_hit,
                "citation_precision_against_gold": (
                    1.0 if citation_hit else 0.0
                )
                if answerable
                else None,
                "citation_evidence_recall": (
                    1.0 if citation_hit else 0.0
                )
                if answerable
                else None,
                "lexical_overlap": (
                    {"precision": 1.0, "recall": 1.0, "f1": 1.0}
                    if answerable
                    else None
                ),
            },
            "error": None,
            "question_total_ms": 1100.0,
        }

    def test_summary_separates_answerable_and_unanswerable(self) -> None:
        summary = summarize_records(
            [
                self.record(
                    answerable=True,
                    status_correct=True,
                    citation_hit=True,
                ),
                self.record(
                    answerable=False,
                    status_correct=True,
                    citation_hit=None,
                ),
            ]
        )
        self.assertEqual(summary["questions"], 2)
        self.assertEqual(summary["metrics"]["status_accuracy"], 1.0)
        self.assertEqual(summary["metrics"]["citation_hit_rate"], 1.0)
        self.assertEqual(
            summary["metrics"]["unanswerable_abstention_rate"],
            1.0,
        )


class OutputDirectoryTests(unittest.TestCase):
    def test_existing_artifact_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            artifact = output_dir / "summary.json"
            artifact.write_text("old", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                prepare_output_dir(output_dir, force=False)
            prepare_output_dir(output_dir, force=True)
            self.assertFalse(artifact.exists())


if __name__ == "__main__":
    unittest.main()
