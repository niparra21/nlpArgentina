# Corpus procesado de normativa estudiantil del TEC

Esta carpeta contiene datos derivados de las capturas inalteradas almacenadas en
`data/raw/tec/`. A diferencia de los HTML originales, estos archivos sí pueden
regenerarse ejecutando el procesador.

## Salidas

Cada carpeta fechada contiene:

- `sections.jsonl`: un objeto JSON por artículo o transitorio.
- `processing_manifest.json`: versión del procesador, hashes, conteos y
  trazabilidad de entradas y salidas.

Las salidas disponibles son:

- `2026-07-23`: 5 documentos y 251 secciones.
- `2026-07-23-expanded`: 25 documentos y 1 184 secciones.

## Esquema de una sección

Los campos principales son:

| Campo | Descripción |
| --- | --- |
| `record_id` | Identificador único y estable de la sección |
| `record_type` | `article` o `transitory` |
| `document_id` | Identificador del reglamento de origen |
| `document_title` | Título oficial del reglamento |
| `sequence` | Posición de la sección dentro del reglamento |
| `chapter_number` | Número romano o arábigo del capítulo |
| `chapter_title` | Título del capítulo |
| `section_label` | Encabezado original del artículo o transitorio |
| `article_number` | Número normalizado del artículo, cuando corresponde |
| `article_title` | Nombre descriptivo incluido en el encabezado |
| `text` | Contenido visible normalizado, sin etiquetas HTML |
| `citation_label` | Etiqueta legible para citar la fuente |
| `source_url` | Página oficial del TEC |
| `snapshot_date` | Fecha de la captura utilizada |
| `snapshot_id` | Identificador de la captura o versión del corpus |
| `collection_profile` | Perfil de recolección: `initial` o `expanded` |
| `raw_file` | Archivo HTML original |
| `raw_sha256` | Huella del HTML original |
| `content_sha256` | Huella del texto normalizado de la sección |

## Decisiones de procesamiento

- Se selecciona el bloque normativo principal de cada página.
- Los artículos se reconocen por su encabezado textual, no por depender de un
  nivel fijo como `h3` o `h4`.
- Los artículos que comienzan dentro de un párrafo también se reconocen y su
  contenido se separa del rótulo.
- Los capítulos que separan el número y el título en dos encabezados se
  reconstruyen.
- Los artículos con sufijos como `bis`, `ter`, `quater`, `quinquies` y `sexies`
  conservan identificadores normalizados.
- Los encabezados estructurales sin número de capítulo se conservan como
  contexto de la sección.
- Los transitorios se mantienen como registros independientes.
- Las notas de reforma contenidas dentro de un artículo se conservan.
- Los menús, encabezados y pies del sitio no pasan al corpus procesado.
- Los HTML originales nunca se modifican.

## Generación

Desde la raíz del repositorio:

```powershell
python scripts/process_tec_regulations.py --snapshot-id 2026-07-23-expanded
```

El procesador verifica primero los SHA-256 del manifiesto de recolección. También
falla si encuentra identificadores duplicados, secciones vacías o una cantidad
inesperada de artículos y transitorios.
