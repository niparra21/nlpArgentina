"""Build a reproducible local embedding index for the TEC corpus."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import numpy as np

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.retrieval import (
    DEFAULT_MAX_INPUT_TOKENS,
    DEFAULT_MODEL_NAME,
    DEFAULT_MODEL_REVISION,
    DEFAULT_OVERLAP_TOKENS,
    DEFAULT_SNAPSHOT_ID,
    INDEX_SCHEMA_VERSION,
    build_chunks,
    default_index_dir,
    default_sections_path,
    read_jsonl,
    sha256_file,
    write_jsonl,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create normalized multilingual E5 embeddings for the processed "
            "TEC regulation sections."
        )
    )
    parser.add_argument("--snapshot-id", default=DEFAULT_SNAPSHOT_ID)
    parser.add_argument("--model-name", default=DEFAULT_MODEL_NAME)
    parser.add_argument("--model-revision", default=DEFAULT_MODEL_REVISION)
    parser.add_argument(
        "--max-input-tokens",
        type=int,
        default=DEFAULT_MAX_INPUT_TOKENS,
    )
    parser.add_argument(
        "--overlap-tokens",
        type=int,
        default=DEFAULT_OVERLAP_TOKENS,
    )
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the three known index artifacts if they exist.",
    )
    return parser.parse_args()


def prepare_output_dir(output_dir: Path, *, force: bool) -> None:
    artifacts = [
        output_dir / "embeddings.npy",
        output_dir / "chunks.jsonl",
        output_dir / "index_manifest.json",
    ]
    existing = [path for path in artifacts if path.exists()]
    if existing and not force:
        names = ", ".join(path.name for path in existing)
        raise FileExistsError(
            f"Index artifacts already exist ({names}). "
            "Use --force to replace them intentionally."
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    if force:
        for path in existing:
            path.unlink()


def build_index(args: argparse.Namespace) -> dict:
    from sentence_transformers import SentenceTransformer

    sections_path = default_sections_path(args.snapshot_id)
    if not sections_path.is_file():
        raise FileNotFoundError(
            f"Processed sections do not exist: {sections_path}"
        )
    if args.batch_size <= 0:
        raise ValueError("batch-size must be positive")

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else default_index_dir(args.snapshot_id, args.model_name)
    )
    prepare_output_dir(output_dir, force=args.force)

    print(f"Loading model: {args.model_name}")
    print(f"Pinned revision: {args.model_revision}")
    model = SentenceTransformer(
        args.model_name,
        revision=args.model_revision,
    )
    model_limit = int(model.max_seq_length)
    if args.max_input_tokens > model_limit:
        raise ValueError(
            f"max-input-tokens={args.max_input_tokens} exceeds the model "
            f"limit of {model_limit}"
        )

    sections = read_jsonl(sections_path)
    print(f"Creating passages from {len(sections)} processed sections...")
    chunks = build_chunks(
        sections,
        model.tokenizer,
        max_input_tokens=args.max_input_tokens,
        overlap_tokens=args.overlap_tokens,
    )

    print(f"Encoding {len(chunks)} passages on {model.device}...")
    embeddings = model.encode(
        [chunk["embedding_text"] for chunk in chunks],
        batch_size=args.batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    embeddings = np.asarray(embeddings, dtype=np.float32)

    embeddings_path = output_dir / "embeddings.npy"
    chunks_path = output_dir / "chunks.jsonl"
    manifest_path = output_dir / "index_manifest.json"
    np.save(embeddings_path, embeddings, allow_pickle=False)
    write_jsonl(chunks_path, chunks)

    chunks_per_record: dict[str, int] = {}
    for chunk in chunks:
        chunks_per_record[chunk["record_id"]] = chunk["chunk_count"]
    split_records = sum(
        chunk_count > 1 for chunk_count in chunks_per_record.values()
    )
    manifest = {
        "schema_version": INDEX_SCHEMA_VERSION,
        "generated_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "snapshot_id": args.snapshot_id,
        "source_file": sections_path.relative_to(
            sections_path.parents[4]
        ).as_posix(),
        "source_sha256": sha256_file(sections_path),
        "model_name": args.model_name,
        "model_revision": args.model_revision,
        "model_max_sequence_length": model_limit,
        "max_input_tokens": args.max_input_tokens,
        "overlap_tokens": args.overlap_tokens,
        "batch_size": args.batch_size,
        "normalized_embeddings": True,
        "similarity": "dot_product_equivalent_to_cosine",
        "source_records": len(sections),
        "chunks": len(chunks),
        "split_records": split_records,
        "vector_dimension": int(embeddings.shape[1]),
        "embeddings_dtype": str(embeddings.dtype),
        "embeddings_file": "embeddings.npy",
        "embeddings_sha256": sha256_file(embeddings_path),
        "chunks_file": "chunks.jsonl",
        "chunks_sha256": sha256_file(chunks_path),
        "packages": {
            "numpy": version("numpy"),
            "sentence-transformers": version("sentence-transformers"),
            "torch": version("torch"),
        },
    }
    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Index written to: {output_dir}")
    print(
        f"Records: {len(sections)} | Chunks: {len(chunks)} | "
        f"Split records: {split_records} | "
        f"Dimensions: {embeddings.shape[1]}"
    )
    return manifest


if __name__ == "__main__":
    build_index(parse_args())
