# Resultados de recuperación

Esta carpeta conserva la línea base de recuperación semántica. Evalúa si el
buscador encuentra la evidencia correcta antes de incorporar un modelo
generador de respuestas.

## Ejecutar

Primero debe existir el índice descrito en `data/indexes/README.md`. Después:

```powershell
python scripts/evaluate_retrieval.py
```

Para regenerar resultados existentes intencionalmente:

```powershell
python scripts/evaluate_retrieval.py --force
```

## Archivos generados

```text
results/retrieval/2026-07-23/multilingual-e5-small/
├── evaluation.jsonl
└── summary.json
```

- `evaluation.jsonl`: una observación por pregunta con artículos esperados,
  fragmentos recuperados, puntuaciones, coincidencias y tiempo.
- `summary.json`: métricas agregadas y huellas de los archivos usados.

## Métricas

- `hit_rate`: proporción de preguntas que recuperó al menos una evidencia.
- `complete_evidence_rate`: proporción que recuperó todas sus evidencias.
- `mean_evidence_recall`: proporción media de evidencias recuperadas.
- `mean_reciprocal_rank`: premia que la primera evidencia correcta aparezca en
  posiciones altas.

Las preguntas `unanswerable` no se incluyen en esas métricas porque un buscador
vectorial siempre devuelve los textos más cercanos, aunque ninguno responda. Sus
puntuaciones se guardan para estudiar posteriormente un umbral de abstención.

## Línea base obtenida

Resultados con `multilingual-e5-small`, búsqueda exacta y cinco artículos:

| Corte | Al menos una evidencia | Todas las evidencias | MRR |
| --- | ---: | ---: | ---: |
| Top 1 | 69.7 % | 57.6 % | 69.7 % |
| Top 3 | 87.9 % | 78.8 % | 77.8 % |
| Top 5 | 93.9 % | 84.8 % | 79.1 % |

En las 25 preguntas directas, 23 recuperaron el artículo correcto dentro de los
primeros cinco resultados (92 %). Las ocho preguntas de varias secciones
recuperaron al menos una evidencia; cinco recuperaron todas (62.5 %).

La latencia mediana fue 22.25 ms por pregunta y la media 28.03 ms, sin contar la
carga inicial del modelo. Las preguntas directas `q016` y `q017` recuperaron el
reglamento temáticamente correcto, pero no el artículo de referencia dentro del
top 5. Las preguntas `q029`, `q031` y `q033` recuperaron solo una parte de la
evidencia requerida.

En esta muestra, las puntuaciones máximas de las preguntas respondibles
estuvieron entre 0.8700 y 0.9358; las no respondibles, entre 0.8265 y 0.8652.
Aunque existe una separación pequeña, siete preguntas no respondibles no son
suficientes para fijar un umbral general sin sobreajustar.
