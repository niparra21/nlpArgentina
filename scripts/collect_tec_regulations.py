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
    Regulation(
        document_id="tec-becas-posgrado",
        filename="tec-becas-posgrado.html",
        title=(
            "Reglamento de becas de posgrado del "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-becas-posgrado-instituto-tecnologico-costa-rica"
        ),
        effective_from="2023-06",
        last_known_modification="",
        required_markers=(
            "REGLAMENTO DE BECAS DE POSGRADO",
            "Artículo 1",
        ),
        notes=(
            "Reglamento estudiantil de alcance institucional para personas "
            "matriculadas en programas de posgrado."
        ),
    ),
    Regulation(
        document_id="tec-convivencia-disciplina",
        filename="tec-convivencia-disciplina.html",
        title=(
            "Reglamento de Convivencia y Régimen disciplinario para la "
            "Comunidad Estudiantil"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-convivencia-regimen-disciplinario-comunidad-"
            "estudiantil-instituto-tecnologico-costa-rica"
        ),
        effective_from="2022-08-01",
        last_known_modification="2023-11",
        required_markers=(
            "Reglamento de Convivencia y Régimen disciplinario",
            "Artículo 1",
        ),
        notes=(
            "Regula derechos, deberes, convivencia y procedimientos "
            "disciplinarios de la comunidad estudiantil."
        ),
    ),
    Regulation(
        document_id="tec-admision-grado",
        filename="tec-admision-grado.html",
        title=(
            "Reglamento de Admisión a Carreras de Grado en el "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-admision-carreras-grado-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="2022-10",
        last_known_modification="2025-10",
        required_markers=(
            "Reglamento de Admisión a Carreras de Grado",
            "Artículo 1",
        ),
        notes=(
            "La página oficial registra una modificación en octubre de 2025."
        ),
    ),
    Regulation(
        document_id="tec-prueba-aptitud",
        filename="tec-prueba-aptitud.html",
        title=(
            "Reglamento de la prueba de aptitud académica del "
            "Instituto Tecnológico de Costa Rica y sus reformas"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-prueba-aptitud-academica-instituto-tecnologico-"
            "costa-rica-sus-reformas-asi-reformado"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Reglamento de la prueba de aptitud académica",
            "Artículo 1",
        ),
        notes=(
            "Regula la organización y aplicación de la prueba de admisión."
        ),
    ),
    Regulation(
        document_id="tec-graduacion",
        filename="tec-graduacion.html",
        title=(
            "Reglamento de Normas Generales de Graduación en el "
            "Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-normas-generales-graduacion-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Reglamento de Normas Generales de Graduación",
            "Artículo 1",
        ),
        notes=(
            "Establece las normas institucionales para graduación y diplomas."
        ),
    ),
    Regulation(
        document_id="tec-tfg-grado",
        filename="tec-tfg-grado.html",
        title=(
            "Reforma Integral al Reglamento de Trabajos Finales de "
            "Graduación para programas de grado del ITCR"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reforma-integral-reglamento-trabajos-finales-graduacion-"
            "programas-grado-itcr"
        ),
        effective_from="2022-03",
        last_known_modification="",
        required_markers=(
            "Reglamento de Trabajos Finales de Graduación",
            "Artículo 1",
        ),
        notes=(
            "Se seleccionó la reforma integral vigente y se excluyó la "
            "versión anterior marcada como derogada."
        ),
    ),
    Regulation(
        document_id="tec-reconocimiento-grados-titulos",
        filename="tec-reconocimiento-grados-titulos.html",
        title=(
            "Reglamento para el Reconocimiento y Equiparación de Grados "
            "y Títulos Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-reconocimiento-equiparacion-grados-titulos-"
            "tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Reconocimiento y Equiparación de Grados y Títulos",
            "Artículo 1",
        ),
        notes=(
            "Regula el reconocimiento de grados y títulos obtenidos en "
            "otras instituciones."
        ),
    ),
    Regulation(
        document_id="tec-horas-estudiante-asistente",
        filename="tec-horas-estudiante-asistente.html",
        title=(
            "Reglamento para la Asignación de Horas Estudiante y Horas "
            "Asistente en el Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-asignacion-horas-estudiante-horas-asistente-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="2022-03",
        required_markers=(
            "Asignación de Horas Estudiante y Horas Asistente",
            "Artículo 1",
        ),
        notes=(
            "Regula requisitos, funciones y beneficios de horas estudiante "
            "y horas asistente."
        ),
    ),
    Regulation(
        document_id="tec-beca-asistente-especial",
        filename="tec-beca-asistente-especial.html",
        title=(
            "Reglamento de Beca del Estudiante Asistente Especial del "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-beca-estudiante-asistente-especial-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Beca del Estudiante Asistente Especial",
            "Artículo 1",
        ),
        notes=(
            "Regula la beca y las funciones de la persona estudiante "
            "asistente especial."
        ),
    ),
    Regulation(
        document_id="tec-beca-asistente-investigacion",
        filename="tec-beca-asistente-investigacion.html",
        title=(
            "Normativa de Beca del Estudiante Asistente para Proyectos "
            "de Investigación y Extensión"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "normativa-beca-estudiante-asistente-proyectos-"
            "investigacion-extension"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Beca del Estudiante Asistente para Proyectos",
            "Artículo 1",
        ),
        notes=(
            "Norma los apoyos estudiantiles vinculados con proyectos de "
            "investigación y extensión."
        ),
    ),
    Regulation(
        document_id="tec-fondo-solidario",
        filename="tec-fondo-solidario.html",
        title=(
            "Reglamento del Fondo Solidario de Desarrollo Estudiantil del "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-fondo-solidario-desarrollo-estudiantil-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Fondo Solidario de Desarrollo Estudiantil",
            "Artículo 1",
        ),
        notes=(
            "Regula recursos institucionales destinados al desarrollo y "
            "apoyo socioeconómico estudiantil."
        ),
    ),
    Regulation(
        document_id="tec-financiamiento-exterior",
        filename="tec-financiamiento-exterior.html",
        title=(
            "Reglamento del Fondo de Financiamiento de Actividades en el "
            "Exterior para Estudiantes de Diplomado y Bachillerato"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-fondo-financiamiento-actividades-exterior-"
            "estudiantes-diplomado-bachillerato"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Fondo de Financiamiento de Actividades en el Exterior",
            "Artículo 1",
        ),
        notes=(
            "Regula ayudas para participación estudiantil en actividades "
            "académicas en el exterior."
        ),
    ),
    Regulation(
        document_id="tec-beca-mauricio-campos",
        filename="tec-beca-mauricio-campos.html",
        title=(
            "Reglamento del Fundamento Humanístico de la Beca Mauricio "
            "Campos del Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-fundamento-humanistico-beca-mauricio-campos-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Beca Mauricio Campos",
            "Artículo 1",
        ),
        notes=(
            "Regula el beneficio y las obligaciones asociadas con la Beca "
            "Mauricio Campos."
        ),
    ),
    Regulation(
        document_id="tec-codigo-electoral-estudiantil",
        filename="tec-codigo-electoral-estudiantil.html",
        title="Código Electoral Estudiantil del Tecnológico de Costa Rica",
        source_url=(
            "https://www.tec.ac.cr/"
            "codigo-electoral-estudiantil-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Código Electoral Estudiantil",
            "Artículo 1",
        ),
        notes=(
            "Regula los procesos electorales y la representación estudiantil."
        ),
    ),
    Regulation(
        document_id="tec-reglamento-superior-feitec",
        filename="tec-reglamento-superior-feitec.html",
        title=(
            "Reglamento Superior de la Federación de Estudiantes del "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-superior-federacion-estudiantes-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Reglamento Superior de la Federación de Estudiantes",
            "Artículo 1",
        ),
        notes=(
            "Regula la estructura y funcionamiento general de la FEITEC."
        ),
    ),
    Regulation(
        document_id="tec-directorio-asambleas-estudiantiles",
        filename="tec-directorio-asambleas-estudiantiles.html",
        title=(
            "Reglamento del Directorio de Asambleas Estudiantiles, "
            "Plenario de Asociaciones y Asamblea General de Estudiantes"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-directorio-asambleas-estudiantiles-plenario-"
            "asociaciones-asamblea-general-estudiantes"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Directorio de Asambleas Estudiantiles",
            "Artículo 1",
        ),
        notes=(
            "Regula las asambleas, asociaciones y órganos deliberativos "
            "estudiantiles."
        ),
    ),
    Regulation(
        document_id="tec-correo-electronico",
        filename="tec-correo-electronico.html",
        title=(
            "Reglamento de uso del correo electrónico del "
            "Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-uso-correo-electronico-"
            "instituto-tecnologico-costa-rica"
        ),
        effective_from="",
        last_known_modification="2025-04",
        required_markers=(
            "Reglamento de uso del correo electrónico",
            "Artículo 1",
        ),
        notes=(
            "Aplica a las cuentas institucionales de personas estudiantes "
            "y funcionarias."
        ),
    ),
    Regulation(
        document_id="tec-hostigamiento-sexual",
        filename="tec-hostigamiento-sexual.html",
        title=(
            "Reglamento Contra El Hostigamiento Sexual en el Empleo y la "
            "Academia en el Instituto Tecnológico de Costa Rica"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-hostigamiento-sexual-empleo-academia-"
            "instituto-tecnologico-costa-rica-0"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Hostigamiento Sexual en el Empleo y la Academia",
            "Artículo 1",
        ),
        notes=(
            "Regula prevención, denuncia e investigación del hostigamiento "
            "sexual en ámbitos laborales y académicos."
        ),
    ),
    Regulation(
        document_id="tec-no-discriminacion",
        filename="tec-no-discriminacion.html",
        title=(
            "Reglamento contra la discriminación por orientación sexual e "
            "identidad de género del ITCR"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-instituto-tecnologico-costa-rica-discriminacion-"
            "orientacion-sexual-identidad-expresion"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "discriminación por orientación sexual",
            "Artículo 1",
        ),
        notes=(
            "Establece medidas y procedimientos contra la discriminación "
            "en la comunidad institucional."
        ),
    ),
    Regulation(
        document_id="tec-tercer-representante-estudiantil",
        filename="tec-tercer-representante-estudiantil.html",
        title=(
            "Reglamento para la Elección del Tercer Representante y Tercer "
            "Suplente Estudiantil ante el Consejo Institucional"
        ),
        source_url=(
            "https://www.tec.ac.cr/"
            "reglamento-eleccion-tercer-representante-tercer-suplente-"
            "estudiantil-consejo-institucional"
        ),
        effective_from="",
        last_known_modification="",
        required_markers=(
            "Tercer Representante y Tercer Suplente Estudiantil",
            "Artículo 1",
        ),
        notes=(
            "Regula esta elección de representación estudiantil ante el "
            "Consejo Institucional."
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
        help="Retrieval date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--snapshot-id",
        help=(
            "Snapshot directory identifier. Defaults to the snapshot date; "
            "may add a lowercase suffix if more than one snapshot is "
            "collected on the same date."
        ),
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

    snapshot_id = args.snapshot_id or snapshot_date
    snapshot_id_pattern = rf"{re.escape(snapshot_date)}(?:-[a-z0-9]+)*"
    if not re.fullmatch(snapshot_id_pattern, snapshot_id):
        print(
            "--snapshot-id must begin with --snapshot-date and contain "
            "only lowercase letters, numbers, and hyphens",
            file=sys.stderr,
        )
        return 2

    retrieved_at = datetime.now(TIMEZONE).isoformat(timespec="seconds")
    snapshot_dir = OUTPUT_ROOT / snapshot_id
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    if snapshot_dir.exists():
        print(
            f"Snapshot already exists; refusing to overwrite: {snapshot_dir}",
            file=sys.stderr,
        )
        return 1

    rows = []
    with tempfile.TemporaryDirectory(
        dir=OUTPUT_ROOT, prefix=f".{snapshot_id}-"
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
                row["snapshot_id"] = snapshot_id
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
            "snapshot_id",
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
