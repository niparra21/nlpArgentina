"""Integrity tests for the generated retrieval baseline artifacts."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from scripts.retrieval import load_index, read_jsonl, sha256_file


ROOT = Path(__file__).resolve().parents[1]
INDEX_DIR = (
    ROOT
    / "data"
    / "indexes"
    / "tec"
    / "2026-07-23"
    / "multilingual-e5-small"
)
RESULTS_DIR = (
    ROOT
    / "results"
    / "retrieval"
    / "2026-07-23"
    / "multilingual-e5-small"
)
QUESTIONS_PATH = ROOT / "data" / "evaluation" / "questions.jsonl"


class RetrievalArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.embeddings, cls.chunks, cls.manifest = load_index(INDEX_DIR)
        cls.results = read_jsonl(RESULTS_DIR / "evaluation.jsonl")
        cls.summary = json.loads(
            (RESULTS_DIR / "summary.json").read_text(encoding="utf-8")
        )

    def test_index_shape_and_normalization(self) -> None:
        self.assertEqual(self.embeddings.shape, (1259, 384))
        self.assertEqual(self.embeddings.dtype, np.float32)
        norms = np.linalg.norm(self.embeddings, axis=1)
        self.assertTrue(np.allclose(norms, 1.0, atol=1e-5))

    def test_chunk_counts_limits_and_identifiers(self) -> None:
        self.assertEqual(self.manifest["source_records"], 1184)
        self.assertEqual(self.manifest["chunks"], 1259)
        self.assertEqual(self.manifest["split_records"], 51)
        chunk_ids = [chunk["chunk_id"] for chunk in self.chunks]
        self.assertEqual(len(chunk_ids), len(set(chunk_ids)))
        self.assertTrue(
            all(
                chunk["token_count"]
                <= self.manifest["max_input_tokens"]
                for chunk in self.chunks
            )
        )
        self.assertTrue(
            all(
                chunk["embedding_text"].startswith("passage: ")
                for chunk in self.chunks
            )
        )

    def test_evaluation_is_complete_and_traceable(self) -> None:
        self.assertEqual(len(self.results), 40)
        self.assertEqual(
            [result["question_id"] for result in self.results],
            [f"q{number:03d}" for number in range(1, 41)],
        )
        for result in self.results:
            with self.subTest(question_id=result["question_id"]):
                self.assertEqual(len(result["retrieved"]), 5)
                record_ids = [
                    hit["record_id"] for hit in result["retrieved"]
                ]
                self.assertEqual(len(record_ids), len(set(record_ids)))
                self.assertGreater(result["latency_ms"], 0)

    def test_summary_references_exact_inputs(self) -> None:
        self.assertEqual(
            self.summary["questions_sha256"],
            sha256_file(QUESTIONS_PATH),
        )
        self.assertEqual(
            self.summary["index_manifest_sha256"],
            sha256_file(INDEX_DIR / "index_manifest.json"),
        )
        self.assertEqual(self.summary["questions"], 40)
        self.assertEqual(self.summary["answerable_questions"], 33)
        self.assertEqual(self.summary["unanswerable_questions"], 7)

    def test_baseline_reaches_documented_minimum(self) -> None:
        metrics = self.summary["metrics"]["at_5"]
        self.assertGreaterEqual(metrics["hit_rate"], 0.90)
        self.assertGreaterEqual(
            metrics["complete_evidence_rate"],
            0.80,
        )
        self.assertGreaterEqual(metrics["mean_reciprocal_rank"], 0.75)


if __name__ == "__main__":
    unittest.main()
