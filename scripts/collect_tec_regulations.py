"""Collect versioned snapshots of selected official TEC regulations."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "data" / "raw" / "tec"
TIMEZONE = ZoneInfo("America/Costa_Rica")
USER_AGENT = (
    "nlpArgentina-academic-corpus/1.0 "
    "(https://github.com/niparra21/nlpArgentina)"
)


@dataclass(frozen=True)
class Regulation:
    document_id: str
    filename: str
    title: str
    source_url: str
    effective_from: str
    last_known_modification: str
    required_markers: tuple[str, ...]
    notes: str


REGULATIONS = (
    Regulation(
        document_id="tec-rrea-2025",
        filename="tec-rrea-2025.html",
        title=(
            "Reglamento del Régimen Enseñanza-Aprendizaje del "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-regimen-ensenanza-aprendizaje-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="2025-01-01",
        last_known_modification="2025-08",
        required_markers=(
            "Entra en vigencia a partir del 01 de enero de 2025",
            "Artículo 95",
        ),
        notes=(
            "La página oficial indica vigencia desde enero de 2025 y "
            "última modificación en agosto de 2025."
        ),
    ),
    Regulation(
        document_id="tec-becas-prestamos",
        filename="tec-becas-prestamos.html",
        title=(
            "Reglamento de Becas y Préstamos Estudiantiles del "
            "Instituto Tecnológico de Costa Rica y sus Reformas"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-becas-prestamos-estudiantiles-"
            "instituto-tecnologico-costa-rica-sus-reformas"
        ),
        effective_from="",
        last_known_modification="2022-11",
        required_markers=(
            "Reglamento de Becas y Préstamos Estudiantiles",
            "Transitorio III",
        ),
        notes=(
            "La página no informa una fecha única de entrada en vigencia; "
            "el texto contiene reformas y transitorios con fechas propias."
        ),
    ),
    Regulation(
        document_id="tec-equiparacion-asignaturas",
        filename="tec-equiparacion-asignaturas.html",
        title=(
            "Reglamento de Equiparación de Asignaturas del "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-equiparacion-asignaturas-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="2023-03",
        last_known_modification="2026-04",
        required_markers=(
            "Reglamento para la Equiparación de Asignaturas",
            "Sesión n.° 3443",
        ),
        notes=(
            "La página oficial registra entrada en vigencia en marzo de "
            "2023 y última modificación en abril de 2026."
        ),
    ),
    Regulation(
        document_id="tec-residencias-estudiantiles",
        filename="tec-residencias-estudiantiles.html",
        title=(
            "Reglamento para el Funcionamiento del Programa de "
            "Residencias Estudiantiles del Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-funcionamiento-programa-residencias-"
            "estudiantiles-instituto-tecnologico-costa-rica"
        ),
        effective_from="2009-05",
        last_known_modification="2023-03",
        required_markers=(
            "Programa de Residencias Estudiantiles",
            "Sesión Ordinaria Número 3302",
        ),
        notes=(
            "Se seleccionó la página actual; la versión antigua del Sistema "
            "de Alojamiento está identificada como derogada."
        ),
    ),
    Regulation(
        document_id="tec-defensoria-estudiantil",
        filename="tec-defensoria-estudiantil.html",
        title="Reglamento de la Defensoría Estudiantil",
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-funcionamiento-defensoria-estudiantil"
        ),
        effective_from="2023-05-26",
        last_known_modification="2025-07",
        required_markers=(
            "Reglamento de Funcionamiento de la Defensoría Estudiantil",
            "Gaceta Número 1105-2023",
        ),
        notes=(
            "La página oficial registra creación en mayo de 2023 y última "
            "modificación en julio de 2025."
        ),
    ),
)


FORBIDDEN_MARKERS = (
    "Reglamento derogado",
    "Vigente hasta el 31 de diciembre de 2024",
)


def normalize_text(raw_html: bytes, charset: str) -> str:
    decoded = raw_html.decode(charset, errors="replace")
    decoded = re.sub(
        r"<(script|style)\b[^>]*>.*?</\1>",
        " ",
        decoded,
        flags=re.IGNORECASE | re.DOTALL,
    )
    decoded = re.sub(r"<[^>]+>", " ", decoded)
    return " ".join(html.unescape(decoded).split())


def extract_title(raw_html: bytes, charset: str) -> str:
    decoded = raw_html.decode(charset, errors="replace")
    match = re.search(
        r"<title[^>]*>(.*?)</title>",
        decoded,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ValueError("The HTML response has no title element")
    return " ".join(html.unescape(match.group(1)).split())


def extract_canonical(raw_html: bytes, charset: str) -> str:
    decoded = raw_html.decode(charset, errors="replace")
    tags = re.findall(r"<link\b[^>]*>", decoded, flags=re.IGNORECASE)
    for tag in tags:
        if not re.search(
            r"\brel\s*=\s*['\"]canonical['\"]", tag, flags=re.IGNORECASE
        ):
            continue
        match = re.search(
            r"\bhref\s*=\s*['\"]([^'\"]+)['\"]", tag, flags=re.IGNORECASE
        )
        if match:
            canonical = html.unescape(match.group(1))
            if canonical.startswith("http://www.tec.ac.cr/"):
                canonical = "https://" + canonical.removeprefix("http://")
            return canonical
    return ""


def ensure_official_url(url: str) -> None:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        raise ValueError(f"Non-HTTPS URL rejected: {url}")
    if host != "tec.ac.cr" and not host.endswith(".tec.ac.cr"):
        raise ValueError(f"Non-TEC domain rejected: {url}")


def collect(regulation: Regulation, destination: Path) -> dict[str, str | int]:
    ensure_official_url(regulation.source_url)
    request = Request(regulation.source_url, headers={"User-Agent": USER_AGENT})

    with urlopen(request, timeout=60) as response:
        final_url = response.geturl()
        ensure_official_url(final_url)
        status = response.status
        content_type = response.headers.get_content_type()
        charset = response.headers.get_content_charset() or "utf-8"
        raw_html = response.read()

    if status != 200:
        raise ValueError(f"{regulation.document_id}: HTTP status {status}")
    if content_type != "text/html":
        raise ValueError(
            f"{regulation.document_id}: expected text/html, got {content_type}"
        )

    page_title = extract_title(raw_html, charset)
    text = normalize_text(raw_html, charset)
    if regulation.title.casefold() not in page_title.casefold():
        raise ValueError(
            f"{regulation.document_id}: unexpected title {page_title!r}"
        )
    for marker in regulation.required_markers:
        if marker.casefold() not in text.casefold():
            raise ValueError(
                f"{regulation.document_id}: missing marker {marker!r}"
            )
    for marker in FORBIDDEN_MARKERS:
        if marker.casefold() in text.casefold():
            raise ValueError(
                f"{regulation.document_id}: forbidden marker {marker!r}"
            )

    destination.write_bytes(raw_html)
    relative_path = destination.relative_to(ROOT).as_posix()
    digest = hashlib.sha256(raw_html).hexdigest()
    return {
        "document_id": regulation.document_id,
        "title": regulation.title,
        "status": "vigente_en_sitio_oficial",
        "effective_from": regulation.effective_from,
        "last_known_modification": regulation.last_known_modification,
        "source_url": regulation.source_url,
        "canonical_url": extract_canonical(raw_html, charset),
        "final_url": final_url,
        "format": "html",
        "language": "es",
        "http_status": status,
        "content_type": content_type,
        "bytes": len(raw_html),
        "sha256": digest,
        "file": relative_path,
        "notes": regulation.notes,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and verify selected official TEC regulations."
    )
    parser.add_argument(
        "--snapshot-date",
        default=datetime.now(TIMEZONE).date().isoformat(),
        help="Snapshot directory date in YYYY-MM-DD format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        snapshot_date = datetime.strptime(
            args.snapshot_date, "%Y-%m-%d"
        ).date().isoformat()
    except ValueError:
        print("--snapshot-date must use YYYY-MM-DD", file=sys.stderr)
        return 2

    retrieved_at = datetime.now(TIMEZONE).isoformat(timespec="seconds")
    snapshot_dir = OUTPUT_ROOT / snapshot_date
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    if snapshot_dir.exists():
        print(
            f"Snapshot already exists; refusing to overwrite: {snapshot_dir}",
            file=sys.stderr,
        )
        return 1

    rows = []
    with tempfile.TemporaryDirectory(
        dir=OUTPUT_ROOT, prefix=f".{snapshot_date}-"
    ) as temporary_directory:
        staging_dir = Path(temporary_directory)
        try:
            for regulation in REGULATIONS:
                destination = staging_dir / regulation.filename
                print(f"Collecting {regulation.document_id} ...")
                row = collect(regulation, destination)
                row["file"] = (
                    snapshot_dir / regulation.filename
                ).relative_to(ROOT).as_posix()
                row["snapshot_date"] = snapshot_date
                row["retrieved_at"] = retrieved_at
                rows.append(row)
        except Exception as exc:
            print(f"Collection failed: {exc}", file=sys.stderr)
            return 1

        fieldnames = (
            "document_id",
            "title",
            "status",
            "effective_from",
            "last_known_modification",
            "source_url",
            "canonical_url",
            "final_url",
            "snapshot_date",
            "retrieved_at",
            "format",
            "language",
            "http_status",
            "content_type",
            "bytes",
            "sha256",
            "file",
            "notes",
        )
        manifest_path = staging_dir / "manifest.csv"
        with manifest_path.open(
            "w", encoding="utf-8-sig", newline=""
        ) as manifest:
            writer = csv.DictWriter(manifest, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        staging_dir.replace(snapshot_dir)

    print(f"Wrote {len(rows)} regulations to {snapshot_dir}")
    print(f"Manifest: {snapshot_dir / 'manifest.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
