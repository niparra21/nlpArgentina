"""Validation tests for the TEC regulation collection inventory."""

from __future__ import annotations

import csv
import hashlib
import unittest

from scripts.collect_tec_regulations import (
    REGULATIONS,
    ROOT,
)


SNAPSHOT_ID = "2026-07-23"


class TecRegulationCollectionTests(unittest.TestCase):
    def test_collection_has_expected_size(self) -> None:
        self.assertEqual(len(REGULATIONS), 25)

    def test_inventory_identifiers_files_and_urls_are_unique(self) -> None:
        for attribute in ("document_id", "filename", "source_url"):
            values = [
                getattr(regulation, attribute)
                for regulation in REGULATIONS
            ]
            self.assertEqual(
                len(values),
                len(set(values)),
                msg=f"Duplicate {attribute}",
            )

    def test_manifest_matches_inventory(self) -> None:
        manifest_path = (
            ROOT
            / "data"
            / "raw"
            / "tec"
            / SNAPSHOT_ID
            / "manifest.csv"
        )
        with manifest_path.open(
            encoding="utf-8-sig",
            newline="",
        ) as manifest:
            rows = list(csv.DictReader(manifest))

        expected_ids = {
            regulation.document_id for regulation in REGULATIONS
        }
        self.assertEqual(
            {row["document_id"] for row in rows},
            expected_ids,
        )
        self.assertEqual(len(rows), 25)

        for row in rows:
            with self.subTest(document_id=row["document_id"]):
                self.assertEqual(row["snapshot_id"], SNAPSHOT_ID)
                self.assertEqual(row["status"], "vigente_en_sitio_oficial")
                self.assertEqual(row["http_status"], "200")
                self.assertEqual(row["content_type"], "text/html")
                self.assertTrue(row["source_url"].startswith("https://"))
                raw_path = ROOT / row["file"]
                self.assertTrue(raw_path.is_file())
                self.assertEqual(
                    hashlib.sha256(raw_path.read_bytes()).hexdigest(),
                    row["sha256"],
                )


if __name__ == "__main__":
    unittest.main()
