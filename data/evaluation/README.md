# Conjunto de evaluación

Este directorio contiene las preguntas de referencia con las que se evaluará el
sistema RAG. No forman parte de los documentos que se indexarán: se mantienen
separadas para evitar que el sistema recupere las respuestas de la propia prueba.

## Archivo

`questions.jsonl` contiene un objeto JSON por línea. La primera versión tiene 40
preguntas:

- 25 preguntas `direct`, una por cada documento del corpus;
- 8 preguntas `multi_section`, cuya respuesta requiere combinar dos o más
  secciones;
- 7 preguntas `unanswerable`, cuya información no está en el corpus y ante las
  que el sistema debería abstenerse de inventar una respuesta.

## Campos

| Campo | Significado |
| --- | --- |
| `question_id` | Identificador estable de la pregunta. |
| `question` | Pregunta que recibirá el sistema RAG. |
| `question_type` | `direct`, `multi_section` o `unanswerable`. |
| `category` | Tema general que permite analizar resultados por área. |
| `answerable` | Indica si el corpus contiene evidencia suficiente. |
| `expected_answer` | Respuesta de referencia redactada a partir de la normativa. |
| `supporting_record_ids` | Secciones de `sections.jsonl` que respaldan la respuesta. |
| `document_ids` | Documentos a los que pertenecen las secciones de respaldo. |

## Cómo se usará

Para cada pregunta se guardarán los fragmentos recuperados, la respuesta
generada, las citas, el tiempo de ejecución y si el sistema decidió abstenerse.
Luego se podrán medir por separado:

1. **recuperación:** si las secciones de respaldo aparecen entre los fragmentos
   recuperados;
2. **respuesta:** si el contenido generado coincide con la respuesta esperada;
3. **fundamentación:** si las citas corresponden a las secciones recuperadas;
4. **abstención:** si reconoce correctamente que las preguntas no respondibles
   están fuera del corpus.

Las respuestas son una referencia para evaluación, no asesoría académica o
administrativa. La normativa oficial debe verificarse antes de tomar decisiones.
