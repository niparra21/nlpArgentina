"""Shared utilities for the local semantic retrieval baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SNAPSHOT_ID = "2026-07-23"
DEFAULT_MODEL_NAME = "intfloat/multilingual-e5-small"
DEFAULT_MODEL_REVISION = "614241f622f53c4eeff9890bdc4f31cfecc418b3"
DEFAULT_MAX_INPUT_TOKENS = 480
DEFAULT_OVERLAP_TOKENS = 50
TOKENIZATION_SAFETY_TOKENS = 8
INDEX_SCHEMA_VERSION = "1.0.0"


def model_slug(model_name: str) -> str:
    """Return a filesystem-friendly short model name."""

    return model_name.rstrip("/").rsplit("/", 1)[-1]


def default_sections_path(snapshot_id: str) -> Path:
    return (
        ROOT
        / "data"
        / "processed"
        / "tec"
        / snapshot_id
        / "sections.jsonl"
    )


def default_index_dir(snapshot_id: str, model_name: str) -> Path:
    return (
        ROOT
        / "data"
        / "indexes"
        / "tec"
        / snapshot_id
        / model_slug(model_name)
    )


def default_results_dir(snapshot_id: str, model_name: str) -> Path:
    return (
        ROOT
        / "results"
        / "retrieval"
        / snapshot_id
        / model_slug(model_name)
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read a UTF-8 JSON Lines file."""

    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    """Write dictionaries as deterministic UTF-8 JSON Lines."""

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
            handle.write("\n")


def sha256_file(path: Path) -> str:
    """Calculate the SHA-256 checksum of a file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def embedding_header(section: dict[str, Any]) -> str:
    """Create the contextual header prepended to every legal passage."""

    labels = [
        section.get("document_title", ""),
        section.get("chapter_label", ""),
        section.get("section_label", ""),
    ]
    context = "\n".join(label.strip() for label in labels if label.strip())
    return f"passage: {context}\n\n"


def _special_token_count(tokenizer: Any) -> int:
    counter = getattr(tokenizer, "num_special_tokens_to_add", None)
    if counter is None:
        return 0
    return int(counter(pair=False))


def chunk_section(
    section: dict[str, Any],
    tokenizer: Any,
    *,
    max_input_tokens: int = DEFAULT_MAX_INPUT_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[dict[str, Any]]:
    """Split one section into model-sized passages while retaining provenance."""

    if max_input_tokens <= 0:
        raise ValueError("max_input_tokens must be positive")
    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative")

    header = embedding_header(section)
    header_ids = tokenizer.encode(
        header,
        add_special_tokens=False,
        truncation=False,
    )
    body_ids = tokenizer.encode(
        section["text"],
        add_special_tokens=False,
        truncation=False,
    )
    body_capacity = (
        max_input_tokens
        - len(header_ids)
        - _special_token_count(tokenizer)
        - TOKENIZATION_SAFETY_TOKENS
    )
    if body_capacity <= overlap_tokens:
        raise ValueError(
            "The contextual header leaves no room for a passage. "
            "Increase max_input_tokens or reduce overlap_tokens."
        )

    slices: list[list[Any]] = []
    start = 0
    while start < len(body_ids):
        end = min(start + body_capacity, len(body_ids))
        slices.append(body_ids[start:end])
        if end == len(body_ids):
            break
        start = end - overlap_tokens

    chunks: list[dict[str, Any]] = []
    chunk_count = len(slices)
    for chunk_index, token_slice in enumerate(slices, start=1):
        chunk_text = tokenizer.decode(
            token_slice,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        ).strip()
        embedding_text = f"{header}{chunk_text}"
        actual_tokens = len(
            tokenizer.encode(
                embedding_text,
                add_special_tokens=True,
                truncation=False,
            )
        )
        if actual_tokens > max_input_tokens:
            raise ValueError(
                f"{section['record_id']} produced a {actual_tokens}-token "
                f"chunk; the configured maximum is {max_input_tokens}."
            )

        chunks.append(
            {
                "chunk_id": (
                    f"{section['record_id']}::chunk-{chunk_index:03d}"
                ),
                "chunk_index": chunk_index,
                "chunk_count": chunk_count,
                "record_id": section["record_id"],
                "record_type": section["record_type"],
                "document_id": section["document_id"],
                "document_title": section["document_title"],
                "chapter_label": section["chapter_label"],
                "section_label": section["section_label"],
                "citation_label": section["citation_label"],
                "source_url": section["source_url"],
                "snapshot_id": section["snapshot_id"],
                "content_sha256": section["content_sha256"],
                "token_count": actual_tokens,
                "text": chunk_text,
                "embedding_text": embedding_text,
            }
        )
    return chunks


def build_chunks(
    sections: Iterable[dict[str, Any]],
    tokenizer: Any,
    *,
    max_input_tokens: int = DEFAULT_MAX_INPUT_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[dict[str, Any]]:
    """Create embedding passages for all processed sections."""

    chunks: list[dict[str, Any]] = []
    for section in sections:
        chunks.extend(
            chunk_section(
                section,
                tokenizer,
                max_input_tokens=max_input_tokens,
                overlap_tokens=overlap_tokens,
            )
        )
    return chunks


def load_index(
    index_dir: Path,
) -> tuple[np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    """Load and validate an embeddings matrix, metadata and manifest."""

    embeddings_path = index_dir / "embeddings.npy"
    chunks_path = index_dir / "chunks.jsonl"
    manifest_path = index_dir / "index_manifest.json"
    for path in (embeddings_path, chunks_path, manifest_path):
        if not path.is_file():
            raise FileNotFoundError(f"Missing index artifact: {path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["schema_version"] != INDEX_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported index schema: "
            f"{manifest['schema_version']} (expected {INDEX_SCHEMA_VERSION})"
        )
    if sha256_file(embeddings_path) != manifest["embeddings_sha256"]:
        raise ValueError("The embeddings checksum does not match the manifest")
    if sha256_file(chunks_path) != manifest["chunks_sha256"]:
        raise ValueError("The chunks checksum does not match the manifest")

    embeddings = np.load(embeddings_path, allow_pickle=False)
    chunks = read_jsonl(chunks_path)
    if embeddings.ndim != 2:
        raise ValueError("The embeddings array must have two dimensions")
    if embeddings.shape[0] != len(chunks):
        raise ValueError("Embeddings and chunk metadata have different sizes")
    if embeddings.shape[1] != manifest["vector_dimension"]:
        raise ValueError("The vector dimension does not match the manifest")
    return embeddings, chunks, manifest


def rank_chunks(
    embeddings: np.ndarray,
    chunks: list[dict[str, Any]],
    query_vector: np.ndarray,
    *,
    top_k: int = 5,
    unique_records: bool = True,
) -> list[dict[str, Any]]:
    """Rank chunks by dot product, optionally keeping one per parent record."""

    if top_k <= 0:
        raise ValueError("top_k must be positive")
    vector = np.asarray(query_vector, dtype=np.float32).reshape(-1)
    if embeddings.shape[1] != vector.shape[0]:
        raise ValueError("Query and document vectors have different dimensions")

    scores = embeddings @ vector
    order = np.argsort(-scores, kind="stable")
    seen_records: set[str] = set()
    hits: list[dict[str, Any]] = []
    for position in order:
        chunk = chunks[int(position)]
        if unique_records and chunk["record_id"] in seen_records:
            continue
        seen_records.add(chunk["record_id"])
        hits.append(
            {
                "rank": len(hits) + 1,
                "score": float(scores[position]),
                **chunk,
            }
        )
        if len(hits) == top_k:
            break
    return hits


def encode_query(model: Any, question: str) -> np.ndarray:
    """Encode one E5 retrieval query as a normalized float32 vector."""

    vector = model.encode(
        [f"query: {question.strip()}"],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )[0]
    return np.asarray(vector, dtype=np.float32)


def search_question(
    model: Any,
    embeddings: np.ndarray,
    chunks: list[dict[str, Any]],
    question: str,
    *,
    top_k: int = 5,
) -> tuple[list[dict[str, Any]], float]:
    """Encode and search one question, returning hits and elapsed milliseconds."""

    started = perf_counter()
    query_vector = encode_query(model, question)
    hits = rank_chunks(
        embeddings,
        chunks,
        query_vector,
        top_k=top_k,
        unique_records=True,
    )
    elapsed_ms = (perf_counter() - started) * 1000
    return hits, elapsed_ms
