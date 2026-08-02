"""Evaluate the complete local RAG pipeline against the 40 gold questions."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from typing import Any, Iterable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.generation import (  # noqa: E402
    DEFAULT_GENERATOR_MODEL,
    DEFAULT_KEEP_ALIVE,
    DEFAULT_NUM_CTX,
    DEFAULT_NUM_PREDICT,
    DEFAULT_SEED,
    DEFAULT_TEMPERATURE,
    RAG_SCHEMA_VERSION,
    GenerationValidationError,
    GroundedAnswer,
    generate_grounded_answer,
    prepare_sources,
)
from scripts.ollama_client import (  # noqa: E402
    DEFAULT_OLLAMA_URL,
    OllamaClient,
    OllamaError,
    find_model,
)
from scripts.rag_answer import (  # noqa: E402
    cited_source_summaries,
    filesystem_slug,
    relative_or_absolute,
)
from scripts.retrieval import (  # noqa: E402
    DEFAULT_MODEL_NAME,
    DEFAULT_SNAPSHOT_ID,
    default_index_dir,
    load_index,
    read_jsonl,
    search_question,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS_PATH = (
    ROOT / "data" / "evaluation" / "questions.jsonl"
)
WORD_PATTERN = re.compile(r"[a-z0-9]+")
CITATION_TOKEN_PATTERN = re.compile(r"\bf[1-9][0-9]*\b")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Ejecuta y evalúa el RAG local sobre el conjunto gold completo."
        )
    )
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--snapshot-id", default=DEFAULT_SNAPSHOT_ID)
    parser.add_argument("--retrieval-model", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--index-dir", type=Path)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--generator-model", default=DEFAULT_GENERATOR_MODEL)
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL)
    parser.add_argument("--ollama-timeout", type=float, default=300)
    parser.add_argument("--num-ctx", type=int, default=DEFAULT_NUM_CTX)
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--num-predict", type=int, default=DEFAULT_NUM_PREDICT)
    parser.add_argument("--keep-alive", default=DEFAULT_KEEP_ALIVE)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--limit",
        type=int,
        help="Evalúa solamente las primeras N preguntas para diagnóstico.",
    )
    parser.add_argument(
        "--question-id",
        action="append",
        help=(
            "Evalúa un ID específico; puede repetirse para seleccionar varios."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reemplaza evaluation.jsonl y summary.json intencionalmente.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    for name in ("top_k", "num_ctx", "num_predict"):
        if getattr(args, name) <= 0:
            raise ValueError(f"--{name.replace('_', '-')} debe ser positivo.")
    if args.ollama_timeout <= 0:
        raise ValueError("--ollama-timeout debe ser positivo.")
    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit debe ser positivo.")


def default_output_dir(
    *,
    generator_model: str,
    started_at: datetime,
) -> Path:
    return (
        ROOT
        / "results"
        / "rag-evaluation"
        / started_at.date().isoformat()
        / filesystem_slug(generator_model)
    )


def prepare_output_dir(output_dir: Path, *, force: bool) -> None:
    """Prepare known batch artifacts without deleting unrelated files."""

    artifacts = [
        output_dir / "evaluation.jsonl",
        output_dir / "summary.json",
    ]
    existing = [path for path in artifacts if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"Ya existen artefactos de evaluación ({names}). "
            "Use --force para reemplazarlos intencionalmente."
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    if force:
        for path in existing:
            path.unlink()


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Append and flush one result so progress survives later failures."""

    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        handle.write("\n")


def normalized_tokens(text: str) -> list[str]:
    """Create accent-insensitive lexical tokens, excluding citation labels."""

    normalized = unicodedata.normalize("NFKD", text.lower())
    without_marks = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    )
    return [
        token
        for token in WORD_PATTERN.findall(without_marks)
        if not CITATION_TOKEN_PATTERN.fullmatch(token)
    ]


def lexical_overlap(
    expected_answer: str,
    generated_answer: str,
) -> dict[str, float]:
    """Calculate descriptive bag-of-words overlap against the reference."""

    expected = Counter(normalized_tokens(expected_answer))
    generated = Counter(normalized_tokens(generated_answer))
    overlap = sum((expected & generated).values())
    expected_total = sum(expected.values())
    generated_total = sum(generated.values())
    precision = overlap / generated_total if generated_total else 0.0
    recall = overlap / expected_total if expected_total else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def unique_in_order(values: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(values))


def retrieval_gold_metrics(
    question: dict[str, Any],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    expected = set(question["supporting_record_ids"])
    if not expected:
        return {
            "retrieval_hit": None,
            "retrieval_complete_evidence": None,
            "retrieval_evidence_recall": None,
        }
    retrieved = {source["record_id"] for source in sources}
    matched = expected & retrieved
    return {
        "retrieval_hit": bool(matched),
        "retrieval_complete_evidence": expected.issubset(retrieved),
        "retrieval_evidence_recall": len(matched) / len(expected),
    }


def generation_gold_metrics(
    question: dict[str, Any],
    answer: GroundedAnswer,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    """Compare status and cited provenance with manually defined gold data."""

    answerable = bool(question["answerable"])
    expected = set(question["supporting_record_ids"])
    source_by_id = {source["source_id"]: source for source in sources}
    cited_record_ids = unique_in_order(
        source_by_id[source_id]["record_id"]
        for source_id in answer.citations
    )
    cited = set(cited_record_ids)
    status_correct = (
        answer.status == "answered"
        if answerable
        else answer.status == "not_found"
    )

    if answerable:
        matched = cited & expected
        citation_precision = (
            len(matched) / len(cited) if cited else 0.0
        )
        citation_recall = len(matched) / len(expected)
        lexical = (
            lexical_overlap(
                question["expected_answer"],
                answer.answer,
            )
            if answer.status == "answered"
            else None
        )
        citation_hit = bool(matched)
        citation_complete = expected.issubset(cited)
    else:
        citation_precision = None
        citation_recall = None
        lexical = None
        citation_hit = None
        citation_complete = None

    return {
        "status_correct": status_correct,
        "cited_record_ids": cited_record_ids,
        "citation_hit": citation_hit,
        "citation_complete_expected_evidence": citation_complete,
        "citation_precision_against_gold": citation_precision,
        "citation_evidence_recall": citation_recall,
        "lexical_overlap": lexical,
    }


def failed_generation_metrics(
    question: dict[str, Any],
) -> dict[str, Any]:
    answerable = bool(question["answerable"])
    return {
        "status_correct": False,
        "cited_record_ids": [],
        "citation_hit": False if answerable else None,
        "citation_complete_expected_evidence": (
            False if answerable else None
        ),
        "citation_precision_against_gold": 0.0 if answerable else None,
        "citation_evidence_recall": 0.0 if answerable else None,
        "lexical_overlap": None,
    }


def numeric_summary(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    ordered = sorted(values)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "mean": mean(ordered),
        "median": median(ordered),
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "p95_nearest_rank": ordered[p95_index],
    }


def optional_mean(values: Iterable[Any]) -> float | None:
    numeric = [float(value) for value in values if value is not None]
    return mean(numeric) if numeric else None


def group_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [record for record in records if record["error"] is None]
    answerable = [
        record for record in records if record["gold"]["answerable"]
    ]
    lexical_f1 = [
        record["evaluation"]["lexical_overlap"]["f1"]
        for record in records
        if record["evaluation"]["lexical_overlap"] is not None
    ]
    return {
        "questions": len(records),
        "completed": len(completed),
        "status_accuracy": optional_mean(
            record["evaluation"]["status_correct"] for record in records
        ),
        "retrieval_hit_rate": optional_mean(
            record["evaluation"]["retrieval_hit"] for record in records
        ),
        "citation_hit_rate": optional_mean(
            record["evaluation"]["citation_hit"] for record in answerable
        ),
        "complete_expected_evidence_citation_rate": optional_mean(
            record["evaluation"]["citation_complete_expected_evidence"]
            for record in answerable
        ),
        "mean_citation_precision_against_gold": optional_mean(
            record["evaluation"]["citation_precision_against_gold"]
            for record in answerable
        ),
        "mean_citation_evidence_recall": optional_mean(
            record["evaluation"]["citation_evidence_recall"]
            for record in answerable
        ),
        "mean_lexical_f1": mean(lexical_f1) if lexical_f1 else None,
    }


def summarize_records(
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    answerable = [
        record for record in records if record["gold"]["answerable"]
    ]
    unanswerable = [
        record for record in records if not record["gold"]["answerable"]
    ]
    completed = [record for record in records if record["error"] is None]
    by_type = {
        question_type: group_summary(
            [
                record
                for record in records
                if record["gold"]["question_type"] == question_type
            ]
        )
        for question_type in sorted(
            {record["gold"]["question_type"] for record in records}
        )
    }
    by_category = {
        category: group_summary(
            [
                record
                for record in records
                if record["gold"]["category"] == category
            ]
        )
        for category in sorted(
            {record["gold"]["category"] for record in records}
        )
    }
    return {
        "questions": len(records),
        "answerable_questions": len(answerable),
        "unanswerable_questions": len(unanswerable),
        "completed_questions": len(completed),
        "errors": len(records) - len(completed),
        "metrics": {
            "status_accuracy": optional_mean(
                record["evaluation"]["status_correct"]
                for record in records
            ),
            "answerable_answer_rate": optional_mean(
                record["result"] is not None
                and record["result"]["status"] == "answered"
                for record in answerable
            ),
            "unanswerable_abstention_rate": optional_mean(
                record["result"] is not None
                and record["result"]["status"] == "not_found"
                for record in unanswerable
            ),
            "retrieval_hit_rate": optional_mean(
                record["evaluation"]["retrieval_hit"]
                for record in answerable
            ),
            "retrieval_complete_evidence_rate": optional_mean(
                record["evaluation"]["retrieval_complete_evidence"]
                for record in answerable
            ),
            "mean_retrieval_evidence_recall": optional_mean(
                record["evaluation"]["retrieval_evidence_recall"]
                for record in answerable
            ),
            "citation_hit_rate": optional_mean(
                record["evaluation"]["citation_hit"]
                for record in answerable
            ),
            "complete_expected_evidence_citation_rate": optional_mean(
                record["evaluation"][
                    "citation_complete_expected_evidence"
                ]
                for record in answerable
            ),
            "mean_citation_precision_against_gold": optional_mean(
                record["evaluation"]["citation_precision_against_gold"]
                for record in answerable
            ),
            "mean_citation_evidence_recall": optional_mean(
                record["evaluation"]["citation_evidence_recall"]
                for record in answerable
            ),
            "mean_lexical_f1": optional_mean(
                (
                    record["evaluation"]["lexical_overlap"]["f1"]
                    if record["evaluation"]["lexical_overlap"] is not None
                    else None
                )
                for record in answerable
            ),
        },
        "latency_ms": {
            "retrieval_search": numeric_summary(
                [
                    float(record["retrieval"]["search_ms"])
                    for record in records
                ]
            ),
            "generation_request": numeric_summary(
                [
                    float(record["generation"]["request_latency_ms"])
                    for record in completed
                ]
            ),
            "question_total": numeric_summary(
                [
                    float(record["question_total_ms"])
                    for record in records
                ]
            ),
        },
        "generation_speed_tokens_per_second": numeric_summary(
            [
                float(record["generation"]["tokens_per_second"])
                for record in completed
            ]
        ),
        "by_question_type": by_type,
        "by_category": by_category,
        "metric_notes": {
            "status_accuracy": (
                "answered para preguntas respondibles y not_found para las "
                "preguntas marcadas como no respondibles."
            ),
            "citation_hit_rate": (
                "Proporción de preguntas respondibles donde al menos una "
                "fuente citada coincide con un record_id gold."
            ),
            "complete_expected_evidence_citation_rate": (
                "Proporción donde se citaron todos los record_id gold; es "
                "especialmente relevante para preguntas multi_section."
            ),
            "lexical_overlap": (
                "Superposición bag-of-words descriptiva contra la respuesta "
                "de referencia. No demuestra por sí sola corrección semántica "
                "ni fidelidad."
            ),
        },
    }


def result_payload(
    answer: GroundedAnswer,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "status": answer.status,
        "answer": answer.answer,
        "citations": list(answer.citations),
        "citation_count": len(answer.citations),
        "citations_valid": True,
        "cited_sources": cited_source_summaries(
            answer.citations,
            sources,
        ),
    }


def execute(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    """Run the configured batch and return its summary and output directory."""

    from sentence_transformers import SentenceTransformer

    validate_args(args)
    batch_started_at = datetime.now().astimezone()
    batch_started = perf_counter()
    questions_path = args.questions.resolve()
    questions = read_jsonl(questions_path)
    if args.question_id:
        requested_ids = set(args.question_id)
        known_ids = {
            question["question_id"] for question in questions
        }
        missing_ids = requested_ids - known_ids
        if missing_ids:
            raise ValueError(
                "No existen estos question_id: "
                f"{sorted(missing_ids)}"
            )
        questions = [
            question
            for question in questions
            if question["question_id"] in requested_ids
        ]
    if args.limit is not None:
        questions = questions[: args.limit]
    if not questions:
        raise ValueError("No hay preguntas para evaluar.")

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else default_output_dir(
            generator_model=args.generator_model,
            started_at=batch_started_at,
        )
    )
    prepare_output_dir(output_dir, force=args.force)
    evaluation_path = output_dir / "evaluation.jsonl"

    client = OllamaClient(
        args.ollama_url,
        timeout=args.ollama_timeout,
    )
    ollama_version = client.version()
    tags = client.tags()
    generator_metadata = find_model(tags, args.generator_model)
    if generator_metadata is None:
        raise FileNotFoundError(
            f"El modelo {args.generator_model!r} no está instalado. "
            f"Ejecute: ollama pull {args.generator_model}"
        )

    index_dir = (
        args.index_dir.resolve()
        if args.index_dir
        else default_index_dir(
            args.snapshot_id,
            args.retrieval_model,
        )
    )
    embeddings, chunks, manifest = load_index(index_dir)
    model_load_started = perf_counter()
    retrieval_model = SentenceTransformer(
        manifest["model_name"],
        revision=manifest["model_revision"],
    )
    retrieval_model_load_ms = (
        perf_counter() - model_load_started
    ) * 1000

    run_id = batch_started_at.strftime("rag-eval-%Y%m%dT%H%M%S-%f")
    records: list[dict[str, Any]] = []
    print(
        f"Evaluando {len(questions)} preguntas con "
        f"{args.generator_model}, top_k={args.top_k}...",
        flush=True,
    )
    for position, question in enumerate(questions, start=1):
        question_started = perf_counter()
        hits, retrieval_ms = search_question(
            retrieval_model,
            embeddings,
            chunks,
            question["question"],
            top_k=args.top_k,
            unique_records=False,
        )
        sources = prepare_sources(hits)
        evaluation = retrieval_gold_metrics(question, sources)
        result = None
        generation = None
        error_payload = None
        try:
            answer, generation, request_metadata = (
                generate_grounded_answer(
                    client,
                    model=args.generator_model,
                    question=question["question"],
                    sources=sources,
                    num_ctx=args.num_ctx,
                    temperature=args.temperature,
                    seed=args.seed,
                    num_predict=args.num_predict,
                    keep_alive=args.keep_alive,
                )
            )
            generation = {
                **generation,
                **request_metadata,
            }
            result = result_payload(answer, sources)
            evaluation.update(
                generation_gold_metrics(
                    question,
                    answer,
                    sources,
                )
            )
            marker = "ok" if evaluation["status_correct"] else "status_miss"
        except (OllamaError, ValueError) as exc:
            evaluation.update(failed_generation_metrics(question))
            error_payload = {
                "type": type(exc).__name__,
                "message": str(exc),
            }
            if isinstance(exc, GenerationValidationError):
                error_payload["raw_model_content"] = exc.raw_content
            marker = "error"

        record = {
            "run_id": run_id,
            "position": position,
            "question_id": question["question_id"],
            "question": question["question"],
            "gold": {
                "question_type": question["question_type"],
                "category": question["category"],
                "answerable": question["answerable"],
                "expected_answer": question["expected_answer"],
                "supporting_record_ids": question[
                    "supporting_record_ids"
                ],
                "document_ids": question["document_ids"],
            },
            "retrieval": {
                "search_ms": retrieval_ms,
                "returned_sources": len(sources),
                "sources": sources,
            },
            "generation": generation,
            "result": result,
            "evaluation": evaluation,
            "error": error_payload,
            "question_total_ms": (
                perf_counter() - question_started
            )
            * 1000,
        }
        records.append(record)
        append_jsonl(evaluation_path, record)
        print(
            f"[{position:02d}/{len(questions):02d}] "
            f"{question['question_id']}: {marker} "
            f"({record['question_total_ms'] / 1000:.2f} s)",
            flush=True,
        )

    batch_finished_at = datetime.now().astimezone()
    model_details = generator_metadata.get("details", {})
    summary = {
        "schema_version": RAG_SCHEMA_VERSION,
        "run_id": run_id,
        "started_at": batch_started_at.isoformat(timespec="milliseconds"),
        "finished_at": batch_finished_at.isoformat(timespec="milliseconds"),
        "batch_duration_ms": (perf_counter() - batch_started) * 1000,
        "configuration": {
            "questions_file": relative_or_absolute(questions_path),
            "questions_sha256": sha256_file(questions_path),
            "snapshot_id": args.snapshot_id,
            "top_k": args.top_k,
            "unique_records": False,
            "index_directory": relative_or_absolute(index_dir),
            "index_manifest_sha256": sha256_file(
                index_dir / "index_manifest.json"
            ),
            "retrieval_model": manifest["model_name"],
            "retrieval_model_revision": manifest["model_revision"],
            "retrieval_model_load_ms": retrieval_model_load_ms,
            "generator_model": args.generator_model,
            "generator_digest": generator_metadata.get("digest"),
            "generator_parameter_size": model_details.get("parameter_size"),
            "generator_quantization": model_details.get(
                "quantization_level"
            ),
            "ollama_version": ollama_version.get("version"),
            "ollama_url": args.ollama_url,
            "num_ctx": args.num_ctx,
            "temperature": args.temperature,
            "seed": args.seed,
            "num_predict": args.num_predict,
            "thinking": False,
            "keep_alive": args.keep_alive,
            "limit": args.limit,
            "question_ids": args.question_id,
            "citation_policy": (
                "structured_required; inline citations validated when "
                "present and appended deterministically when absent"
            ),
        },
        **summarize_records(records),
        "artifacts": {
            "evaluation_jsonl": relative_or_absolute(evaluation_path),
        },
    }
    summary_path = output_dir / "summary.json"
    summary["artifacts"]["summary_json"] = relative_or_absolute(summary_path)
    summary_path.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    metrics = summary["metrics"]
    print(f"\nResultados: {output_dir}", flush=True)
    print(
        f"Completadas: {summary['completed_questions']}/"
        f"{summary['questions']} | "
        f"Status accuracy: {metrics['status_accuracy']:.3f} | "
        f"Citation hit: {metrics['citation_hit_rate']:.3f}",
        flush=True,
    )
    return summary, output_dir


def main() -> int:
    try:
        execute(parse_args())
        return 0
    except (
        FileExistsError,
        FileNotFoundError,
        OllamaError,
        RuntimeError,
        ValueError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
