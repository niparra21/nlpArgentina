# Índice semántico local

Esta carpeta contiene los vectores derivados del corpus procesado. Los
embeddings no sustituyen los textos: permiten buscar fragmentos similares a una
pregunta, mientras que `chunks.jsonl` conserva el texto y la procedencia que se
usarán para responder y citar.

## Modelo y estrategia

- Modelo: `intfloat/multilingual-e5-small`
- Revisión: `614241f622f53c4eeff9890bdc4f31cfecc418b3`
- Dimensiones esperadas: 384
- Longitud máxima usada: 480 tokens
- Superposición: 50 tokens
- Similitud: producto punto entre vectores normalizados, equivalente a coseno

Cada entrada se construye con este contexto:

```text
passage: Título del reglamento
Capítulo
Artículo

Texto del artículo o fragmento
```

Los artículos cortos producen un fragmento. Los que exceden el límite se
dividen, pero todos sus fragmentos conservan el `record_id` original.

## Construir el índice

Desde la raíz del repositorio y con el entorno virtual activado:

```powershell
python scripts/build_vector_index.py
```

El comando se niega a sobrescribir un índice existente. Para regenerarlo de
forma intencional:

```powershell
python scripts/build_vector_index.py --force
```

## Archivos generados

```text
data/indexes/tec/2026-07-23/multilingual-e5-small/
├── embeddings.npy
├── chunks.jsonl
└── index_manifest.json
```

- `embeddings.npy`: matriz NumPy de vectores `float32`.
- `chunks.jsonl`: metadatos, texto y trazabilidad de cada fila de la matriz.
- `index_manifest.json`: modelo, revisión, configuración, cantidades y huellas
  SHA-256.

La fila `n` de `embeddings.npy` corresponde a la línea `n` de `chunks.jsonl`.
Al cargar el índice, el buscador verifica las huellas y rechaza archivos
modificados o desalineados.

La captura `2026-07-23` produjo 1,259 fragmentos a partir de 1,184 secciones.
Un total de 51 artículos requirió división; los 1,133 restantes conservaron un
solo fragmento.

## Probar una consulta

```powershell
python scripts/search_corpus.py `
  "¿Cuántas horas puede trabajar un estudiante asistente?"
```

El buscador convierte la pregunta en `query: ...`, calcula la similitud contra
todos los vectores y muestra los cinco artículos distintos con mayor puntuación.
