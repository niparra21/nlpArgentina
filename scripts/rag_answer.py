"""Answer one TEC question with retrieval, local generation and observability."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

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
    generate_grounded_answer,
    prepare_sources,
)
from scripts.ollama_client import (  # noqa: E402
    DEFAULT_OLLAMA_URL,
    OllamaClient,
    OllamaError,
    find_model,
)
from scripts.retrieval import (  # noqa: E402
    DEFAULT_MODEL_NAME,
    DEFAULT_SNAPSHOT_ID,
    default_index_dir,
    load_index,
    search_question,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Responde una pregunta sobre normativa del TEC con recuperación "
            "semántica y Qwen local."
        )
    )
    parser.add_argument("question", help="Pregunta escrita en lenguaje natural")
    parser.add_argument("--snapshot-id", default=DEFAULT_SNAPSHOT_ID)
    parser.add_argument(
        "--retrieval-model",
        default=DEFAULT_MODEL_NAME,
    )
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
    parser.add_argument(
        "--output",
        type=Path,
        help="Ruta JSON opcional; por defecto se crea bajo results/rag/.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not args.question.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    if args.top_k <= 0:
        raise ValueError("--top-k debe ser positivo.")
    if args.num_ctx <= 0:
        raise ValueError("--num-ctx debe ser positivo.")
    if args.num_predict <= 0:
        raise ValueError("--num-predict debe ser positivo.")
    if args.ollama_timeout <= 0:
        raise ValueError("--ollama-timeout debe ser positivo.")


def filesystem_slug(value: str) -> str:
    """Return a stable model tag suitable for a Windows directory name."""

    return (
        value.strip()
        .replace("\\", "-")
        .replace("/", "-")
        .replace(":", "-")
        .replace(" ", "-")
    )


def relative_or_absolute(path: Path) -> str:
    """Prefer a repository-relative path in observable records."""

    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return str(resolved)


def default_output_path(
    *,
    generator_model: str,
    started_at: datetime,
) -> Path:
    date = started_at.date().isoformat()
    run_id = started_at.strftime("rag-%Y%m%dT%H%M%S-%f")
    return (
        ROOT
        / "results"
        / "rag"
        / date
        / filesystem_slug(generator_model)
        / f"{run_id}.json"
    )


def write_record(path: Path, record: dict[str, Any]) -> None:
    """Write one immutable, human-readable RAG observation."""

    if path.exists():
        raise FileExistsError(
            f"El registro ya existe y no se reemplazará: {path}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            record,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def cited_source_summaries(
    citations: tuple[str, ...],
    sources: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Resolve prompt-local citation IDs back to official provenance."""

    by_id = {source["source_id"]: source for source in sources}
    return [
        {
            "source_id": source_id,
            "citation_label": by_id[source_id]["citation_label"],
            "source_url": by_id[source_id]["source_url"],
        }
        for source_id in citations
    ]


def execute(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    """Execute one complete RAG request and persist its observation."""

    from sentence_transformers import SentenceTransformer

    validate_args(args)
    started_at = datetime.now().astimezone()
    pipeline_started = perf_counter()

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

    retrieval_model_started = perf_counter()
    retrieval_model = SentenceTransformer(
        manifest["model_name"],
        revision=manifest["model_revision"],
    )
    retrieval_model_load_ms = (
        perf_counter() - retrieval_model_started
    ) * 1000

    hits, retrieval_search_ms = search_question(
        retrieval_model,
        embeddings,
        chunks,
        args.question,
        top_k=args.top_k,
        unique_records=False,
    )
    if not hits:
        raise RuntimeError("El recuperador no devolvió fragmentos.")
    sources = prepare_sources(hits)

    answer, generation, request_metadata = generate_grounded_answer(
        client,
        model=args.generator_model,
        question=args.question,
        sources=sources,
        num_ctx=args.num_ctx,
        temperature=args.temperature,
        seed=args.seed,
        num_predict=args.num_predict,
        keep_alive=args.keep_alive,
    )
    finished_at = datetime.now().astimezone()
    total_ms = (perf_counter() - pipeline_started) * 1000
    model_details = generator_metadata.get("details", {})

    record = {
        "schema_version": RAG_SCHEMA_VERSION,
        "run_id": started_at.strftime("rag-%Y%m%dT%H%M%S-%f"),
        "started_at": started_at.isoformat(timespec="milliseconds"),
        "finished_at": finished_at.isoformat(timespec="milliseconds"),
        "question": args.question.strip(),
        "configuration": {
            "snapshot_id": args.snapshot_id,
            "top_k": args.top_k,
            "unique_records": False,
            "index_directory": relative_or_absolute(index_dir),
            "index_manifest_sha256": sha256_file(
                index_dir / "index_manifest.json"
            ),
            "retrieval_model": manifest["model_name"],
            "retrieval_model_revision": manifest["model_revision"],
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
        },
        "retrieval": {
            "model_load_ms": retrieval_model_load_ms,
            "search_ms": retrieval_search_ms,
            "returned_sources": len(sources),
            "sources": sources,
        },
        "generation": {
            **generation,
            **request_metadata,
        },
        "result": {
            "status": answer.status,
            "answer": answer.answer,
            "citations": list(answer.citations),
            "citation_count": len(answer.citations),
            "citations_valid": True,
            "cited_sources": cited_source_summaries(
                answer.citations,
                sources,
            ),
        },
        "total_pipeline_ms": total_ms,
    }

    output_path = (
        args.output.resolve()
        if args.output
        else default_output_path(
            generator_model=args.generator_model,
            started_at=started_at,
        )
    )
    write_record(output_path, record)
    return record, output_path


def print_result(record: dict[str, Any], output_path: Path) -> None:
    result = record["result"]
    retrieval = record["retrieval"]
    generation = record["generation"]
    print(f"\nPregunta:\n{record['question']}")
    print(f"\nRespuesta:\n{result['answer']}")
    if result["cited_sources"]:
        print("\nFuentes citadas:")
        for source in result["cited_sources"]:
            print(
                f"[{source['source_id']}] {source['citation_label']}\n"
                f"    {source['source_url']}"
            )
    print(
        "\nObservabilidad:\n"
        f"- Recuperación: {retrieval['search_ms']:.2f} ms\n"
        f"- Generación: {generation['request_latency_ms']:.2f} ms\n"
        f"- Velocidad: {generation['tokens_per_second']:.2f} tokens/s\n"
        f"- Pipeline total: {record['total_pipeline_ms']:.2f} ms\n"
        f"- Registro: {output_path}"
    )


def main() -> int:
    try:
        record, output_path = execute(parse_args())
        print_result(record, output_path)
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
