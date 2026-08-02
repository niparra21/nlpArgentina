# Evaluación del RAG sobre 40 preguntas

Fecha de las corridas: **28 de julio de 2026**.

Esta etapa pasó de probar ejemplos aislados a medir el sistema completo contra
el conjunto gold creado previamente.

## 1. Objetivo

La evaluación busca responder preguntas diferentes:

1. ¿El recuperador trae el artículo o sección esperado?
2. ¿El sistema decide correctamente entre responder y abstenerse?
3. ¿La respuesta cita al menos una fuente gold?
4. ¿Cita todas las fuentes necesarias para preguntas de varias secciones?
5. ¿Cuánto tarda cada etapa?
6. ¿Qué tipos de fallo quedan ocultos si solo vemos una respuesta exitosa?

No se utiliza Qwen como juez de sus propias respuestas. Las métricas automáticas
se calculan contra metadatos y respuestas manuales existentes.

## 2. Conjunto de evaluación

Archivo:

```text
data/evaluation/questions.jsonl
```

SHA-256:

```text
5fb065bc2d8cf175dbdbffb41e9e231e3a61393c3d50eb9043b7abb4e9f95f6a
```

Distribución:

| Tipo | Cantidad |
|---|---:|
| Preguntas directas | 25 |
| Preguntas que combinan varias secciones | 8 |
| Preguntas imposibles según el corpus | 7 |
| **Total** | **40** |

Por disponibilidad de respuesta:

```text
33 respondibles
7 no respondibles
```

Cada pregunta respondible contiene:

- respuesta de referencia redactada manualmente;
- uno o más `supporting_record_ids`;
- documentos esperados;
- tipo y categoría.

Los siete casos imposibles tienen una lista vacía de evidencia gold.

## 3. Configuración fija

Las dos corridas usaron:

| Componente | Configuración |
|---|---|
| Snapshot | `2026-07-23` |
| Embeddings | `intfloat/multilingual-e5-small` |
| Revisión embeddings | `614241f...` |
| Fragmentos | top-5 |
| Repetición de record | permitida |
| Generador | `qwen3.5:9b` |
| Digest Qwen | `6488c96fa5fa...` |
| Cuantización | `Q4_K_M` |
| Contexto | 8,192 tokens |
| Temperatura | 0.1 |
| Semilla | 42 |
| Salida máxima | 512 tokens |
| Thinking | desactivado |
| Ollama | 0.32.5 |

El manifiesto del índice tenía SHA-256:

```text
b832bba614cdc8cc352c768fef896848c70d8adc7391da9cdbba04dbf43b814c
```

Mantener fija la configuración permite atribuir diferencias entre corridas a la
política de validación de citas.

## 4. Comando creado

El evaluador está en:

```text
scripts/evaluate_rag.py
```

Ejecución completa:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/evaluate_rag.py
```

El programa:

1. valida argumentos;
2. comprueba Ollama y Qwen;
3. comprueba huellas del índice;
4. carga `multilingual-e5-small` una sola vez;
5. reutiliza Qwen durante todo el lote;
6. procesa las preguntas en orden;
7. escribe cada resultado inmediatamente;
8. continúa después de errores conocidos de generación;
9. crea el resumen al terminar.

La carga única es importante. Ejecutar `rag_answer.py` cuarenta veces volvería a
cargar el modelo de embeddings en cada proceso y distorsionaría los tiempos.

## 5. Opciones de diagnóstico

Limitar a las primeras preguntas:

```powershell
python scripts/evaluate_rag.py --limit 3
```

Evaluar IDs concretos:

```powershell
python scripts/evaluate_rag.py `
  --question-id q003 `
  --question-id q029
```

Elegir otro directorio:

```powershell
python scripts/evaluate_rag.py `
  --output-dir results\rag-evaluation\prueba
```

Reemplazar intencionalmente los dos artefactos conocidos:

```powershell
python scripts/evaluate_rag.py --force
```

Sin `--force`, la existencia de `evaluation.jsonl` o `summary.json` detiene el
programa. No se reemplaza una medición anterior accidentalmente.

## 6. Escritura incremental

Cada pregunta se añade a:

```text
evaluation.jsonl
```

El archivo se abre, escribe y cierra en cada iteración. Si la pregunta 30 falla,
los primeros 29 registros ya están guardados.

Cada línea contiene:

- pregunta y datos gold;
- cinco fragmentos completos;
- puntuaciones y procedencia;
- respuesta y citas, si fueron válidas;
- comparación contra evidencia gold;
- latencias;
- error estructurado, cuando existe.

Al finalizar se crea:

```text
summary.json
```

## 7. Métricas de recuperación

### Retrieval hit rate

Pregunta respondible donde al menos un `record_id` recuperado coincide con la
evidencia gold:

```text
preguntas con alguna evidencia gold recuperada / 33
```

Resultado:

```text
31 / 33 = 93.9%
```

### Complete retrieval evidence rate

Pregunta donde se recuperaron todos los `record_id` gold:

```text
28 / 33 = 84.8%
```

### Mean retrieval evidence recall

Promedio de la fracción de fuentes gold recuperadas por pregunta:

```text
89.4%
```

Estas métricas miden presencia de registros esperados. No prueban todavía que el
chunk exacto incluya cada oración necesaria.

## 8. Métrica de decisión

Se considera decisión correcta:

- `answered` para una pregunta gold respondible;
- `not_found` para una pregunta gold no respondible.

Errores de formato cuentan como decisiones incorrectas porque el sistema no pudo
entregar una respuesta válida.

Resultado principal:

```text
35 / 40 = 87.5%
```

Desglose:

```text
preguntas directas:      23/25 = 92.0%
preguntas multi-sección:  5/8  = 62.5%
preguntas imposibles:     7/7  = 100%
```

## 9. Métricas de citas

### Citation hit rate

Al menos uno de los `record_id` citados coincide con el gold:

```text
27 / 33 = 81.8%
```

Los errores y abstenciones incorrectas cuentan como cero.

### Complete expected evidence citation rate

La respuesta citó todos los `record_id` gold:

```text
25 / 33 = 75.8%
```

Esta métrica es más exigente para preguntas multi-sección:

```text
directas:      22/25 = 88.0%
multi-sección:  3/8  = 37.5%
```

### Mean citation evidence recall

Fracción promedio de evidencia gold citada:

```text
78.8%
```

### Mean citation precision against gold

Fracción promedio de registros citados que pertenecen al conjunto gold:

```text
72.2%
```

Una precisión menor que el hit rate indica que algunas respuestas citan una
fuente correcta junto con fuentes adicionales no incluidas en el gold.

Esto puede significar:

- citas innecesarias;
- evidencia relacionada pero no requerida;
- evidencia gold incompleta;
- atribución incorrecta.

Debe revisarse manualmente antes de decidir.

## 10. Superposición léxica

Se calcula una métrica bag-of-words:

1. convierte a minúsculas;
2. elimina tildes;
3. separa palabras y números;
4. excluye tokens como `F1`;
5. compara frecuencias contra la respuesta manual;
6. calcula precisión, recall y F1.

F1 promedio:

```text
53.5%
```

Esta métrica es solamente descriptiva. Dos respuestas equivalentes pueden usar
palabras diferentes, y dos respuestas incorrectas pueden compartir muchas
palabras. No debe rotularse como “exactitud de respuestas”.

## 11. Latencias

Corrida principal:

| Medición | Promedio | Mediana | P95 | Máximo |
|---|---:|---:|---:|---:|
| Recuperación | 26.99 ms | 24.90 ms | 40.27 ms | 53.57 ms |
| Solicitud de generación | 5.36 s | 5.02 s | 7.34 s | 7.66 s |
| Pregunta completa | 5.53 s | 5.16 s | 7.57 s | 7.97 s |

Velocidad de generación:

```text
promedio: 49.03 tokens/s
mediana:  50.04 tokens/s
mínimo:   43.52 tokens/s
máximo:   51.29 tokens/s
```

Duración interna del lote:

```text
229.5 segundos, aproximadamente 3 minutos 49 segundos
```

La terminal informó un tiempo ligeramente mayor porque importar bibliotecas
ocurre antes de iniciar el cronómetro interno del lote.

## 12. Resultados por tipo

| Tipo | Completadas | Status correcto | Alguna cita gold | Toda evidencia citada |
|---|---:|---:|---:|---:|
| Directa | 24/25 | 92.0% | 88.0% | 88.0% |
| Multi-sección | 6/8 | 62.5% | 62.5% | 37.5% |
| No respondible | 7/7 | 100% | No aplica | No aplica |

La recuperación obtuvo hit en las ocho preguntas multi-sección, pero el sistema
solo citó toda la evidencia en tres. Por tanto, el cuello de botella no es
únicamente encontrar información: también es combinarla y atribuirla.

## 13. Resultados por categoría

Hallazgos relevantes:

- `admisión_y_graduación`: 100% de decisión y citation hit;
- `enseñanza_y_evaluación`: 100% en las dos preguntas;
- `becas_y_apoyo`: 80% de decisión y 70% citation hit;
- `comunicación_institucional`: 50% de decisión;
- `fuera_del_corpus`: 100% de abstención.

Las categorías tienen pocas preguntas y no deben interpretarse como estimaciones
estadísticas generales. Sirven para localizar casos que revisar.

## 14. Primera corrida: política inline estricta

Directorio:

```text
results/rag-evaluation/2026-07-28/qwen3.5-9b/
```

Esquema:

```text
1.0.0
```

El validador exigía igualdad exacta entre:

- marcas `[F1]` dentro de `answer`;
- arreglo `citations`.

Resultado:

| Métrica | Primera corrida |
|---|---:|
| Completadas | 31/40 |
| Errores | 9 |
| Status accuracy | 72.5% |
| Citation hit | 63.6% |
| Abstención | 100% |

Los nueve errores tenían el mismo mensaje:

```text
Las citas del texto y del campo citations no coinciden.
```

Todos habían recuperado alguna evidencia gold.

## 15. Diagnóstico de la primera corrida

Se añadió `GenerationValidationError`, que conserva la salida bruta del modelo.
Después se repitieron `q003`, `q004`, `q009` y `q028` fuera de los artefactos
principales.

`q003` generó:

```json
{
  "status": "answered",
  "answer": "Los Trabajos Finales de Graduación no serán susceptibles de equiparación.",
  "citations": ["F1"]
}
```

La respuesta y la fuente eran correctas, pero Qwen omitió `[F1]` dentro de la
frase.

`q004` y `q009` mostraron el mismo patrón. `q028`, en cambio, contenía citas
visibles adicionales que no aparecían en el arreglo. Ese caso sí representa una
inconsistencia y no debía aceptarse.

## 16. Política seleccionada de citas

La política `1.1.0` establece:

1. `citations` sigue siendo obligatorio y no puede estar vacío al responder;
2. todos sus identificadores deben existir entre las fuentes recuperadas;
3. si Qwen incluye marcas inline, deben coincidir exactamente con el arreglo;
4. si no incluye ninguna marca inline, el programa añade determinísticamente el
   arreglo al final de la respuesta;
5. una abstención continúa exigiendo cero citas.

Ejemplo normalizado:

```text
Antes:
Los trabajos finales no son susceptibles de equiparación.

citations:
["F1"]

Después:
Los trabajos finales no son susceptibles de equiparación [F1].
```

Esto corrige presentación sin inventar ni cambiar la fuente declarada.

## 17. Comparación de corridas

| Política | Completadas | Errores | Status | Citation hit | Abstención |
|---|---:|---:|---:|---:|---:|
| Inline estricta 1.0.0 | 31/40 | 9 | 72.5% | 63.6% | 100% |
| Normalizada 1.1.0 | 37/40 | 3 | 87.5% | 81.8% | 100% |

No cambiaron:

- preguntas;
- corpus;
- embeddings;
- top-k;
- prompt;
- Qwen;
- temperatura;
- semilla.

La comparación mide el impacto de una decisión de contrato y presentación.

## 18. Tres errores estructurales restantes

### `q025`

Pregunta directa sobre la elección del tercer representante estudiantil.

La respuesta mostraba `[F4]`, `[F3]`, `[F2]` y `[F1]`, pero el arreglo solo
declaraba `F3` y `F4`. Se rechazó.

### `q028`

Pregunta multi-sección sobre horas de estudiantes asistentes.

El texto utilizó cuatro identificadores; el arreglo declaró tres. Se rechazó.

### `q032`

Pregunta multi-sección sobre denuncias y medidas cautelares.

El texto terminó usando `[F5]`, pero el arreglo declaró únicamente `F2` y `F1`.
Se rechazó.

Aceptar estos casos implicaría escoger arbitrariamente qué representación creer.

## 19. Fallos sustantivos adicionales

### `q016`: fallo de recuperación

La pregunta pedía el programa prioritario del Fondo Solidario. El artículo gold
no apareció en top-5 y Qwen se abstuvo.

```text
retrieval_hit = false
status = not_found
```

La abstención fue razonable dado el contexto recibido, pero incorrecta contra el
corpus completo.

### `q017`: evidencia gold no recuperada

La pregunta pedía condiciones para financiamiento de actividades en el exterior.
El Artículo 11 gold no entró al top-5. Qwen respondió citando cinco artículos
relacionados, ninguno gold.

```text
status = answered
citation_hit = false
```

Este caso requiere revisión humana: la respuesta puede contener condiciones
relacionadas, pero no utilizó la evidencia manualmente seleccionada.

### `q029`: combinación incompleta

La pregunta requería:

- plazo y medio del Artículo 66;
- regla de recepción del Reglamento de Correo Electrónico, Artículo 5.

El recuperador tuvo al menos un hit, pero Qwen devolvió `not_found`. Es un fallo
de composición multi-sección.

## 20. Qué podemos afirmar

Con la configuración probada podemos afirmar que:

- el pipeline completó válidamente 37 de 40 solicitudes;
- detectó correctamente 7 de 7 preguntas imposibles;
- recuperó alguna evidencia gold en 31 de 33 preguntas respondibles;
- citó alguna evidencia gold en 27 de 33;
- citó toda la evidencia gold en 25 de 33;
- respondió en aproximadamente 5.5 segundos por pregunta en promedio;
- las preguntas multi-sección son el grupo más difícil;
- la observabilidad permitió separar fallos de recuperación, abstención,
  composición y formato.

## 21. Qué todavía no podemos afirmar

No podemos afirmar todavía:

- “87.5% de respuestas correctas”;
- que toda afirmación generada esté implicada por su fuente;
- que el gold contenga todas las fuentes alternativas válidas;
- que el resultado se repita idénticamente en otra computadora;
- que top-5 sea la mejor configuración;
- que el prototipo sea apto para decisiones administrativas reales.

`status_accuracy` mide la decisión de responder, no exactitud semántica.
`citation_hit` mide coincidencia de procedencia, no entailment.

## 22. Artefactos principales

Evaluación seleccionada:

```text
results/rag-evaluation/2026-07-28/
qwen3.5-9b-normalized-citations/
```

Archivos:

```text
evaluation.jsonl
summary.json
```

Tamaños y SHA-256:

| Archivo | Tamaño | SHA-256 |
|---|---:|---|
| `evaluation.jsonl` | 342,105 bytes | `30dcc3026aee...` |
| `summary.json` | 7,875 bytes | `4f37cb432cb1...` |

Los hashes completos pueden regenerarse con:

```powershell
Get-FileHash `
  results\rag-evaluation\2026-07-28\qwen3.5-9b-normalized-citations\* `
  -Algorithm SHA256
```

## 23. Pruebas automáticas

Se añadió:

```text
tests/test_evaluate_rag.py
```

Comprueba:

- normalización de tildes y citas;
- cálculo de superposición léxica;
- métricas de recuperación gold;
- resolución de citas;
- abstención;
- resúmenes;
- protección de artefactos.

También se ampliaron las pruebas de generación para conservar salida bruta en
errores y normalizar citas estructuradas.

Resultado final:

```text
59 pruebas
OK
```

## 24. Siguiente paso

La siguiente etapa debe ser una revisión humana de las 28 respuestas aceptadas
y los seis casos problemáticos identificados:

```text
q016, q017, q025, q028, q029, q032
```

Tres son errores de consistencia de citas y tres son fallos de recuperación o
composición.

La revisión humana debería etiquetar:

- corrección factual;
- cobertura;
- fidelidad a citas;
- claridad;
- si una fuente no gold también es válida.

Después podremos escoger métricas honestas para el póster y decidir si conviene
mejorar recuperación o el contrato de generación.
