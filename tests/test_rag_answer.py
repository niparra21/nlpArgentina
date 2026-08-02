"""Unit tests for RAG observation paths and citation provenance."""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scripts.rag_answer import (
    cited_source_summaries,
    default_output_path,
    filesystem_slug,
    write_record,
)


class RagArtifactTests(unittest.TestCase):
    def test_model_tag_becomes_windows_safe_directory(self) -> None:
        self.assertEqual(filesystem_slug("qwen3.5:9b"), "qwen3.5-9b")

    def test_default_output_is_grouped_by_date_and_model(self) -> None:
        path = default_output_path(
            generator_model="qwen3.5:9b",
            started_at=datetime.fromisoformat(
                "2026-07-28T10:20:30.123456-06:00"
            ),
        )
        self.assertIn("results", path.parts)
        self.assertIn("2026-07-28", path.parts)
        self.assertIn("qwen3.5-9b", path.parts)
        self.assertEqual(path.suffix, ".json")

    def test_citations_resolve_to_official_provenance(self) -> None:
        sources = [
            {
                "source_id": "F1",
                "citation_label": "Reglamento, Artículo 1",
                "source_url": "https://www.tec.ac.cr/example",
            }
        ]
        summaries = cited_source_summaries(("F1",), sources)
        self.assertEqual(
            summaries[0]["citation_label"],
            "Reglamento, Artículo 1",
        )

    def test_observation_file_is_not_silently_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            write_record(path, {"run_id": "first"})
            with self.assertRaises(FileExistsError):
                write_record(path, {"run_id": "second"})


if __name__ == "__main__":
    unittest.main()
