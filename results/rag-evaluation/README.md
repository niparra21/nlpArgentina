# Evaluación del RAG completo

Esta carpeta conserva evaluaciones por lotes contra las 40 preguntas gold. No
debe confundirse con `results/rag/`, que contiene consultas individuales.

## Artefactos

Cada directorio de evaluación contiene:

- `evaluation.jsonl`: un registro completo por pregunta;
- `summary.json`: configuración, métricas agregadas, latencias y desglose.

`evaluation.jsonl` se escribe y vacía a disco después de cada pregunta. Esto
permite conservar avance si una consulta posterior falla.

## Corridas del 28 de julio de 2026

| Directorio | Uso | Esquema | Resultado |
|---|---|---:|---|
| `qwen3.5-9b/` | Diagnóstico con coincidencia inline estricta | 1.0.0 | 31/40 completadas |
| `qwen3.5-9b-normalized-citations/` | **Evaluación principal** | 1.1.0 | 37/40 completadas |

La primera corrida reveló que Qwen frecuentemente llenaba correctamente
`citations`, pero omitía escribir `[F1]` dentro de la frase. La segunda política
mantiene obligatoria la lista estructurada y:

1. valida las citas inline si Qwen las escribió;
2. añade visiblemente la lista estructurada si Qwen omitió las marcas inline;
3. sigue rechazando cualquier desacuerdo entre ambas representaciones.

La normalización solo cambió validación y presentación. El corpus, embeddings,
top-k, prompt, modelo, temperatura y semilla permanecieron iguales.

## Resultado principal

La evaluación seleccionada es:

```text
results/rag-evaluation/2026-07-28/
qwen3.5-9b-normalized-citations/
```

Resultados principales:

| Métrica | Resultado |
|---|---:|
| Preguntas | 40 |
| Salidas aceptadas | 37/40 |
| Decisión correcta | 35/40, 87.5% |
| Abstención en preguntas imposibles | 7/7, 100% |
| Recuperación con alguna evidencia gold | 31/33, 93.9% |
| Alguna cita gold | 27/33, 81.8% |
| Toda la evidencia gold citada | 25/33, 75.8% |

Los denominadores de recuperación y citas son las 33 preguntas respondibles.
Los errores estructurales cuentan como fallos; no se excluyen para mejorar las
métricas.

La explicación completa, fórmulas, latencias y análisis de fallos está en
`docs/03-evaluacion-rag-40-preguntas.md`.

La evaluación humana complementaria se realiza con:

- `outputs/rag-manual-review-20260728/revision_manual_rag.xlsx`;
- `docs/04-revision-manual-respuestas-rag.md`.
