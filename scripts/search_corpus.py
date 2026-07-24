"""Search the local TEC semantic index from the command line."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from textwrap import shorten

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.retrieval import (  # noqa: E402
    DEFAULT_MODEL_NAME,
    DEFAULT_SNAPSHOT_ID,
    default_index_dir,
    load_index,
    search_question,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Return the most relevant TEC regulation sections."
    )
    parser.add_argument("question", help="Question written in natural language")
    parser.add_argument("--snapshot-id", default=DEFAULT_SNAPSHOT_ID)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--index-dir", type=Path)
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def main(args: argparse.Namespace) -> list[dict]:
    from sentence_transformers import SentenceTransformer

    index_dir = (
        args.index_dir.resolve()
        if args.index_dir
        else default_index_dir(args.snapshot_id, args.model_name)
    )
    embeddings, chunks, manifest = load_index(index_dir)
    model = SentenceTransformer(
        manifest["model_name"],
        revision=manifest["model_revision"],
        local_files_only=True,
    )
    hits, elapsed_ms = search_question(
        model,
        embeddings,
        chunks,
        args.question,
        top_k=args.top_k,
    )

    print(f"\nPregunta: {args.question}")
    print(
        f"Modelo: {manifest['model_name']} | "
        f"Tiempo de consulta: {elapsed_ms:.2f} ms"
    )
    for hit in hits:
        preview = shorten(
            " ".join(hit["text"].split()),
            width=360,
            placeholder="…",
        )
        print(
            f"\n{hit['rank']}. score={hit['score']:.4f}\n"
            f"   {hit['citation_label']}\n"
            f"   record_id: {hit['record_id']}\n"
            f"   chunk_id: {hit['chunk_id']}\n"
            f"   {preview}\n"
            f"   Fuente: {hit['source_url']}"
        )
    return hits


if __name__ == "__main__":
    main(parse_args())
