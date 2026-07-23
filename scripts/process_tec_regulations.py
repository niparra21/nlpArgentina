"""Transform raw TEC regulation snapshots into traceable JSONL sections."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, Tag


ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = ROOT / "data" / "raw" / "tec"
PROCESSED_ROOT = ROOT / "data" / "processed" / "tec"
TIMEZONE = ZoneInfo("America/Costa_Rica")
PARSER_VERSION = "1.1.0"
HEADING_TAGS = {"h2", "h3", "h4", "h5", "h6"}

ARTICLE_RE = re.compile(
    r"^art[ií]culo\s+"
    r"(?P<number>\d+(?:\s*(?:-\s*)?"
    r"(?:bis(?:-\d+)?|ter|quater|quinquies|sexies|septies|octies|"
    r"nonies|decies))?)"
    r"\s*(?:[.:]\s*)?(?P<title>.*)$",
    re.IGNORECASE,
)
TRANSITORY_RE = re.compile(
    r"^transitorio\s+(?P<number>[IVXLCDM]+|\d+)"
    r"\s*(?:[.:]\s*)?(?P<title>.*)$",
    re.IGNORECASE,
)
CHAPTER_RE = re.compile(
    r"^(?:t[ií]tulo\s+[IVXLCDM\d]+\s*(?:[.:\-]\s*)?.*?\s+)?"
    r"cap[ií]tulo\s+"
    r"(?P<number>[IVXLCDM]+|\d+(?:\s+bis)?|[uú]nic[oa])"
    r"\s*(?:[.:\-]\s*)?(?P<title>.*)$",
    re.IGNORECASE,
)

EXPECTED_COUNTS = {
    "tec-rrea-2025": {"article": 95, "transitory": 2},
    "tec-becas-prestamos": {"article": 56, "transitory": 3},
    "tec-equiparacion-asignaturas": {"article": 34, "transitory": 0},
    "tec-residencias-estudiantiles": {"article": 29, "transitory": 2},
    "tec-defensoria-estudiantil": {"article": 30, "transitory": 0},
    "tec-becas-posgrado": {"article": 24, "transitory": 3},
    "tec-convivencia-disciplina": {"article": 42, "transitory": 4},
    "tec-admision-grado": {"article": 43, "transitory": 1},
    "tec-prueba-aptitud": {"article": 31, "transitory": 1},
    "tec-graduacion": {"article": 27, "transitory": 0},
    "tec-tfg-grado": {"article": 26, "transitory": 0},
    "tec-reconocimiento-grados-titulos": {
        "article": 33,
        "transitory": 2,
    },
    "tec-horas-estudiante-asistente": {
        "article": 32,
        "transitory": 1,
    },
    "tec-beca-asistente-especial": {"article": 33, "transitory": 0},
    "tec-beca-asistente-investigacion": {
        "article": 14,
        "transitory": 0,
    },
    "tec-fondo-solidario": {"article": 19, "transitory": 1},
    "tec-financiamiento-exterior": {"article": 23, "transitory": 0},
    "tec-beca-mauricio-campos": {"article": 22, "transitory": 0},
    "tec-codigo-electoral-estudiantil": {
        "article": 146,
        "transitory": 0,
    },
    "tec-reglamento-superior-feitec": {
        "article": 136,
        "transitory": 6,
    },
    "tec-directorio-asambleas-estudiantiles": {
        "article": 101,
        "transitory": 3,
    },
    "tec-correo-electronico": {"article": 28, "transitory": 4},
    "tec-hostigamiento-sexual": {"article": 40, "transitory": 2},
    "tec-no-discriminacion": {"article": 47, "transitory": 7},
    "tec-tercer-representante-estudiantil": {
        "article": 30,
        "transitory": 1,
    },
}

INITIAL_DOCUMENT_IDS = {
    "tec-rrea-2025",
    "tec-becas-prestamos",
    "tec-equiparacion-asignaturas",
    "tec-residencias-estudiantiles",
    "tec-defensoria-estudiantil",
}
EXPANDED_DOCUMENT_IDS = set(EXPECTED_COUNTS)


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    title: str
    source_url: str
    canonical_url: str
    snapshot_date: str
    snapshot_id: str
    profile: str
    retrieved_at: str
    effective_from: str
    last_known_modification: str
    raw_file: str
    raw_sha256: str


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def normalize_visible_text(node: Tag) -> str:
    return " ".join(node.get_text(" ", strip=True).replace("\xa0", " ").split())


def normalize_identifier(value: str) -> str:
    value = value.strip().casefold()
    value = re.sub(r"\s*-\s*", "-", value)
    value = re.sub(r"\s+", "-", value)
    return value


def is_structural_heading(value: str) -> bool:
    return (
        value.isupper()
        or bool(
            re.match(
                r"^(?:t[ií]tulo|disposiciones|secci[oó]n)\b",
                value,
                flags=re.IGNORECASE,
            )
        )
    )


def load_sources(snapshot_id: str) -> list[SourceDocument]:
    manifest_path = RAW_ROOT / snapshot_id / "manifest.csv"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Raw manifest not found: {manifest_path}")

    sources: list[SourceDocument] = []
    with manifest_path.open(encoding="utf-8-sig", newline="") as manifest:
        for row in csv.DictReader(manifest):
            raw_path = (ROOT / row["file"]).resolve()
            if not raw_path.is_relative_to(ROOT):
                raise ValueError(
                    f"Raw file escapes repository: {row['file']}"
                )
            if not raw_path.is_file():
                raise FileNotFoundError(f"Raw file not found: {raw_path}")
            raw_sha256 = sha256_bytes(raw_path.read_bytes())
            if raw_sha256 != row["sha256"]:
                raise ValueError(
                    f"Raw SHA-256 mismatch for {row['document_id']}"
                )
            row_snapshot_id = row.get("snapshot_id") or row["snapshot_date"]
            if row_snapshot_id != snapshot_id:
                raise ValueError(
                    f"Snapshot mismatch for {row['document_id']}: "
                    f"{row_snapshot_id}"
                )
            sources.append(
                SourceDocument(
                    document_id=row["document_id"],
                    title=row["title"],
                    source_url=row["source_url"],
                    canonical_url=row["canonical_url"],
                    snapshot_date=row["snapshot_date"],
                    snapshot_id=row_snapshot_id,
                    profile=row.get("profile") or "initial",
                    retrieved_at=row["retrieved_at"],
                    effective_from=row["effective_from"],
                    last_known_modification=row[
                        "last_known_modification"
                    ],
                    raw_file=row["file"],
                    raw_sha256=row["sha256"],
                )
            )

    actual_documents = {source.document_id for source in sources}
    supported_document_sets = (
        INITIAL_DOCUMENT_IDS,
        EXPANDED_DOCUMENT_IDS,
    )
    if actual_documents not in supported_document_sets:
        raise ValueError(
            "Unexpected document set. Expected the initial or expanded "
            f"profile, found {sorted(actual_documents)}"
        )
    profiles = {source.profile for source in sources}
    if len(profiles) != 1:
        raise ValueError(f"Mixed collection profiles: {sorted(profiles)}")
    return sources


def select_normative_body(soup: BeautifulSoup, document_id: str) -> Tag:
    candidates = soup.select(".field--name-body")
    if not candidates:
        raise ValueError(
            f"{document_id}: no .field--name-body element found"
        )
    body = max(candidates, key=lambda node: len(normalize_visible_text(node)))
    if not body.find(HEADING_TAGS):
        raise ValueError(f"{document_id}: normative body has no headings")
    return body


def build_record(
    source: SourceDocument,
    record_type: str,
    section_number: str,
    section_label: str,
    section_title: str,
    sequence: int,
    chapter_number: str,
    chapter_title: str,
    chapter_label: str,
    text_blocks: list[str],
) -> dict[str, Any]:
    text = "\n\n".join(block for block in text_blocks if block)
    normalized_id = normalize_identifier(section_number)
    prefix = "article" if record_type == "article" else "transitory"
    record_id = f"{source.document_id}::{prefix}-{normalized_id}"
    article_number = normalized_id if record_type == "article" else None
    article_title = section_title if record_type == "article" else None
    citation_label = f"{source.title}, {section_label}"
    return {
        "record_id": record_id,
        "record_type": record_type,
        "document_id": source.document_id,
        "document_title": source.title,
        "sequence": sequence,
        "chapter_number": chapter_number or None,
        "chapter_title": chapter_title or None,
        "chapter_label": chapter_label or None,
        "section_label": section_label,
        "article_number": article_number,
        "article_title": article_title,
        "text": text,
        "citation_label": citation_label,
        "source_url": source.source_url,
        "canonical_url": source.canonical_url,
        "snapshot_date": source.snapshot_date,
        "snapshot_id": source.snapshot_id,
        "collection_profile": source.profile,
        "retrieved_at": source.retrieved_at,
        "effective_from": source.effective_from or None,
        "last_known_modification": (
            source.last_known_modification or None
        ),
        "raw_file": source.raw_file,
        "raw_sha256": source.raw_sha256,
        "content_sha256": sha256_bytes(text.encode("utf-8")),
        "character_count": len(text),
        "word_count": len(re.findall(r"\b\w+\b", text, flags=re.UNICODE)),
        "parser_version": PARSER_VERSION,
    }


def parse_document(source: SourceDocument) -> list[dict[str, Any]]:
    raw_path = ROOT / source.raw_file
    soup = BeautifulSoup(raw_path.read_bytes(), "html.parser")
    body = select_normative_body(soup, source.document_id)

    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    chapter_number = ""
    chapter_title = ""
    chapter_label = ""
    chapter_waiting_for_title = False

    def flush_current() -> None:
        nonlocal current
        if current is None:
            return
        records.append(
            build_record(
                source=source,
                record_type=current["record_type"],
                section_number=current["section_number"],
                section_label=current["section_label"],
                section_title=current["section_title"],
                sequence=len(records) + 1,
                chapter_number=current["chapter_number"],
                chapter_title=current["chapter_title"],
                chapter_label=current["chapter_label"],
                text_blocks=current["text_blocks"],
            )
        )
        current = None

    for child in body.children:
        if not isinstance(child, Tag):
            continue
        visible_text = normalize_visible_text(child)
        if not visible_text:
            continue
        is_heading = child.name in HEADING_TAGS

        if is_heading:
            chapter_match = CHAPTER_RE.match(visible_text)
            if chapter_match:
                flush_current()
                chapter_number = normalize_identifier(
                    chapter_match.group("number")
                ).upper()
                chapter_title = chapter_match.group("title").strip()
                chapter_label = visible_text
                chapter_waiting_for_title = not bool(chapter_title)
                continue

        article_match = ARTICLE_RE.match(visible_text)
        if article_match:
            flush_current()
            inline_text = article_match.group("title").strip()
            if is_heading:
                section_label = visible_text
                section_title = inline_text
                text_blocks: list[str] = []
            else:
                section_label = visible_text[
                    : article_match.start("title")
                ].rstrip(" .:")
                section_title = ""
                text_blocks = [inline_text] if inline_text else []
            current = {
                "record_type": "article",
                "section_number": article_match.group("number"),
                "section_label": section_label,
                "section_title": section_title,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "chapter_label": chapter_label,
                "text_blocks": text_blocks,
            }
            chapter_waiting_for_title = False
            continue

        transitory_match = TRANSITORY_RE.match(visible_text)
        if transitory_match:
            flush_current()
            inline_text = transitory_match.group("title").strip()
            if is_heading:
                section_label = visible_text
                section_title = inline_text
                text_blocks = []
            else:
                section_label = visible_text[
                    : transitory_match.start("title")
                ].rstrip(" .:")
                section_title = ""
                text_blocks = [inline_text] if inline_text else []
            current = {
                "record_type": "transitory",
                "section_number": transitory_match.group("number"),
                "section_label": section_label,
                "section_title": section_title,
                "chapter_number": chapter_number,
                "chapter_title": chapter_title,
                "chapter_label": chapter_label,
                "text_blocks": text_blocks,
            }
            chapter_waiting_for_title = False
            continue

        if is_heading and chapter_waiting_for_title and current is None:
            chapter_title = visible_text
            chapter_label = f"{chapter_label} {visible_text}"
            chapter_waiting_for_title = False
            continue

        if is_heading and is_structural_heading(visible_text):
            flush_current()
            chapter_number = ""
            chapter_title = visible_text
            chapter_label = visible_text
            chapter_waiting_for_title = False
            continue

        if current is not None:
            current["text_blocks"].append(visible_text)

    flush_current()
    return records


def validate_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    record_ids = [record["record_id"] for record in records]
    duplicates = sorted(
        record_id
        for record_id in set(record_ids)
        if record_ids.count(record_id) > 1
    )
    if duplicates:
        raise ValueError(f"Duplicate record IDs: {duplicates}")

    empty_records = [
        record["record_id"] for record in records if not record["text"].strip()
    ]
    if empty_records:
        raise ValueError(f"Empty section text: {empty_records}")

    document_stats: list[dict[str, Any]] = []
    present_document_ids = {
        record["document_id"] for record in records
    }
    for document_id, expected in EXPECTED_COUNTS.items():
        if document_id not in present_document_ids:
            continue
        document_records = [
            record
            for record in records
            if record["document_id"] == document_id
        ]
        actual = {
            "article": sum(
                record["record_type"] == "article"
                for record in document_records
            ),
            "transitory": sum(
                record["record_type"] == "transitory"
                for record in document_records
            ),
        }
        if actual != expected:
            raise ValueError(
                f"Unexpected section counts for {document_id}: "
                f"expected {expected}, found {actual}"
            )
        document_stats.append(
            {
                "document_id": document_id,
                "articles": actual["article"],
                "transitories": actual["transitory"],
                "records": len(document_records),
                "characters": sum(
                    record["character_count"] for record in document_records
                ),
                "words": sum(
                    record["word_count"] for record in document_records
                ),
            }
        )

    return {
        "records": len(records),
        "articles": sum(
            record["record_type"] == "article" for record in records
        ),
        "transitories": sum(
            record["record_type"] == "transitory" for record in records
        ),
        "documents": document_stats,
    }


def write_outputs(
    snapshot_id: str,
    sources: list[SourceDocument],
    records: list[dict[str, Any]],
    stats: dict[str, Any],
) -> tuple[Path, Path]:
    output_dir = PROCESSED_ROOT / snapshot_id
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        dir=output_dir, prefix=".processing-"
    ) as temporary_directory:
        staging_dir = Path(temporary_directory)
        sections_path = staging_dir / "sections.jsonl"
        with sections_path.open("w", encoding="utf-8", newline="\n") as output:
            for record in records:
                output.write(
                    json.dumps(record, ensure_ascii=False, sort_keys=True)
                )
                output.write("\n")

        sections_bytes = sections_path.read_bytes()
        generated_at = datetime.now(TIMEZONE).isoformat(timespec="seconds")
        snapshot_dates = {source.snapshot_date for source in sources}
        if len(snapshot_dates) != 1:
            raise ValueError(
                f"Mixed snapshot dates: {sorted(snapshot_dates)}"
            )
        processing_manifest = {
            "parser_version": PARSER_VERSION,
            "generated_at": generated_at,
            "snapshot_date": next(iter(snapshot_dates)),
            "snapshot_id": snapshot_id,
            "collection_profile": sources[0].profile,
            "input_manifest": (
                RAW_ROOT / snapshot_id / "manifest.csv"
            ).relative_to(ROOT).as_posix(),
            "output_file": (
                output_dir / "sections.jsonl"
            ).relative_to(ROOT).as_posix(),
            "output_sha256": sha256_bytes(sections_bytes),
            "statistics": stats,
            "source_documents": [
                {
                    "document_id": source.document_id,
                    "raw_file": source.raw_file,
                    "raw_sha256": source.raw_sha256,
                    "source_url": source.source_url,
                }
                for source in sources
            ],
            "validation": {
                "input_sha256_verified": True,
                "unique_record_ids": True,
                "nonempty_sections": True,
                "expected_counts_verified": True,
            },
        }
        manifest_path = staging_dir / "processing_manifest.json"
        manifest_path.write_text(
            json.dumps(
                processing_manifest,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
            newline="\n",
        )

        final_sections = output_dir / "sections.jsonl"
        final_manifest = output_dir / "processing_manifest.json"
        sections_path.replace(final_sections)
        manifest_path.replace(final_manifest)

    return final_sections, final_manifest


def process_snapshot(
    snapshot_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sources = load_sources(snapshot_id)
    records: list[dict[str, Any]] = []
    for source in sources:
        records.extend(parse_document(source))
    stats = validate_records(records)
    return records, stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract traceable articles from raw TEC regulations."
    )
    parser.add_argument(
        "--snapshot-id",
        "--snapshot-date",
        dest="snapshot_id",
        required=True,
        help=(
            "Raw snapshot directory identifier. --snapshot-date remains "
            "available as a backwards-compatible alias."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        snapshot_id = args.snapshot_id
        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}(?:-[a-z0-9]+)*",
            snapshot_id,
        ):
            raise ValueError("invalid snapshot identifier")
        sources = load_sources(snapshot_id)
        records: list[dict[str, Any]] = []
        for source in sources:
            document_records = parse_document(source)
            print(
                f"{source.document_id}: "
                f"{len(document_records)} sections"
            )
            records.extend(document_records)
        stats = validate_records(records)
        sections_path, manifest_path = write_outputs(
            snapshot_id, sources, records, stats
        )
    except Exception as exc:
        print(f"Processing failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Wrote {stats['records']} sections: "
        f"{stats['articles']} articles and "
        f"{stats['transitories']} transitories"
    )
    print(f"Sections: {sections_path}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
