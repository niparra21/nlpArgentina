"""Integrity tests for the gold evaluation questions."""

from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data" / "evaluation" / "questions.jsonl"
SECTIONS_PATH = (
    ROOT
    / "data"
    / "processed"
    / "tec"
    / "2026-07-23"
    / "sections.jsonl"
)


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class EvaluationQuestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.questions = load_jsonl(QUESTIONS_PATH)
        cls.sections = load_jsonl(SECTIONS_PATH)
        cls.sections_by_id = {
            section["record_id"]: section for section in cls.sections
        }
        cls.corpus_document_ids = {
            section["document_id"] for section in cls.sections
        }

    def test_expected_size_and_distribution(self) -> None:
        self.assertEqual(len(self.questions), 40)
        self.assertEqual(
            Counter(q["question_type"] for q in self.questions),
            {"direct": 25, "multi_section": 8, "unanswerable": 7},
        )

    def test_question_ids_are_stable_and_unique(self) -> None:
        expected = [f"q{number:03d}" for number in range(1, 41)]
        actual = [question["question_id"] for question in self.questions]
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len(set(actual)))

    def test_direct_questions_cover_every_document_once(self) -> None:
        direct_document_ids = [
            question["document_ids"][0]
            for question in self.questions
            if question["question_type"] == "direct"
        ]
        self.assertEqual(len(direct_document_ids), 25)
        self.assertEqual(set(direct_document_ids), self.corpus_document_ids)
        self.assertTrue(
            all(count == 1 for count in Counter(direct_document_ids).values())
        )

    def test_answerable_questions_have_valid_evidence(self) -> None:
        for question in self.questions:
            if not question["answerable"]:
                continue
            with self.subTest(question_id=question["question_id"]):
                self.assertTrue(question["expected_answer"])
                self.assertTrue(question["supporting_record_ids"])
                evidence_documents = {
                    self.sections_by_id[record_id]["document_id"]
                    for record_id in question["supporting_record_ids"]
                }
                self.assertEqual(
                    evidence_documents,
                    set(question["document_ids"]),
                )

    def test_multi_section_questions_use_multiple_sections(self) -> None:
        for question in self.questions:
            if question["question_type"] != "multi_section":
                continue
            with self.subTest(question_id=question["question_id"]):
                self.assertGreaterEqual(
                    len(question["supporting_record_ids"]),
                    2,
                )

    def test_unanswerable_questions_have_no_evidence(self) -> None:
        for question in self.questions:
            if question["question_type"] != "unanswerable":
                continue
            with self.subTest(question_id=question["question_id"]):
                self.assertFalse(question["answerable"])
                self.assertEqual(question["supporting_record_ids"], [])
                self.assertEqual(question["document_ids"], [])
                self.assertEqual(
                    question["expected_answer"],
                    "La información no se encuentra en el corpus.",
                )

    def test_questions_and_answers_are_unique(self) -> None:
        prompts = [q["question"].casefold() for q in self.questions]
        self.assertEqual(len(prompts), len(set(prompts)))
        for question in self.questions:
            with self.subTest(question_id=question["question_id"]):
                self.assertTrue(question["question"].endswith("?"))
                self.assertNotIn("<", question["question"])
                self.assertNotIn("<", question["expected_answer"])


if __name__ == "__main__":
    unittest.main()
