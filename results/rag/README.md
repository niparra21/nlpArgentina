# Registros observables del RAG

Cada ejecución de `scripts/rag_answer.py` crea un archivo JSON inmutable con la
pregunta, configuración, fragmentos recuperados, respuesta, citas y tiempos.

## Organización

```text
results/rag/
└── AAAA-MM-DD/
    └── modelo-generativo/
        └── rag-AAAAMMDDTHHMMSS-microsegundos.json
```

La fecha y el identificador se calculan al iniciar la consulta. Si un archivo ya
existe, el programa se detiene en lugar de reemplazarlo.

## Contenido de cada registro

- `configuration`: versiones, digest del índice, modelos y parámetros.
- `retrieval`: tiempo de carga, tiempo de búsqueda y cinco fragmentos con
  procedencia completa.
- `generation`: latencia, tokens, velocidad y tamaño del contexto.
- `result`: estado, respuesta, citas validadas y URLs oficiales citadas.
- `total_pipeline_ms`: tiempo total observado por el proceso.

Los identificadores `[F1]`, `[F2]`, etc. son locales a una ejecución. Siempre se
deben interpretar mediante `retrieval.sources` o `result.cited_sources`.

## Ejecuciones de referencia

El 28 de julio de 2026 se conservaron dos comprobaciones:

1. una pregunta respondible sobre la reposición de una evaluación, con estado
   `answered` y cita válida al Artículo 66;
2. una pregunta sin respuesta en el corpus sobre el precio actual de un
   almuerzo, con estado `not_found` y cero citas.

Estos archivos son ejemplos de ejecución, no una evaluación completa de las 40
preguntas.
