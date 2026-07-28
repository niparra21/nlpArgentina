"""Unit tests for prompt construction and grounded-answer validation."""

from __future__ import annotations

import json
import unittest

from scripts.generation import (
    GenerationValidationError,
    answer_schema,
    build_messages,
    format_context,
    generation_metrics,
    generate_grounded_answer,
    parse_grounded_answer,
    prepare_sources,
)


def example_hit(rank: int = 1) -> dict:
    return {
        "rank": rank,
        "score": 0.91,
        "chunk_id": "tec-example::article-1::chunk-001",
        "record_id": "tec-example::article-1",
        "document_id": "tec-example",
        "document_title": "Reglamento de ejemplo",
        "citation_label": "Reglamento de ejemplo, Artículo 1",
        "source_url": "https://www.tec.ac.cr/example",
        "text": "La solicitud se presenta en tres días hábiles.",
    }


class SourcePreparationTests(unittest.TestCase):
    def test_sources_receive_prompt_local_ids_in_rank_order(self) -> None:
        sources = prepare_sources([example_hit(), example_hit(2)])
        self.assertEqual(
            [source["source_id"] for source in sources],
            ["F1", "F2"],
        )

    def test_context_keeps_provenance_and_delimiters(self) -> None:
        context = format_context(prepare_sources([example_hit()]))
        self.assertIn("[F1]", context)
        self.assertIn("Reglamento de ejemplo, Artículo 1", context)
        self.assertIn("https://www.tec.ac.cr/example", context)
        self.assertIn("tres días hábiles", context)

    def test_messages_label_context_and_question(self) -> None:
        messages = build_messages(
            "¿Cuál es el plazo?",
            prepare_sources([example_hit()]),
        )
        self.assertEqual(
            [message["role"] for message in messages],
            ["system", "user"],
        )
        self.assertIn("Pregunta del usuario", messages[1]["content"])
        self.assertIn("¿Cuál es el plazo?", messages[1]["content"])

    def test_schema_only_allows_retrieved_source_ids(self) -> None:
        schema = answer_schema(["F1", "F2"])
        citation_items = schema["properties"]["citations"]["items"]
        self.assertEqual(citation_items["enum"], ["F1", "F2"])


class GroundedAnswerValidationTests(unittest.TestCase):
    def test_valid_answer_requires_matching_inline_and_structured_cites(
        self,
    ) -> None:
        content = json.dumps(
            {
                "status": "answered",
                "answer": "El plazo es de tres días hábiles [F1].",
                "citations": ["F1"],
            },
            ensure_ascii=False,
        )
        answer = parse_grounded_answer(
            content,
            valid_source_ids={"F1", "F2"},
        )
        self.assertEqual(answer.status, "answered")
        self.assertEqual(answer.citations, ("F1",))

    def test_unknown_citation_is_rejected(self) -> None:
        content = json.dumps(
            {
                "status": "answered",
                "answer": "Respuesta [F9].",
                "citations": ["F9"],
            }
        )
        with self.assertRaisesRegex(ValueError, "inexistentes"):
            parse_grounded_answer(
                content,
                valid_source_ids={"F1"},
            )

    def test_mismatch_between_text_and_array_is_rejected(self) -> None:
        content = json.dumps(
            {
                "status": "answered",
                "answer": "Respuesta [F1].",
                "citations": ["F2"],
            }
        )
        with self.assertRaisesRegex(ValueError, "no coinciden"):
            parse_grounded_answer(
                content,
                valid_source_ids={"F1", "F2"},
            )

    def test_answer_without_citation_is_rejected(self) -> None:
        content = json.dumps(
            {
                "status": "answered",
                "answer": "Respuesta sin fuente.",
                "citations": [],
            }
        )
        with self.assertRaisesRegex(ValueError, "debe incluir citas"):
            parse_grounded_answer(
                content,
                valid_source_ids={"F1"},
            )

    def test_structured_citation_is_appended_when_inline_is_absent(
        self,
    ) -> None:
        content = json.dumps(
            {
                "status": "answered",
                "answer": "El plazo es de tres días hábiles.",
                "citations": ["F1"],
            },
            ensure_ascii=False,
        )
        answer = parse_grounded_answer(
            content,
            valid_source_ids={"F1"},
        )
        self.assertEqual(
            answer.answer,
            "El plazo es de tres días hábiles [F1].",
        )

    def test_exact_abstention_without_citations_is_valid(self) -> None:
        content = json.dumps(
            {
                "status": "not_found",
                "answer": "No encontrado en el contexto.",
                "citations": [],
            }
        )
        answer = parse_grounded_answer(
            content,
            valid_source_ids={"F1"},
        )
        self.assertEqual(answer.status, "not_found")

    def test_abstention_with_citation_is_rejected(self) -> None:
        content = json.dumps(
            {
                "status": "not_found",
                "answer": "No encontrado en el contexto. [F1]",
                "citations": ["F1"],
            }
        )
        with self.assertRaises(ValueError):
            parse_grounded_answer(
                content,
                valid_source_ids={"F1"},
            )

    def test_non_json_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "JSON válido"):
            parse_grounded_answer(
                "respuesta libre",
                valid_source_ids={"F1"},
            )


class GenerationMetricTests(unittest.TestCase):
    def test_metrics_convert_nanoseconds_and_calculate_speed(self) -> None:
        metrics = generation_metrics(
            {
                "total_duration": 2_000_000_000,
                "load_duration": 500_000_000,
                "prompt_eval_count": 100,
                "eval_count": 20,
                "eval_duration": 400_000_000,
                "done_reason": "stop",
            },
            request_elapsed_ms=2100.0,
        )
        self.assertEqual(metrics["ollama_total_ms"], 2000.0)
        self.assertEqual(metrics["model_load_ms"], 500.0)
        self.assertEqual(metrics["tokens_per_second"], 50.0)

    def test_generation_error_preserves_raw_model_content(self) -> None:
        class FakeClient:
            @staticmethod
            def chat(payload: dict) -> dict:
                del payload
                return {
                    "message": {
                        "content": (
                            '{"status":"answered","answer":"",'
                            '"citations":[]}'
                        )
                    }
                }

        with self.assertRaises(GenerationValidationError) as caught:
            generate_grounded_answer(
                FakeClient(),
                model="example",
                question="¿Pregunta?",
                sources=[
                    {
                        "source_id": "F1",
                        "document_title": "Documento",
                        "citation_label": "Artículo 1",
                        "source_url": "https://example.com",
                        "text": "Evidencia",
                    }
                ],
            )
        self.assertIn(
            '"answer":""',
            caught.exception.raw_content,
        )


if __name__ == "__main__":
    unittest.main()
