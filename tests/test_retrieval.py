"""Unit tests for chunking, ranking and retrieval metrics."""

from __future__ import annotations

import unittest

import numpy as np

from scripts.evaluate_retrieval import metrics_at_k
from scripts.retrieval import (
    chunk_section,
    embedding_header,
    rank_chunks,
    search_question,
)


class WhitespaceTokenizer:
    """Small tokenizer substitute used to test chunking without a model."""

    @staticmethod
    def encode(
        text: str,
        *,
        add_special_tokens: bool,
        truncation: bool,
    ) -> list[str]:
        del add_special_tokens, truncation
        return text.split()

    @staticmethod
    def decode(
        tokens: list[str],
        *,
        skip_special_tokens: bool,
        clean_up_tokenization_spaces: bool,
    ) -> str:
        del skip_special_tokens, clean_up_tokenization_spaces
        return " ".join(tokens)

    @staticmethod
    def num_special_tokens_to_add(*, pair: bool) -> int:
        del pair
        return 0


def example_section(text: str) -> dict:
    return {
        "record_id": "tec-example::article-1",
        "record_type": "article",
        "document_id": "tec-example",
        "document_title": "Reglamento de ejemplo",
        "chapter_label": "Capítulo I",
        "section_label": "Artículo 1",
        "citation_label": "Reglamento de ejemplo, Artículo 1",
        "source_url": "https://www.tec.ac.cr/example",
        "snapshot_id": "2026-07-23",
        "content_sha256": "abc123",
        "text": text,
    }


class ChunkingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tokenizer = WhitespaceTokenizer()

    def test_header_contains_legal_context_and_e5_prefix(self) -> None:
        header = embedding_header(example_section("Contenido"))
        self.assertTrue(header.startswith("passage: "))
        self.assertIn("Reglamento de ejemplo", header)
        self.assertIn("Artículo 1", header)

    def test_short_section_produces_one_traceable_chunk(self) -> None:
        chunks = chunk_section(
            example_section("cinco horas por semana"),
            self.tokenizer,
            max_input_tokens=20,
            overlap_tokens=2,
        )
        self.assertEqual(len(chunks), 1)
        self.assertEqual(
            chunks[0]["chunk_id"],
            "tec-example::article-1::chunk-001",
        )
        self.assertEqual(chunks[0]["record_id"], "tec-example::article-1")
        self.assertLessEqual(chunks[0]["token_count"], 20)

    def test_long_section_is_split_with_provenance(self) -> None:
        text = " ".join(f"palabra{number}" for number in range(30))
        chunks = chunk_section(
            example_section(text),
            self.tokenizer,
            max_input_tokens=24,
            overlap_tokens=2,
        )
        self.assertGreater(len(chunks), 1)
        self.assertTrue(
            all(
                chunk["record_id"] == "tec-example::article-1"
                for chunk in chunks
            )
        )
        self.assertTrue(
            all(chunk["token_count"] <= 24 for chunk in chunks)
        )
        self.assertEqual(
            [chunk["chunk_index"] for chunk in chunks],
            list(range(1, len(chunks) + 1)),
        )


class RankingTests(unittest.TestCase):
    def test_ranking_keeps_only_best_chunk_per_record(self) -> None:
        embeddings = np.array(
            [
                [1.0, 0.0],
                [0.9, 0.1],
                [0.0, 1.0],
                [-1.0, 0.0],
            ],
            dtype=np.float32,
        )
        chunks = [
            {
                "chunk_id": "a-1",
                "record_id": "record-a",
            },
            {
                "chunk_id": "a-2",
                "record_id": "record-a",
            },
            {
                "chunk_id": "b-1",
                "record_id": "record-b",
            },
            {
                "chunk_id": "c-1",
                "record_id": "record-c",
            },
        ]
        hits = rank_chunks(
            embeddings,
            chunks,
            np.array([1.0, 0.0], dtype=np.float32),
            top_k=3,
        )
        self.assertEqual(
            [hit["record_id"] for hit in hits],
            ["record-a", "record-b", "record-c"],
        )
        self.assertEqual(hits[0]["chunk_id"], "a-1")

    def test_search_can_keep_multiple_chunks_from_same_record(self) -> None:
        class ExampleModel:
            @staticmethod
            def encode(*args, **kwargs) -> np.ndarray:
                del args, kwargs
                return np.array([[1.0, 0.0]], dtype=np.float32)

        embeddings = np.array(
            [
                [1.0, 0.0],
                [0.9, 0.1],
                [0.0, 1.0],
            ],
            dtype=np.float32,
        )
        chunks = [
            {"chunk_id": "a-1", "record_id": "record-a"},
            {"chunk_id": "a-2", "record_id": "record-a"},
            {"chunk_id": "b-1", "record_id": "record-b"},
        ]
        hits, _ = search_question(
            ExampleModel(),
            embeddings,
            chunks,
            "pregunta",
            top_k=2,
            unique_records=False,
        )
        self.assertEqual(
            [hit["chunk_id"] for hit in hits],
            ["a-1", "a-2"],
        )


class MetricTests(unittest.TestCase):
    def test_metrics_distinguish_partial_and_complete_evidence(self) -> None:
        results = [
            {
                "answerable": True,
                "expected_record_ids": ["a"],
                "retrieved": [{"record_id": "a"}, {"record_id": "x"}],
            },
            {
                "answerable": True,
                "expected_record_ids": ["b", "c"],
                "retrieved": [{"record_id": "b"}, {"record_id": "x"}],
            },
            {
                "answerable": False,
                "expected_record_ids": [],
                "retrieved": [{"record_id": "x"}],
            },
        ]
        metrics = metrics_at_k(results, 2)
        self.assertEqual(metrics["hit_rate"], 1.0)
        self.assertEqual(metrics["complete_evidence_rate"], 0.5)
        self.assertEqual(metrics["mean_evidence_recall"], 0.75)
        self.assertEqual(metrics["mean_reciprocal_rank"], 1.0)


if __name__ == "__main__":
    unittest.main()
