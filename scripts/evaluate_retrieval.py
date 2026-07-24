"""Evaluate semantic retrieval against the gold TEC questions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.retrieval import (  # noqa: E402
    DEFAULT_MODEL_NAME,
    DEFAULT_SNAPSHOT_ID,
    default_index_dir,
    default_results_dir,
    load_index,
    read_jsonl,
    search_question,
    sha256_file,
    write_jsonl,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_QUESTIONS_PATH = (
    ROOT / "data" / "evaluation" / "questions.jsonl"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate the TEC semantic retrieval baseline."
    )
    parser.add_argument("--snapshot-id", default=DEFAULT_SNAPSHOT_ID)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--index-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing evaluation artifacts.",
    )
    return parser.parse_args()


def prepare_output_dir(output_dir: Path, *, force: bool) -> None:
    artifacts = [
        output_dir / "evaluation.jsonl",
        output_dir / "summary.json",
    ]
    existing = [path for path in artifacts if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"Evaluation artifacts already exist ({names}). "
            "Use --force to replace them intentionally."
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    if force:
        for path in existing:
            path.unlink()


def compact_hit(hit: dict[str, Any]) -> dict[str, Any]:
    """Keep observable retrieval data without duplicating embedding input."""

    return {
        "rank": hit["rank"],
        "score": hit["score"],
        "chunk_id": hit["chunk_id"],
        "record_id": hit["record_id"],
        "document_id": hit["document_id"],
        "citation_label": hit["citation_label"],
        "source_url": hit["source_url"],
        "text": hit["text"],
    }


def evaluate_question(
    question: dict[str, Any],
    hits: list[dict[str, Any]],
    elapsed_ms: float,
) -> dict[str, Any]:
    expected = set(question["supporting_record_ids"])
    retrieved_ids = [hit["record_id"] for hit in hits]
    matched = [
        record_id for record_id in retrieved_ids if record_id in expected
    ]
    evidence_recall = (
        len(set(matched)) / len(expected) if expected else None
    )
    return {
        "question_id": question["question_id"],
        "question": question["question"],
        "question_type": question["question_type"],
        "answerable": question["answerable"],
        "expected_record_ids": question["supporting_record_ids"],
        "retrieved": [compact_hit(hit) for hit in hits],
        "matched_record_ids": matched,
        "hit_at_k": bool(matched) if expected else None,
        "complete_evidence_at_k": (
            expected.issubset(retrieved_ids) if expected else None
        ),
        "evidence_recall_at_k": evidence_recall,
        "max_score": hits[0]["score"] if hits else None,
        "latency_ms": elapsed_ms,
    }


def metrics_at_k(
    results: list[dict[str, Any]],
    k: int,
) -> dict[str, float]:
    answerable = [result for result in results if result["answerable"]]
    hit_values: list[float] = []
    complete_values: list[float] = []
    recall_values: list[float] = []
    reciprocal_ranks: list[float] = []
    for result in answerable:
        expected = set(result["expected_record_ids"])
        ranked = [
            hit["record_id"] for hit in result["retrieved"][:k]
        ]
        found = expected.intersection(ranked)
        hit_values.append(float(bool(found)))
        complete_values.append(float(expected.issubset(ranked)))
        recall_values.append(len(found) / len(expected))
        first_relevant_rank = next(
            (
                rank
                for rank, record_id in enumerate(ranked, start=1)
                if record_id in expected
            ),
            None,
        )
        reciprocal_ranks.append(
            1 / first_relevant_rank if first_relevant_rank else 0.0
        )
    return {
        "hit_rate": mean(hit_values),
        "complete_evidence_rate": mean(complete_values),
        "mean_evidence_recall": mean(recall_values),
        "mean_reciprocal_rank": mean(reciprocal_ranks),
    }


def summarize(
    results: list[dict[str, Any]],
    *,
    top_k: int,
    model_name: str,
    model_revision: str,
    snapshot_id: str,
) -> dict[str, Any]:
    answerable = [result for result in results if result["answerable"]]
    unanswerable = [
        result for result in results if not result["answerable"]
    ]
    latencies = [result["latency_ms"] for result in results]
    unanswerable_scores = [
        result["max_score"]
        for result in unanswerable
        if result["max_score"] is not None
    ]
    cutoffs = sorted({1, 3, top_k})
    by_type: dict[str, Any] = {}
    for question_type in ("direct", "multi_section"):
        subset = [
            result
            for result in answerable
            if result["question_type"] == question_type
        ]
        by_type[question_type] = {
            "questions": len(subset),
            f"metrics_at_{top_k}": metrics_at_k(subset, top_k),
        }

    return {
        "generated_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "snapshot_id": snapshot_id,
        "model_name": model_name,
        "model_revision": model_revision,
        "top_k": top_k,
        "questions": len(results),
        "answerable_questions": len(answerable),
        "unanswerable_questions": len(unanswerable),
        "metrics": {
            f"at_{cutoff}": metrics_at_k(results, cutoff)
            for cutoff in cutoffs
        },
        "by_question_type": by_type,
        "latency_ms": {
            "mean": mean(latencies),
            "median": median(latencies),
            "minimum": min(latencies),
            "maximum": max(latencies),
        },
        "unanswerable_max_score": {
            "mean": mean(unanswerable_scores),
            "minimum": min(unanswerable_scores),
            "maximum": max(unanswerable_scores),
            "note": (
                "Retrieval always returns candidates. These scores are "
                "descriptive and do not yet define an abstention threshold."
            ),
        },
    }


def main(args: argparse.Namespace) -> dict[str, Any]:
    from sentence_transformers import SentenceTransformer

    if args.top_k <= 0:
        raise ValueError("top-k must be positive")
    questions_path = args.questions.resolve()
    index_dir = (
        args.index_dir.resolve()
        if args.index_dir
        else default_index_dir(args.snapshot_id, args.model_name)
    )
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else default_results_dir(args.snapshot_id, args.model_name)
    )
    prepare_output_dir(output_dir, force=args.force)

    embeddings, chunks, manifest = load_index(index_dir)
    questions = read_jsonl(questions_path)
    model = SentenceTransformer(
        manifest["model_name"],
        revision=manifest["model_revision"],
        local_files_only=True,
    )

    results: list[dict[str, Any]] = []
    print(
        f"Evaluating {len(questions)} questions with top_k={args.top_k}..."
    )
    for question in questions:
        hits, elapsed_ms = search_question(
            model,
            embeddings,
            chunks,
            question["question"],
            top_k=args.top_k,
        )
        result = evaluate_question(question, hits, elapsed_ms)
        results.append(result)
        marker = (
            "hit"
            if result["hit_at_k"]
            else "miss"
            if result["answerable"]
            else "unanswerable"
        )
        print(
            f"{question['question_id']}: {marker} "
            f"({elapsed_ms:.2f} ms)"
        )

    summary = summarize(
        results,
        top_k=args.top_k,
        model_name=manifest["model_name"],
        model_revision=manifest["model_revision"],
        snapshot_id=args.snapshot_id,
    )
    summary["questions_file"] = questions_path.relative_to(ROOT).as_posix()
    summary["questions_sha256"] = sha256_file(questions_path)
    summary["index_manifest"] = (
        index_dir / "index_manifest.json"
    ).relative_to(ROOT).as_posix()
    summary["index_manifest_sha256"] = sha256_file(
        index_dir / "index_manifest.json"
    )

    evaluation_path = output_dir / "evaluation.jsonl"
    summary_path = output_dir / "summary.json"
    write_jsonl(evaluation_path, results)
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

    at_k = summary["metrics"][f"at_{args.top_k}"]
    print(f"\nResults written to: {output_dir}")
    print(
        f"Hit rate@{args.top_k}: {at_k['hit_rate']:.3f} | "
        f"Complete evidence@{args.top_k}: "
        f"{at_k['complete_evidence_rate']:.3f} | "
        f"MRR@{args.top_k}: {at_k['mean_reciprocal_rank']:.3f}"
    )
    return summary


if __name__ == "__main__":
    main(parse_args())
