"""Validation tests for the TEC regulation processor."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from scripts.process_tec_regulations import (
    ROOT,
    load_sources,
    parse_document,
    process_snapshot,
)


SNAPSHOT_DATE = "2026-07-23"


class TecRegulationProcessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = load_sources(SNAPSHOT_DATE)
        cls.records, cls.stats = process_snapshot(SNAPSHOT_DATE)
        cls.by_id = {
            record["record_id"]: record for record in cls.records
        }

    def test_expected_counts(self) -> None:
        self.assertEqual(self.stats["records"], 251)
        self.assertEqual(self.stats["articles"], 244)
        self.assertEqual(self.stats["transitories"], 7)

    def test_known_article_keeps_context(self) -> None:
        article = self.by_id["tec-rrea-2025::article-66"]
        self.assertEqual(article["chapter_number"], "VI")
        self.assertEqual(article["chapter_title"], "Sobre la evaluación")
        self.assertEqual(
            article["article_title"],
            "De las ausencias justificadas a actividades de evaluación",
        )
        self.assertIn("tres días hábiles", article["text"])

    def test_bis_identifiers_are_normalized(self) -> None:
        self.assertIn(
            "tec-becas-prestamos::article-6-bis-1", self.by_id
        )
        self.assertIn(
            "tec-equiparacion-asignaturas::article-15-bis", self.by_id
        )

    def test_split_chapter_heading_is_reconstructed(self) -> None:
        article = self.by_id["tec-defensoria-estudiantil::article-6"]
        self.assertEqual(article["chapter_number"], "II")
        self.assertEqual(
            article["chapter_title"],
            "DE LA NATURALEZA Y ORGANIZACIÓN DE LA DEFENSORIA",
        )

    def test_every_record_is_traceable_and_plain_text(self) -> None:
        for record in self.records:
            with self.subTest(record_id=record["record_id"]):
                raw_path = ROOT / record["raw_file"]
                self.assertTrue(raw_path.is_file())
                self.assertEqual(record["snapshot_date"], SNAPSHOT_DATE)
                self.assertTrue(record["source_url"].startswith("https://"))
                self.assertNotIn("<p", record["text"].casefold())
                self.assertNotIn("<h", record["text"].casefold())

    def test_raw_hashes_remain_valid(self) -> None:
        for source in self.sources:
            with self.subTest(document_id=source.document_id):
                content = (ROOT / source.raw_file).read_bytes()
                self.assertEqual(
                    hashlib.sha256(content).hexdigest(),
                    source.raw_sha256,
                )

    def test_generated_output_matches_processing_manifest(self) -> None:
        output_dir = (
            ROOT / "data" / "processed" / "tec" / SNAPSHOT_DATE
        )
        sections_path = output_dir / "sections.jsonl"
        manifest_path = output_dir / "processing_manifest.json"
        self.assertTrue(sections_path.is_file())
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(
            hashlib.sha256(sections_path.read_bytes()).hexdigest(),
            manifest["output_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
