# Contenido y diseño del póster

## Identificación

Título oficial:

> Diseño arquitectónico mínimo para sistemas RAG observables en español
> latinoamericano

Autora:

> Nicole Tatiana Parra Valverde

Evento:

> Segunda Escuela Sudamericana de NLP

Datos de presentación:

- sesión: 2;
- número de orden: 12;
- tamaño permitido: A1 o A0;
- orientación obligatoria: vertical;
- beca de impresión: concedida;
- fecha límite de entrega: 30 de julio de 2026.

## Decisión de formato

Se utilizará **A0 vertical**, con dimensiones físicas de 841 × 1189 mm.

La razón es que el trabajo necesita mostrar tres tipos de evidencia:

1. la arquitectura y sus componentes;
2. el diseño experimental;
3. los resultados automáticos y humanos.

El tamaño A0 permite conservar tipografía legible y dar protagonismo al
diagrama arquitectónico. La beca de impresión elimina la principal desventaja
práctica de escoger el tamaño mayor.

## Trabajo de comunicación

Al terminar de leer el póster, una persona participante de la escuela debería
comprender que:

> Un sistema RAG local y pequeño puede ser reproducible y observable sin
> infraestructura compleja, pero la evaluación humana revela que su principal
> debilidad aparece cuando debe recuperar y combinar evidencia distribuida
> entre varias secciones.

El póster no pretende demostrar que se construyó el mejor sistema RAG ni
comparar muchas arquitecturas. Presenta una arquitectura mínima, un caso de
estudio reproducible y los riesgos técnicos que la observabilidad permitió
identificar.

## Narrativa

La lectura sigue este orden:

```text
problema
→ objetivo
→ arquitectura
→ experimento
→ resultados
→ fallos observados
→ conclusión
```

La arquitectura ocupa la franja central y más visible. Los resultados no se
presentan como una colección de porcentajes: cada métrica se acompaña de su
interpretación.

## Distribución visual

### Franja superior

Incluye:

- título;
- nombre de la autora;
- condición de trabajo independiente;
- caso de estudio;
- una frase central que resuma el aporte.

Frase propuesta:

> Un caso de estudio con 25 reglamentos del TEC muestra que registrar
> evidencia, citas y tiempos permite explicar no solo cuánto falla un RAG,
> sino en qué componente ocurre el fallo.

### Franja arquitectónica

Presenta el flujo principal:

```text
25 documentos oficiales
→ 1 184 secciones
→ 1 259 fragmentos
→ embeddings e índice
→ recuperación top-5
→ contexto y prompt
→ Qwen3.5:9B local
→ validación de citas
→ respuesta y traza
```

Debajo del flujo se muestra la traza observable por consulta:

```text
pregunta
+ fragmentos y puntuaciones
+ respuesta
+ citas
+ estado answered / not_found
+ tiempo de recuperación y generación
```

### Zona inferior izquierda

Contiene problema, objetivo, caso de estudio y diseño experimental.

### Zona inferior central

Contiene los resultados humanos, un gráfico por tipo de pregunta y las
métricas automáticas de recuperación y tiempo.

### Zona inferior derecha

Contiene los hallazgos, limitaciones, conclusión, trabajo futuro y enlace al
repositorio.

## Texto propuesto

### Problema

Los prototipos RAG suelen mostrar una respuesta final, pero no siempre
conservan suficiente información para explicar por qué fue generada. Sin una
traza que conecte pregunta, evidencia, respuesta, citas y tiempos, es difícil
distinguir fallos de recuperación, generación o validación.

### Objetivo

Diseñar e implementar una arquitectura RAG mínima, local y reproducible para
documentos en español latinoamericano, incorporando señales básicas de
observabilidad que permitan analizar el comportamiento del sistema por
consulta.

### Pregunta de investigación

> ¿Qué componentes y registros mínimos permiten construir y diagnosticar un
> sistema RAG pequeño, basado en fuentes y ejecutado localmente?

### Caso de estudio

- 25 reglamentos y documentos oficiales del Tecnológico de Costa Rica;
- captura con URL, fecha y suma de verificación;
- 1 184 artículos y transitorios procesados;
- 1 259 fragmentos indexados;
- contenido institucional en español de Costa Rica.

### Configuración

- embeddings: `intfloat/multilingual-e5-small`;
- vectores de 384 dimensiones;
- similitud coseno mediante producto punto de vectores normalizados;
- recuperación: cinco fragmentos;
- generación: `qwen3.5:9b`, cuantización Q4_K_M;
- ejecución local mediante Ollama;
- temperatura: 0,1;
- validación de citas visibles y estructuradas.

### Evaluación

Se construyeron 40 preguntas:

- 25 directas, una por documento;
- 8 de varias secciones;
- 7 deliberadamente no respondibles.

Cada ejecución guardó los fragmentos recuperados, la respuesta, las citas y los
tiempos. Posteriormente se realizó una revisión humana de las 40 respuestas
mediante seis criterios:

- corrección factual;
- cobertura;
- fidelidad;
- claridad;
- calidad de la evidencia `gold`;
- conclusión manual.

## Resultados seleccionados

### Resultados humanos

| Indicador | Resultado | Interpretación |
|---|---:|---|
| Corrección factual estricta | 78,8 % | Excluye las siete abstenciones correctas marcadas como `No aplica`. |
| Puntaje factual ponderado | 86,4 % | Asigna medio punto a las respuestas parciales. |
| Fidelidad total a fuentes | 93,5 % | La mayoría de las afirmaciones realizadas estaba respaldada. |
| Cobertura completa | 72,7 % | Las omisiones son más frecuentes que las afirmaciones sin respaldo. |
| Abstención correcta | 7 de 7 | El sistema no inventó información ausente, actual o sensible. |

Conclusiones manuales:

- 28 aprobadas;
- 3 para revisar;
- 9 rechazadas.

### Resultados por tipo

| Tipo | Aprobadas | Total |
|---|---:|---:|
| Directas | 19 | 25 |
| Varias secciones | 2 | 8 |
| No respondibles | 7 | 7 |

Este gráfico debe comunicar el hallazgo central: el problema no es la
abstención, sino combinar evidencia distribuida.

### Métricas automáticas

- recuperación con al menos una evidencia `gold` en top-5: 93,9 %;
- recuperación completa de la evidencia esperada: 84,8 %;
- búsqueda semántica promedio: 27 ms;
- tiempo total promedio por pregunta: 5,53 s;
- generación promedio: 5,36 s;
- velocidad media del modelo: 49 tokens/s.

La búsqueda representa menos del 1 % del tiempo total. La generación domina la
latencia del pipeline.

## Hallazgos

### 1. La evidencia distribuida es el principal reto

Solo dos de ocho preguntas de varias secciones fueron aprobadas. En varios
casos el recuperador encontró una parte de la respuesta, pero no todos los
artículos necesarios.

### 2. Recuperar el documento no garantiza recuperar el fragmento

En `q029` se recuperó un registro relacionado con el artículo correcto, pero no
el fragmento que contenía el plazo y el medio solicitado. La observabilidad a
nivel de fragmento permitió identificar el fallo.

### 3. Una respuesta correcta puede ser una salida inválida

En `q025` y `q032`, el contenido visible era correcto, pero las citas del texto
no coincidían con el campo estructurado. Ambas salidas fueron rechazadas por
incumplir el contrato del pipeline.

### 4. La abstención funcionó

Las siete preguntas sobre precios, horarios, contraseñas o disponibilidad
actual recibieron `not_found`. El modelo evitó presentar como hechos datos que
no estaban en el corpus.

## Conclusión

Una arquitectura mínima puede ofrecer trazabilidad útil sin depender de una
plataforma de observabilidad compleja. Registrar evidencia, citas, estados y
tiempos permitió localizar fallos en recuperación, generación y validación.

El prototipo funcionó mejor con preguntas directas y abstenciones. El reto
principal fue combinar evidencia distribuida. Por ello, una arquitectura RAG
observable debe distinguir evidencia por documento y por fragmento, y validar
la consistencia de las citas antes de entregar la respuesta.

## Limitaciones

- un único dominio documental;
- un modelo de embeddings y un modelo generativo;
- 40 preguntas;
- una sola persona revisora;
- ausencia de comparación con BM25, recuperación híbrida o reranking;
- el caso de estudio no representa toda la diversidad del español
  latinoamericano.

## Trabajo futuro

- comparar recuperación densa, léxica e híbrida;
- incorporar reranking para preguntas de varias secciones;
- evaluar otros modelos locales;
- ampliar el corpus a otros países y dominios;
- realizar revisión humana con más de una persona;
- estudiar umbrales de abstención y calibración.

## Repositorio

```text
github.com/niparra21/nlpArgentina
```

## Referencias breves

1. Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive
   NLP Tasks*.
2. Wang et al. (2024). *Multilingual E5 Text Embeddings: A Technical Report*.
3. Tecnológico de Costa Rica. Reglamentos y normativa institucional utilizados
   como caso de estudio.

## Decisiones editoriales

### Métricas que sí se muestran

Se muestran corrección, fidelidad, cobertura, abstención, recuperación y
latencia porque responden preguntas diferentes sobre el sistema.

### Métricas que no se presentan como exactitud

La superposición léxica no se utilizará como indicador principal. Mide
coincidencia de palabras contra una respuesta de referencia, pero no demuestra
corrección semántica.

La métrica automática `status_accuracy` tampoco se presentará como exactitud
factual. Solo verifica si el sistema eligió `answered` o `not_found`.

### Lenguaje

El póster se redacta en español. Los nombres de modelos, campos y estados se
mantienen en su forma técnica cuando traducirlos reduciría la precisión.

### Afiliación y logotipos

Se indicará «trabajo independiente» y «caso de estudio: normativa estudiantil
del Tecnológico de Costa Rica». No se utilizará el logotipo del TEC de manera
que pueda interpretarse como autoría, supervisión o respaldo institucional.

## Lista de verificación de impresión

Antes de enviar:

1. confirmar que el formulario acepta PDF y revisar el límite de tamaño;
2. comprobar que el documento mide 841 × 1189 mm;
3. verificar orientación vertical;
4. comprobar que no hay texto cortado ni elementos fuera del lienzo;
5. comprobar que todas las cifras coinciden con los artefactos finales;
6. revisar ortografía y acentos;
7. revisar el PDF renderizado a página completa y por zonas;
8. comprobar que las tipografías estén incrustadas o convertidas
   correctamente;
9. usar imágenes y gráficos con resolución suficiente;
10. conservar una copia editable en PowerPoint;
11. subir el archivo antes del 30 de julio de 2026.

## Producción de la primera maqueta

La primera maqueta se produjo el 28 de julio de 2026 en tamaño A0 vertical. Se
conservaron dos salidas:

- `outputs/poster-20260728/poster-rag-observable-a0-vertical.pptx`: copia
  editable para modificar textos, posiciones o colores;
- `outputs/poster-20260728/poster-rag-observable-a0-vertical.pdf`: copia
  destinada a la impresión y al formulario de entrega.

El PDF es el archivo que debe enviarse, siempre que el formulario confirme que
acepta ese tipo de archivo y su tamaño. El PowerPoint se conserva como fuente
editable y respaldo, no como primera opción para la imprenta.

### Qué representa cada zona

1. **Encabezado:** identifica el evento, el título oficial, la autora y el caso
   de estudio.
2. **Arquitectura:** presenta las siete etapas del flujo, de izquierda a
   derecha, y la información que se conserva en la traza de cada consulta.
3. **Columna izquierda:** explica el problema, el objetivo, el corpus, el diseño
   experimental y los criterios de revisión humana.
4. **Columna central:** muestra las métricas revisadas manualmente, la
   aprobación según tipo de pregunta y el rendimiento automático.
5. **Columna derecha:** traduce las trazas en cuatro hallazgos, formula la
   conclusión y reconoce las limitaciones.
6. **Pie:** incluye referencias breves, el enlace al repositorio, la sesión y
   el número de orden.

### Validaciones realizadas

- El PowerPoint contiene una sola página y no tiene elementos fuera del
  lienzo.
- El PDF contiene una sola página A0 vertical.
- El tamaño reportado por el PDF es `2384,28 × 3370,56 pt`, equivalente a A0.
- Las tipografías utilizadas en el PDF están incrustadas.
- Se renderizó el PDF completo y se inspeccionó visualmente.
- Se corrigió la dirección de las flechas del pipeline para que el flujo vaya
  de `Fuentes` a `Salida`.
- No se detectaron textos cortados, superposiciones ni gráficos fuera de
  margen.

### Decisión pendiente antes de subirlo

El formulario de Google solicita iniciar sesión antes de mostrar todos sus
campos. Por eso todavía se debe comprobar, desde la cuenta que hará la entrega,
el tipo de archivo permitido y el límite de tamaño. No se ha subido ningún
archivo automáticamente.
