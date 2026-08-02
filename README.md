# nlpArgentina

Prototipo académico de una arquitectura RAG mínima y observable sobre normativa
estudiantil del Tecnológico de Costa Rica.

## Corpus

El repositorio conserva un corpus de 25 documentos oficiales del TEC. La
captura registra procedencia, fecha de consulta y suma de verificación. Una
segunda capa derivada organiza el contenido por artículos y transitorios.

- [Metodología de recolección](data/raw/tec/README.md)
- [Captura de 25 documentos](data/raw/tec/2026-07-23/)
- [Corpus procesado por secciones](data/processed/tec/README.md)
- [Conjunto de evaluación de 40 preguntas](data/evaluation/README.md)

## Reproducir

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/process_tec_regulations.py --snapshot-id 2026-07-23
python -m unittest discover -s tests
```

## Recuperación semántica

El buscador local usa `intfloat/multilingual-e5-small` para convertir los
artículos y las preguntas en vectores normalizados. La versión exacta del modelo
y las huellas de los archivos quedan registradas para reproducibilidad.

```powershell
python scripts/search_corpus.py `
  "¿Cuántas horas puede trabajar un estudiante asistente?"
python scripts/evaluate_retrieval.py --force
```

El índice y la evaluación de referencia ya están incluidos. Para reconstruir el
índice completo desde el corpus y reproducir el experimento:

```powershell
python scripts/build_vector_index.py --force
python scripts/evaluate_retrieval.py --force
```

- [Construcción y estructura del índice](data/indexes/README.md)
- [Evaluación y significado de las métricas](results/retrieval/README.md)

## Modelo generativo local

La generación se ejecuta localmente con Ollama y `qwen3.5:9b`. Una prueba de
integración pequeña comprueba que el modelo use evidencia, incluya una cita y se
abstenga cuando el contexto no contiene la respuesta.

```powershell
python scripts/check_local_model.py
```

- [Instalación, conceptos, comandos y resultados](docs/01-modelo-local-con-ollama.md)
- [Índice de documentación de aprendizaje](docs/README.md)

## Responder con el RAG completo

El comando completo recupera cinco fragmentos, genera una respuesta local,
valida las citas y guarda un registro JSON observable:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/rag_answer.py `
  "¿Se puede equiparar un Trabajo Final de Graduación en el TEC?"
```

- [Arquitectura, contrato de citas y explicación paso a paso](docs/02-rag-completo-y-observabilidad.md)
- [Estructura de los registros RAG](results/rag/README.md)

## Evaluar las 40 preguntas

El evaluador carga los modelos una sola vez, procesa las 40 preguntas gold y
produce resultados por pregunta y un resumen:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/evaluate_rag.py
```

La evaluación principal completó 37/40 solicitudes, tomó la decisión correcta en
35/40 y se abstuvo correctamente en las siete preguntas imposibles. Estas
métricas no equivalen todavía a exactitud factual.

- [Metodología, resultados y análisis de fallos](docs/03-evaluacion-rag-40-preguntas.md)
- [Artefactos y corrida seleccionada](results/rag-evaluation/README.md)
- [Resumen JSON seleccionado](results/rag-evaluation/2026-07-28/qwen3.5-9b-normalized-citations/summary.json)

## Revisar manualmente las respuestas

Las métricas automáticas no demuestran por sí solas que el contenido sea
correcto. La plantilla de Excel organiza las 40 respuestas, los 200 fragmentos
recuperados y una rúbrica humana de corrección, cobertura, fidelidad, claridad y
calidad de la evidencia `gold`.

```powershell
Start-Process `
  ".\outputs\rag-manual-review-20260728\revision_manual_rag.xlsx"
```

- [Plantilla de revisión manual](outputs/rag-manual-review-20260728/revision_manual_rag.xlsx)
- [Rúbrica e instrucciones paso a paso](docs/04-revision-manual-respuestas-rag.md)

La información almacenada se utiliza únicamente con fines de investigación. Para
tomar decisiones académicas o administrativas se debe consultar siempre la fuente
oficial del TEC.
