# Guion para exponer el póster

## Datos de la sesión

La página oficial no establece una duración individual ni una presentación
oral formal por póster. La dinámica anunciada es una sesión abierta a visitas:

- sesión de pósters 2: martes 4 de agosto de 2026;
- primer bloque: 11:00–11:30, durante el coffee break;
- continuación: 12:30–14:30, durante el almuerzo;
- ubicación general de la escuela: Ciudad Universitaria, pabellones 0 y I.

La estrategia recomendada es preparar un recorrido principal de tres a cuatro
minutos, una explicación de treinta segundos y ampliaciones para responder
preguntas.

## Recorrido visual

Mientras se expone, señalar estas zonas en este orden:

1. título y franja con el mensaje central;
2. problema y objetivo, en la parte superior izquierda;
3. arquitectura observable, en la parte superior derecha;
4. corpus y protocolo de evaluación;
5. tarjetas, gráfico y tabla de resultados;
6. lecciones arquitectónicas, conclusión e investigación en curso.

No es necesario leer cada cifra ni cada bloque del póster. El guion presenta la
historia principal y deja los detalles como apoyo para las preguntas.

## Guion principal: aproximadamente tres a cuatro minutos

### 0:00–0:20 — Presentación y pregunta central

> Hola, soy Nicole Tatiana Parra Valverde. Este trabajo se titula “Diseño
> arquitectónico mínimo para sistemas RAG observables en español
> latinoamericano”. La pregunta que motivó el proyecto fue sencilla: cuando un
> sistema RAG responde mal, ¿cómo podemos saber si falló la recuperación, la
> generación o la validación de la salida?

### 0:20–0:50 — Problema y propuesta

> Un sistema RAG recupera documentos y los entrega como contexto a un modelo de
> lenguaje. Sin embargo, si únicamente conservamos la respuesta final, perdemos
> la información necesaria para reconstruir lo que ocurrió. Por eso diseñé e
> implementé una arquitectura mínima que registra, para cada consulta, la
> configuración, los fragmentos recuperados y sus puntuaciones, el contexto, la
> respuesta, el estado, las citas y los tiempos.

### 0:50–1:30 — Implementación

> Como caso de estudio utilicé 25 documentos oficiales de normativa estudiantil
> del Tecnológico de Costa Rica. El procesamiento produjo 1 184 secciones y
> 1 259 fragmentos. Generé embeddings normalizados de 384 dimensiones con
> multilingual-e5-small, recuperé los cinco fragmentos más cercanos y generé la
> respuesta localmente con Qwen3.5:9B mediante Ollama. Un validador independiente
> comprobó el estado, el contrato JSON y la consistencia de las citas. Toda esa
> ejecución quedó almacenada como una traza reproducible.

### 1:30–2:15 — Evaluación y resultados

> Evalué el pipeline con 40 preguntas: 25 directas, 8 que necesitaban combinar
> evidencia de varias secciones y 7 que no podían responderse con el corpus.
> En las 33 preguntas respondibles, el recuperador encontró al menos un registro
> de referencia en 31 casos, es decir, un 93,9 %. Sin embargo, la revisión manual
> aprobó 28 de las 40 salidas, un 70 %. Por tipo de pregunta, se aprobaron 19 de
> 25 directas, solamente 2 de 8 multisección y las 7 de 7 no respondibles. El
> tiempo total promedio del pipeline fue de 5,53 segundos por pregunta.

### 2:15–2:50 — Qué permitió descubrir la observabilidad

> La diferencia entre recuperar evidencia y aprobar la respuesta fue el hallazgo
> principal. La traza permitió distinguir tres problemas. Primero, en las
> preguntas multisección se recuperaba con frecuencia solo una parte de la
> evidencia. Segundo, en un caso se recuperó el documento y el artículo
> relacionados, pero no el fragmento que contenía el dato. Tercero, dos
> respuestas con contenido correcto fueron rechazadas porque las citas visibles
> no coincidían con los identificadores del JSON. Estos problemas no se habrían
> entendido observando únicamente la respuesta final.

### 2:50–3:15 — Conclusión y continuidad

> En conclusión, una arquitectura pequeña puede ofrecer observabilidad útil sin
> depender de una plataforma compleja. En este caso, el principal reto no fue la
> abstención, que funcionó correctamente en siete de siete casos, sino reunir y
> validar evidencia distribuida. Esta implementación es una prueba de concepto
> y no el pipeline definitivo. La investigación continúa con recuperación
> híbrida, reranking, mejores estrategias para evidencia multisección,
> validación de citas y nuevos dominios latinoamericanos.

> Gracias. Con gusto puedo profundizar en la arquitectura, la evaluación o en
> alguno de los casos de fallo.

## Versión de treinta segundos

> Este trabajo presenta una arquitectura RAG mínima y observable para documentos
> en español. Construí un prototipo local sobre 25 documentos del TEC y conservé
> una traza completa de cada consulta: recuperación, contexto, respuesta, citas,
> estado y tiempos. Aunque el sistema recuperó alguna evidencia de referencia en
> el 93,9 % de las preguntas respondibles, la revisión manual aprobó el 70 % de
> las salidas. La observabilidad mostró que el principal problema era combinar
> evidencia distribuida y validar la consistencia de las citas. Esta es una
> prueba de concepto y el pipeline continúa en investigación.

## Ampliaciones para visitantes interesados

### Ejemplo 1: documento correcto, fragmento incorrecto

> En la pregunta q029, la recuperación automática encontró un fragmento del
> artículo relacionado, pero no la parte que contenía el plazo y el requisito de
> usar la cuenta institucional. También faltó una segunda sección necesaria.
> Por eso una métrica basada únicamente en el identificador del registro podía
> verse positiva mientras el contexto entregado al modelo seguía siendo
> insuficiente.

### Ejemplo 2: respuesta correcta, salida inválida

> En q025 y q032, el texto visible era pertinente y estaba respaldado. Sin
> embargo, las citas escritas dentro de la respuesta no coincidían con la lista
> de citas del objeto JSON. El validador rechazó ambas salidas. Esto muestra que
> la calidad no consiste solamente en producir texto correcto: la salida también
> debe cumplir el contrato que consumirán los componentes posteriores.

## Preguntas probables y respuestas breves

### ¿Qué significa “observable” en este proyecto?

Significa poder reconstruir una consulta a partir de sus artefactos: versión
del corpus y del índice, modelos y parámetros, fragmentos y puntuaciones,
contexto, respuesta, citas, estado, errores y tiempos. No implica necesariamente
tener un dashboard.

### ¿La observabilidad es una métrica de calidad?

No. La traza no garantiza que la respuesta sea correcta. Es un artefacto
diagnóstico que permite explicar los resultados de las métricas y localizar el
componente donde aparece un fallo.

### ¿Qué significa evidencia “gold” o de referencia?

Es la sección o el registro que se identificó manualmente como necesario para
responder una pregunta. Sirve para comprobar si la recuperación y las citas
incluyeron la evidencia esperada.

### ¿Por qué usar normativa del TEC?

Porque es un dominio público, institucional, estructurado y en español de Costa
Rica. Permitió construir un corpus reproducible con URL, fecha y huella SHA-256.
Es un caso de estudio, no una representación de todo el español latinoamericano.

### ¿Por qué 25 documentos y 40 preguntas?

El objetivo era construir una prueba de concepto pequeña y auditable. Se creó
una pregunta directa por documento, ocho preguntas para exigir combinación de
evidencia y siete preguntas deliberadamente ausentes para evaluar abstención.

### ¿Por qué multilingual-e5-small y Qwen3.5:9B?

Se buscó una configuración local y reproducible con recursos moderados.
Multilingual E5 ofrece representaciones multilingües de 384 dimensiones y
Qwen3.5:9B permitió ejecutar la generación localmente mediante Ollama.

### ¿Cómo se explica 93,9 % de recuperación frente a 70 % de aprobación?

Recuperar al menos un registro relacionado no garantiza reunir toda la
evidencia, seleccionar el fragmento exacto, generar una respuesta completa ni
producir citas estructuralmente válidas. Esa diferencia es justamente el
hallazgo central.

### ¿Por qué fallaron las preguntas multisección?

Porque el top-5 podía recuperar una parte de la respuesta, pero no todas las
secciones necesarias. El próximo paso es evaluar recuperación híbrida,
reranking, descomposición de consultas y medidas de cobertura conjunta.

### ¿El sistema alucinó cuando no había información?

En las siete preguntas deliberadamente no respondibles, el sistema se abstuvo
correctamente y produjo `not_found`. Este resultado debe interpretarse dentro
del conjunto pequeño evaluado, no como una garantía general.

### ¿Se puede generalizar a todo el español latinoamericano?

Todavía no. El experimento utiliza normativa de un único dominio costarricense.
El título expresa la dirección de diseño; la generalización lingüística y
documental requiere incorporar otros países y dominios.

### ¿Cuáles son los próximos pasos?

Comparar recuperación densa, léxica e híbrida; añadir reranking y estrategias
para evidencia distribuida; robustecer la validación de citas; evaluar otros
modelos locales; ampliar países y dominios; y realizar revisión humana con más
de una persona.

## Recomendaciones para la interacción

- Empezar preguntando: “¿Quieres la versión de treinta segundos o el recorrido
  completo?”.
- Mantenerse a un lado del póster para no taparlo.
- Señalar la zona correspondiente, pero mantener contacto visual con la persona.
- Hacer una pausa después del hallazgo principal para permitir preguntas.
- No intentar mencionar todas las métricas; usar la tabla solo cuando la
  conversación requiera detalle.
- Tener preparados los casos q029, q025 y q032 como ejemplos técnicos.
- Cerrar mencionando que es una prueba de concepto y que la investigación
  continúa.

## Verificación pendiente del número de orden

El correo de aceptación y el pie del póster indican “Sesión 2, orden 12”. Sin
embargo, la lista oficial publicada actualmente ubica el trabajo en la sesión
del segundo día con el orden 9. Conviene confirmar con la organización cuál
número se utilizará para la ubicación física del póster.
