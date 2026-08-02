# Bitácora de revisión manual de respuestas RAG

## Propósito

Esta bitácora conserva el razonamiento humano detrás de cada valoración. El
libro de Excel contiene los valores estructurados y las métricas; este documento
explica por qué se seleccionó cada valor.

La revisión corresponde a la corrida:

```text
results/rag-evaluation/2026-07-28/
qwen3.5-9b-normalized-citations/
```

Libro de trabajo:

```text
outputs/rag-manual-review-20260728/
revision_manual_rag_completada.xlsx
```

Persona revisora:

```text
Nicole Tatiana Parra Valverde
```

Fecha de revisión:

```text
2026-07-28
```

## Estado

| Estado | Cantidad |
|---|---:|
| Preguntas totales | 40 |
| Revisadas | 40 |
| Pendientes | 0 |
| Avance | 100.0% |

## q001

### Pregunta

> ¿En qué plazo y por cuáles medios puede una persona estudiante solicitar la
> reposición de una evaluación que no realizó por una ausencia justificada?

### Elementos esperados

La pregunta solicita dos componentes:

1. el plazo para presentar la solicitud;
2. los medios permitidos para presentarla.

La evidencia `gold`, correspondiente al artículo 66, establece un plazo de tres
días hábiles después de la evaluación y permite hacer la solicitud:

- personalmente;
- mediante correo electrónico remitido a la cuenta oficial de la Institución;
- por medio de una persona autorizada.

### Análisis de la respuesta

La primera oración de la respuesta generada incluye correctamente el plazo y
los tres medios. Después añade una excepción para casos en los que la persona
estudiante no pueda realizar el trámite dentro del plazo por razones de salud
comprobadas.

Esa información adicional no constituye una alucinación: también aparece en el
fragmento `F2` del artículo 66. El modelo empleó precisamente `F2` como cita.
`F1` y `F2` son fragmentos diferentes del mismo `Record ID gold`,
`tec-rrea-2025::article-66`.

### Decisión acordada

| Criterio | Valor | Razón |
|---|---|---|
| Corrección factual | Correcta | El plazo, los medios y la excepción son verdaderos según el artículo 66. |
| Cobertura | Completa | Respondió las dos partes solicitadas. |
| Fidelidad a fuentes | Total | Todas las afirmaciones aparecen en el fragmento citado `F2`. |
| Claridad | Clara | La respuesta principal aparece primero y la excepción se explica por separado. |
| Gold adecuado | Sí | El artículo seleccionado contiene exactamente la evidencia necesaria. |
| Conclusión manual | Aprobada | La respuesta es correcta, completa, clara y está respaldada. |

### Nota registrada

> Responde correctamente el plazo y los tres medios solicitados. Añade una
> excepción médica pertinente y respaldada por F2, correspondiente al mismo
> artículo 66 definido como evidencia gold.

## q002

### Pregunta

> ¿En qué consiste la beca de excelencia académica del TEC y a cuántos
> estudiantes de primer ingreso se otorga?

### Elementos esperados

La pregunta solicita dos datos:

1. el beneficio otorgado por la beca;
2. la cantidad de estudiantes de primer ingreso que la reciben.

El artículo 35 establece que la beca consiste en la exoneración del pago de los
derechos de estudio durante toda la carrera y que se otorga a los cien
estudiantes de primer ingreso con mayor puntaje.

### Análisis de la respuesta

La respuesta generada incluye correctamente los dos elementos solicitados.
También enumera varios criterios utilizados para calcular el puntaje y añade los
requisitos de créditos necesarios para conservar la beca.

Los criterios de selección están respaldados por `F2`. Los requisitos de
mantenimiento están respaldados por `F1`. Por eso la información adicional no
reduce la corrección factual ni la fidelidad.

La debilidad está en la presentación: la respuesta es más extensa de lo
necesario para una pregunta directa y termina con una llave de cierre sobrante,
`}`. El defecto no cambia el significado de la respuesta, pero justifica marcar
la claridad como mejorable.

### Decisión acordada

| Criterio | Valor | Razón |
|---|---|---|
| Corrección factual | Correcta | El beneficio, la cantidad, los criterios y los requisitos adicionales coinciden con el artículo 35. |
| Cobertura | Completa | Respondió las dos partes solicitadas. |
| Fidelidad a fuentes | Total | `F2` respalda la selección y `F1` los requisitos para conservar la beca. |
| Claridad | Mejorable | Añade información no solicitada y presenta una llave sobrante al final. |
| Gold adecuado | Sí | El artículo 35 contiene directamente la respuesta. |
| Conclusión manual | Aprobada | Los defectos de redacción son menores y el contenido es correcto y verificable. |

### Nota registrada

> Responde correctamente el beneficio y la cantidad de estudiantes. Los
> criterios de selección y requisitos de mantenimiento añadidos están
> respaldados, pero hacen la respuesta innecesariamente extensa. Presenta
> además una llave de cierre sobrante al final.

## q003

### Pregunta

> ¿Se puede equiparar un Trabajo Final de Graduación en el TEC?

### Análisis de la respuesta

La respuesta indica directamente que los Trabajos Finales de Graduación no son
susceptibles de equiparación. `F1` contiene exactamente esa disposición y
corresponde al artículo 29 definido como evidencia `gold`.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

### Nota registrada

> Respuesta directa y completamente respaldada por F1, correspondiente al
> artículo 29 definido como evidencia gold.

## q004

### Pregunta

> ¿Cuál es el objetivo general del Programa de Residencias Estudiantiles del
> TEC?

### Análisis de la respuesta

La respuesta reproduce los componentes centrales del artículo 1:

- atracción y permanencia de estudiantes;
- condición socioeconómica limitada;
- procedencia de zonas alejadas o de difícil acceso;
- meta profesional;
- formación integral;
- equidad e igualdad de oportunidades.

El fragmento citado `F1` es también la evidencia `gold`.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

### Nota registrada

> Reproduce correctamente el objetivo general del Programa de Residencias
> Estudiantiles y está totalmente respaldada por F1.

## q005

### Pregunta

> ¿Quiénes pueden dirigirse a la Defensoría Estudiantil cuando se vulneran
> derechos o intereses de estudiantes?

### Análisis de la respuesta

La respuesta identifica correctamente:

- estudiantes regulares del ITCR;
- tutores;
- representantes judiciales o extrajudiciales;
- funcionarios del ITCR.

Sin embargo, omite una categoría incluida en el artículo 8: estudiantes
regulares de cualquier ente adscrito a la Federación de Estudiantes. Por eso la
información afirmada es verdadera, pero la enumeración no está completa.

La respuesta también añade información procedente de `F2` sobre asistencia
legal en procesos disciplinarios. Esa información está respaldada, pero se
aleja de la pregunta principal y hace menos directa la respuesta.

Este caso muestra por qué corrección y cobertura son criterios distintos:

- `Corrección factual = Correcta`, porque no hay afirmaciones falsas;
- `Cobertura = Parcial`, porque falta una categoría relevante.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Parcial |
| Fidelidad a fuentes | Total |
| Claridad | Mejorable |
| Gold adecuado | Sí |
| Conclusión manual | Revisar |

### Nota registrada

> Identifica correctamente estudiantes del ITCR, tutores, representantes y
> funcionarios, pero omite estudiantes de entes adscritos a la Federación de
> Estudiantes. La información adicional de F2 está respaldada, aunque desvía la
> respuesta.

## q006

### Pregunta

> ¿Cuántas horas semanales debe comprometer una persona de posgrado que solicita
> por primera vez una beca de asistencia para investigación o extensión?

### Análisis de la respuesta

La respuesta contiene los tres elementos relevantes:

- compromiso presentado por escrito;
- al menos veinte horas semanales para maestría;
- cuarenta horas semanales para doctorado.

Los tres aparecen directamente en `F1`, correspondiente al artículo 14.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

### Nota registrada

> Indica correctamente el compromiso escrito de veinte horas semanales para
> maestría y cuarenta para doctorado, respaldado por F1.

## q007

### Pregunta

> ¿En qué plazo puede una persona sancionada presentar recursos de revocatoria
> o apelación y qué instancias los resuelven?

### Análisis de la respuesta

La respuesta identifica correctamente:

- el plazo de tres días hábiles;
- el Tribunal Disciplinario Formativo para resolver la revocatoria;
- la autoridad de la Vicerrectoría de Vida Estudiantil y Servicios Académicos
  para resolver la apelación.

También añade que ambas instancias cuentan con ocho días hábiles para resolver.
Este dato no era necesario, pero aparece en `F1` y resulta pertinente.

La respuesta esperada también menciona que los recursos pueden presentarse por
escrito o por medios electrónicos. No se penalizó su omisión porque la pregunta
solicita explícitamente el plazo y las instancias, no los medios de
presentación.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

### Nota registrada

> Responde el plazo de tres días hábiles y las instancias que resuelven cada
> recurso. Los plazos de resolución añadidos también están respaldados por F1.

## q008

### Pregunta

> ¿Qué requisito académico mínimo permite optar por un cambio de carrera y qué
> criterio se usa para seleccionar?

### Análisis de la respuesta

La pregunta contiene dos partes y ambas fueron respondidas:

1. haber cursado y aprobado seis créditos del plan de estudios;
2. utilizar el promedio ponderado de todas las materias del último periodo.

El fragmento `F1` contiene directamente los dos elementos y corresponde a la
evidencia `gold`.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

### Nota registrada

> Responde los dos elementos solicitados: seis créditos cursados y aprobados, y
> selección por promedio ponderado del último periodo.

## q009

### Pregunta

> ¿Cuál es el propósito de la Prueba de Aptitud Académica del TEC?

### Análisis de la respuesta

La respuesta señala que el propósito es contribuir a predecir el rendimiento
académico de las personas que solicitan ingreso. Esa formulación coincide con
la oración del artículo 3 que define explícitamente el propósito.

El texto `gold` también indica que se trata de un test psicoeducativo y que es
uno de los criterios de admisión. Esos datos describen la naturaleza y el uso de
la prueba, pero no son necesarios para responder únicamente por su propósito.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

### Nota registrada

> Expresa exactamente el propósito de la prueba: contribuir a predecir el
> rendimiento académico de quienes solicitan ingreso.

## q010

### Pregunta

> ¿Cuál es el promedio mínimo requerido en programas de grado para obtener
> graduación de honor?

### Análisis de la respuesta

La respuesta establece correctamente que el promedio final ponderado debe ser
igual o superior a 90.

El artículo también especifica que deben incluirse las asignaturas aprobadas por
suficiencia. La respuesta no menciona ese detalle. Se mantuvo la cobertura como
completa porque la pregunta solicita el umbral mínimo y no los componentes del
cálculo.

Esta decisión sigue un criterio orientado a la pregunta: se evalúa si la
respuesta atiende lo solicitado, no si reproduce todos los detalles de la
respuesta `gold`.

### Decisión acordada

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

### Nota registrada

> Responde correctamente el promedio mínimo solicitado, igual o superior a 90.
> No menciona las asignaturas por suficiencia, pero ese detalle no era una parte
> explícita de la pregunta.

## Resumen después del primer bloque

| Indicador | Resultado |
|---|---:|
| Revisiones completas | 10 de 40 |
| Avance | 25.0% |
| Aprobadas | 9 |
| Para revisar | 1 |
| Rechazadas | 0 |
| Corrección factual estricta | 100.0% |
| Fidelidad total | 100.0% |
| Cobertura completa | 90.0% |

La única respuesta clasificada como `Revisar` en este bloque es `q005`.

## q011

### Pregunta

> ¿Cuántos créditos puede valer un Trabajo Final de Graduación?

### Análisis y decisión

La respuesta indica un mínimo de siete y un máximo de doce créditos. Ambos
valores aparecen directamente en `F1`.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Responde exactamente el valor mínimo de siete créditos y el máximo de doce
> créditos establecido en F1.

## q012

### Pregunta

> ¿Qué exigencias de idioma y autenticación se aplican a ciertos documentos
> extranjeros para reconocer o equiparar un grado o título?

### Análisis de la respuesta

La respuesta explica correctamente:

- traducción al español;
- autenticación de originales;
- posibilidad de certificar una copia fiel;
- secuencia de firmas para la autenticación.

Los datos están respaldados por `F2` y `F3`. Sin embargo, omite el procedimiento
de terceros países que se puede utilizar cuando Costa Rica no tiene consulado
en el país donde se expide el documento. Esa alternativa aparece directamente
en la evidencia `gold`.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Parcial |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Revisar |

Nota registrada:

> Explica correctamente traducción y autenticación, e incorpora la secuencia
> respaldada por F3. Omite el procedimiento de terceros países cuando no existe
> consulado de Costa Rica.

## q013

### Pregunta

> ¿Cuál es el mínimo y el máximo de horas semanales que se pueden asignar a un
> estudiante asistente?

### Análisis y decisión

La respuesta proporciona el rango solicitado de cinco a diez horas. También
distingue el caso de la Beca Estudiante Asistente Especial, cuyo rango es de
diez a veinte horas. La distinción está explícitamente formulada y respaldada,
por lo que no genera una contradicción.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Responde correctamente el rango general de cinco a diez horas. Distingue
> además el caso especial de diez a veinte horas, respaldado por F3.

## q014

### Pregunta

> ¿Cuál es el rango de horas semanales de una Beca Estudiante Asistente
> Especial?

### Análisis y decisión

La respuesta señala exactamente un mínimo de diez y un máximo de veinte horas.
`F1` contiene ambos valores.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Responde exactamente el rango de diez a veinte horas semanales para la Beca
> Estudiante Asistente Especial, respaldado por F1.

## q015

### Pregunta

> ¿Cuál es el máximo de horas semanales para un estudiante asistente de
> investigación o extensión y cuál es la excepción?

### Análisis y decisión

La respuesta incluye correctamente:

- máximo ordinario de veinte horas;
- máximo excepcional de cuarenta horas;
- condición de cursar un TFG que forme parte de un proyecto de investigación o
  extensión inscrito en la VIE.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Incluye correctamente el máximo ordinario de veinte horas y la excepción de
> cuarenta horas para TFG vinculados con proyectos inscritos en la VIE.

## q016

### Pregunta

> ¿Qué programa recibe prioridad en la asignación de egresos del Fondo
> Solidario de Desarrollo Estudiantil?

### Análisis de la respuesta

El sistema respondió:

> No encontrado en el contexto.

La respuesta sí existe en el corpus. El artículo 18 establece que se asignarán
prioritariamente recursos para cubrir el Programa de Becas y Préstamos.

El artículo 18 no apareció entre los cinco fragmentos recuperados. El modelo
solo recibió artículos relacionados con principios, fines y becas de asistencia.
Por eso la abstención fue prudente respecto del contexto recibido, pero el
sistema RAG completo falló.

El caso se clasifica como fallo de recuperación:

```text
pregunta respondible
→ evidencia gold no recuperada
→ modelo se abstiene
→ respuesta final incorrecta
```

| Criterio | Valor |
|---|---|
| Corrección factual | Incorrecta |
| Cobertura | Insuficiente |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> El sistema se abstuvo porque el artículo 18 no apareció entre los cinco
> fragmentos recuperados. La respuesta existe en el corpus: se prioriza el
> Programa de Becas y Préstamos. Fallo de recuperación.

## q017

### Pregunta

> ¿Qué condiciones debe cumplir un estudiante para recibir financiamiento para
> actividades en el exterior?

### Elementos esperados

El artículo 11 establece cuatro condiciones:

1. demostrar participación destacada;
2. contar con algún financiamiento del organismo patrocinador;
3. demostrar aprovechamiento académico;
4. no haber sido objeto de sanción.

### Análisis de la respuesta

El artículo 11 no apareció entre los cinco fragmentos recuperados. La respuesta
utilizó otros artículos del mismo reglamento y describió:

- alcance general del fondo;
- tipos de actividades;
- condiciones del evento;
- firma del contrato.

Esta información está relacionada y es mayormente verdadera, pero no responde
ninguna de las cuatro condiciones solicitadas.

La fidelidad se calificó como parcial porque la mayoría de las afirmaciones sí
están respaldadas, pero `F4` se usa para afirmar que el evento debe estar
dirigido a estudiantes de Diplomado o Bachillerato. El fragmento realmente
define el alcance del reglamento, no una condición concreta del evento.

| Criterio | Valor |
|---|---|
| Corrección factual | Parcial |
| Cobertura | Insuficiente |
| Fidelidad a fuentes | Parcial |
| Claridad | Mejorable |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> No recuperó el artículo 11 ni respondió las cuatro condiciones del
> estudiante. Presenta requisitos relacionados y mayormente respaldados, pero
> F4 se interpreta de forma demasiado amplia.

## q018

### Pregunta

> ¿Qué gastos cubre la Beca Mauricio Campos y qué exoneración incluye?

### Análisis y decisión

La respuesta incluye alojamiento, alimentación, transporte, material didáctico
y exoneración de los créditos matriculados. También añade información general
de `F4` sobre derechos y otros costos de estudio, la cual está respaldada y no
contradice la respuesta principal.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Incluye correctamente alojamiento, alimentación, transporte, material
> didáctico y exoneración de créditos. La información adicional de F4 también
> está respaldada.

## q019

### Pregunta

> ¿A más tardar cuándo debe darse la declaratoria oficial del proceso electoral
> estudiantil de la FEITEC?

### Análisis y decisión

La respuesta indica exactamente la última semana de abril y cita el artículo
correspondiente.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Responde exactamente que la declaratoria oficial debe darse a más tardar en
> la última semana de abril, respaldado por F1.

## q020

### Pregunta

> ¿Con cuánta anticipación debe el DAE convocar las sesiones ordinarias y
> extraordinarias del Plenario de Movimiento Estudiantil?

### Análisis y decisión

La respuesta incluye correctamente los dos plazos:

- siete días naturales para las sesiones ordinarias;
- tres días naturales para las sesiones extraordinarias.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Responde ambos plazos: siete días naturales para sesiones ordinarias y tres
> para extraordinarias, respaldados por F1.

## Resumen después del segundo bloque

| Indicador | Resultado |
|---|---:|
| Revisiones completas | 20 de 40 |
| Avance | 50.0% |
| Aprobadas | 16 |
| Para revisar | 2 |
| Rechazadas | 2 |
| Respuestas factualmente correctas | 18 |
| Respuestas factualmente parciales | 1 |
| Respuestas factualmente incorrectas | 1 |
| Tasa estricta de corrección | 90.0% |
| Puntaje factual ponderado | 92.5% |
| Fidelidad total | 94.7% |
| Cobertura completa | 80.0% |

En este bloque:

- `q012` quedó para revisar por una omisión;
- `q016` fue rechazada por fallo de recuperación y abstención incorrecta;
- `q017` fue rechazada por recuperar evidencia relacionada, pero no la
  necesaria para responder.

## q021

### Pregunta

> ¿Cada cuánto sesiona ordinariamente el Directorio de Asambleas Estudiantiles
> y con qué anticipación se convocan sus sesiones?

### Análisis de la respuesta

La respuesta indica correctamente que el Directorio sesiona ordinariamente
cada quince días y que las sesiones ordinarias deben convocarse con cinco días
hábiles de anticipación. Ambas afirmaciones están respaldadas por la evidencia
recuperada.

Sin embargo, la expresión «sus sesiones» también comprende las sesiones
extraordinarias. La fuente establece que estas deben convocarse con
veinticuatro horas de anticipación, dato que la respuesta omitió. La respuesta
es factualmente correcta en lo que afirma, pero su cobertura es parcial.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Parcial |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Revisar |

Nota registrada:

> Responde correctamente la frecuencia ordinaria y los cinco días de
> anticipación, pero omite que las sesiones extraordinarias deben convocarse
> veinticuatro horas antes.

## q022

### Pregunta

> ¿Cuándo se considera recibida una comunicación enviada al correo
> institucional y qué ocurre si se usa un correo particular?

### Análisis y decisión

La respuesta cubre los dos componentes solicitados: la comunicación se
considera recibida al finalizar el día hábil siguiente a su envío y el uso de
una cuenta de correo particular produce la nulidad de la comunicación. La
fuente `F2` respalda ambas afirmaciones.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Responde correctamente cuándo se considera recibida la comunicación y la
> nulidad de utilizar un correo particular, respaldado por F2.

## q023

### Pregunta

> ¿Ante cuál instancia y en qué forma debe presentarse una denuncia por
> hostigamiento sexual?

### Análisis y decisión

La respuesta identifica correctamente a la Fiscalía Institucional como la
instancia receptora y explica que la denuncia debe presentarse por escrito.
También detalla los datos de las partes, la descripción de los hechos, las
pruebas, los medios para notificaciones y las firmas requeridas. Estos
elementos están respaldados por `F3`.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Identifica correctamente la Fiscalía, la presentación escrita y los datos,
> pruebas, notificaciones y firmas requeridos, respaldado por F3.

## q024

### Pregunta

> ¿Cómo puede presentarse una denuncia por discriminación por orientación
> sexual, identidad o expresión de género?

### Análisis y decisión

La respuesta identifica la instancia correspondiente y distingue las
modalidades presencial y digital. Además, incluye correctamente las firmas y
la información que debe contener la denuncia. La respuesta está respaldada por
`F1` y satisface lo solicitado.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Responde correctamente la instancia, las modalidades presencial o digital,
> las firmas y la información requerida, respaldado por F1.

## q025

### Pregunta

> ¿Cómo se realiza la votación para elegir al tercer representante estudiantil
> ante el Consejo Institucional?

### Análisis de la respuesta

El contenido visible responde correctamente que la elección se realiza
mediante sufragio universal y público. Los detalles adicionales también están
respaldados por los fragmentos mostrados.

El problema no es factual, sino estructural. En el texto de la respuesta
aparecen citas `F1`, `F2`, `F3` y `F4`, pero el campo estructurado de citas
declara únicamente `F3` y `F4`. Esto significa que la salida incumple el
contrato de datos del pipeline: la representación legible y la representación
que consumiría otro componente no coinciden.

Se conservan «Correcta», «Completa», «Total» y «Clara» para describir la
calidad del contenido. La conclusión se marca «Rechazada» porque el sistema
debe entregar una salida estructuralmente válida, no solo texto correcto.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> El contenido responde correctamente que la votación es por sufragio
> universal y público y los detalles añadidos están respaldados. Se rechaza la
> salida porque las citas visibles F1-F4 no coinciden con el campo
> estructurado, que declara solo F3 y F4.

## q026

### Pregunta

> ¿Cómo se solicita un cambio de carrera, qué requisito académico se exige y
> qué criterio se usa para asignar los cupos?

### Análisis y decisión

La respuesta combina correctamente información de dos secciones: solicitud
escrita ante el Departamento de Admisión y Registro durante el periodo
establecido en el calendario; aprobación de al menos seis créditos; selección
por promedio ponderado del último periodo; y límite inicial de cupos del cinco
por ciento, sujeto al aumento previsto por la norma. Las dos fuentes `gold`
necesarias fueron utilizadas.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Combina correctamente solicitud escrita, periodo, seis créditos, promedio
> ponderado y límite inicial del 5 %, utilizando las dos fuentes gold.

## q027

### Pregunta

> ¿Qué condiciones académicas y disciplinarias debe cumplir una persona de
> grado para obtener graduación de honor?

### Análisis y decisión

La respuesta incluye los requisitos operativos solicitados: no haber reprobado
asignaturas, no haber recibido sanciones y obtener un promedio igual o
superior a 90, incluyendo las asignaturas aprobadas por suficiencia. La norma
también emplea una formulación general sobre haberse distinguido
permanentemente, pero la respuesta sí contiene las condiciones verificables
que pide la pregunta.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Incluye los requisitos operativos: no reprobar asignaturas, no recibir
> sanciones y promedio igual o superior a 90 con asignaturas por suficiencia.

## q028

### Pregunta

> ¿Cómo cambian los límites de horas semanales entre un estudiante asistente,
> un asistente especial y un asistente de investigación o extensión?

### Análisis de la respuesta

La respuesta presenta correctamente los dos primeros rangos:

- estudiante asistente: de cinco a diez horas;
- estudiante asistente especial: de diez a veinte horas.

En el tercer caso invierte la regla. Para investigación o extensión, el máximo
ordinario es de veinte horas y la excepción permite llegar a cuarenta. La
respuesta lo plantea al revés: usa cuarenta como máximo general y veinte como
excepción. Esa inversión altera una parte sustancial de la comparación.

La cobertura se considera completa porque intenta responder los tres casos.
La corrección y la fidelidad son parciales porque solo dos de los tres están
bien y la tercera afirmación contradice la fuente. La claridad se marca como
confusa debido a la inversión. Además, existe una discrepancia entre las citas
visibles y las citas del campo estructurado.

| Criterio | Valor |
|---|---|
| Corrección factual | Parcial |
| Cobertura | Completa |
| Fidelidad a fuentes | Parcial |
| Claridad | Confusa |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> Presenta correctamente los rangos de cinco a diez y de diez a veinte horas,
> pero invierte la regla de investigación: el máximo ordinario es veinte y la
> excepción es cuarenta. Además, las citas visibles y estructuradas no
> coinciden.

## q029

### Pregunta

> Si una persona estudiante solicita por correo la reposición de una
> evaluación, ¿qué plazo tiene, qué cuenta debe usar y cuándo se considera
> recibida la solicitud?

### Análisis de la respuesta

El sistema respondió «No encontrado en el contexto», aunque la pregunta es
respondible con el corpus. El recuperador encontró un fragmento asociado al
artículo 66, pero no la parte del artículo que contiene el plazo de tres días
hábiles y el requisito de usar la cuenta institucional. Tampoco recuperó el
artículo 5, necesario para determinar cuándo se considera recibida la
comunicación.

Este ejemplo revela que acertar el `Record ID` no garantiza recuperar el
fragmento correcto dentro del documento. Por tanto, el indicador automático de
recuperación por documento puede verse positivo y, aun así, el contexto
entregado al modelo puede ser insuficiente. Es un fallo de recuperación a nivel
de fragmento, seguido por una abstención incorrecta a nivel del sistema
completo.

| Criterio | Valor |
|---|---|
| Corrección factual | Incorrecta |
| Cobertura | Insuficiente |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> El sistema se abstuvo. Recuperó un fragmento del artículo 66, pero no la
> parte que contiene el plazo y el correo, y tampoco recuperó el artículo 5.
> Es un fallo de recuperación a nivel de fragmento.

## q030

### Pregunta

> ¿Cuáles de los documentos requeridos para reconocer o equiparar un título
> extranjero deben traducirse y autenticarse?

### Elementos esperados

La respuesta debía enumerar tres documentos:

1. el diploma o su equivalente;
2. la certificación oficial de las asignaturas y calificaciones;
3. el documento que acredita que la institución está autorizada o legalmente
   habilitada para otorgar el título.

### Análisis de la respuesta

La respuesta explica correctamente reglas generales de traducción y
autenticación, pero no enumera los tres documentos solicitados. Además, añade
información de movilidad estudiantil y de diplomas de posgrado que no sustituye
la lista requerida.

Las afirmaciones realizadas sí están respaldadas por los fragmentos citados;
por esa razón, la fidelidad es total. No obstante, la corrección es parcial y
la cobertura insuficiente porque la respuesta se desplaza hacia información
relacionada, pero no entrega el núcleo solicitado.

| Criterio | Valor |
|---|---|
| Corrección factual | Parcial |
| Cobertura | Insuficiente |
| Fidelidad a fuentes | Total |
| Claridad | Mejorable |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> No enumera los tres documentos solicitados. Explica reglas generales de
> traducción y autenticación y añade información de movilidad y posgrado; las
> afirmaciones están respaldadas, pero no responden la lista requerida.

## Resumen después del tercer bloque

| Indicador | Resultado |
|---|---:|
| Revisiones completas | 30 de 40 |
| Avance | 75.0% |
| Aprobadas | 21 |
| Para revisar | 3 |
| Rechazadas | 6 |
| Respuestas factualmente correctas | 25 |
| Respuestas factualmente parciales | 3 |
| Respuestas factualmente incorrectas | 2 |
| Tasa estricta de corrección | 83.3% |
| Puntaje factual ponderado | 88.3% |
| Fidelidad total | 92.9% |
| Cobertura completa | 76.7% |

En este bloque:

- `q021` quedó para revisar por omitir el plazo de convocatoria de las sesiones
  extraordinarias;
- `q025` fue rechazada por incumplir el contrato de citas estructuradas, aunque
  su contenido visible es correcto;
- `q028` fue rechazada por invertir la regla ordinaria y la excepción;
- `q029` mostró un fallo de recuperación a nivel de fragmento;
- `q030` fue rechazada por no enumerar los documentos pedidos.

## q031

### Pregunta

> ¿Qué debe contener una denuncia por hostigamiento sexual y qué plazo recibe
> la persona denunciada para responder después de su ampliación?

### Elementos esperados

La pregunta combina dos artículos:

1. el artículo 27, que define el contenido obligatorio de la denuncia;
2. el artículo 30, que establece el traslado y el plazo de respuesta después
   de la ampliación.

La denuncia debe identificar a las partes, describir los hechos, lugares y
fechas, mencionar posibles testigos y pruebas, señalar un medio para
notificaciones e incluir fecha y firmas. Después de la ampliación, la Comisión
Investigadora debe dar traslado dentro de dos días hábiles y conceder ocho días
hábiles para responder por escrito y ofrecer prueba de descargo.

### Análisis de la respuesta

El artículo 27 no apareció entre los cinco fragmentos recuperados. Por esa
razón, el modelo declaró que el contexto no especificaba el contenido
obligatorio de la denuncia y dejó sin responder la primera mitad.

Sí recuperó el artículo 30 y respondió correctamente que la persona denunciada
dispone de ocho días hábiles para referirse por escrito a los hechos, ofrecer
prueba de descargo y señalar un medio de notificación. También mencionó el
plazo de tres días para que la persona denunciante amplíe o aclare la denuncia,
información respaldada por los fragmentos, aunque no era el dato principal
solicitado.

La corrección y la cobertura son parciales porque se respondió uno de dos
componentes sustantivos. La fidelidad es total: las afirmaciones realizadas
están respaldadas. Se rechaza la respuesta porque la omisión afecta la mitad de
una pregunta de varias secciones.

| Criterio | Valor |
|---|---|
| Corrección factual | Parcial |
| Cobertura | Parcial |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> Responde correctamente el plazo de ocho días y el alcance del descargo, pero
> omite el contenido obligatorio de la denuncia porque el artículo 27 no fue
> recuperado.

## q032

### Pregunta

> ¿Dónde y cómo se presenta una denuncia por discriminación y qué medidas
> cautelares pueden solicitarse para proteger a la persona denunciante?

### Análisis del contenido

El texto generado identifica correctamente:

- la Fiscalía contra la discriminación como instancia receptora;
- la presentación presencial o con firma digital;
- la información que debe describir la denuncia;
- la prohibición de acercamientos, perturbaciones o represalias;
- la reubicación temporal del puesto o curso;
- la separación temporal del cargo con goce salarial;
- otras medidas necesarias para proteger a la persona denunciante.

Los fragmentos `F1` y `F2` del reglamento contra la discriminación contienen la
evidencia principal. El texto también utiliza `F5`, proveniente del reglamento
contra el hostigamiento sexual, para añadir medidas equivalentes aplicables a
personas funcionarias y estudiantes.

### Error estructural

La salida visible utiliza las citas `F1`, `F2` y `F5`. Sin embargo, el campo
estructurado `citations` declara solamente `F2` y `F1`. La capa de validación
detectó la diferencia y produjo un `GenerationValidationError`.

Al igual que en `q025`, se separa la evaluación del contenido de la evaluación
de la salida completa:

```text
contenido factual correcto
+ cobertura suficiente
+ afirmaciones respaldadas
≠ salida utilizable
```

Por eso los criterios de contenido reciben valores positivos, pero la
conclusión es «Rechazada». Un componente posterior del sistema no podría
confiar en dos representaciones incompatibles de las citas.

| Criterio | Valor |
|---|---|
| Corrección factual | Correcta |
| Cobertura | Completa |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> El contenido visible responde correctamente dónde y cómo presentar la
> denuncia y enumera medidas cautelares respaldadas. Se rechaza porque las
> citas visibles F1, F2 y F5 no coinciden con el campo estructurado, que
> declara únicamente F2 y F1.

## q033

### Pregunta

> ¿En qué momentos del año se realiza la declaratoria del proceso electoral de
> la FEITEC y se elige al tercer representante estudiantil ante el Consejo
> Institucional?

### Elementos esperados

La respuesta requiere combinar dos documentos:

- la declaratoria del proceso electoral de la FEITEC debe darse a más tardar
  en la última semana de abril;
- el periodo de elección del tercer representante inicia en septiembre y la
  elección se realiza durante octubre.

### Análisis de la respuesta

El modelo recuperó el artículo 11 del Código Electoral Estudiantil y respondió
correctamente la fecha límite de abril. No recuperó el artículo 19 del
reglamento del tercer representante, por lo que manifestó que no había
información específica para responder la segunda parte.

La abstención parcial es prudente respecto del contexto recibido, pero el
sistema RAG completo debía recuperar ambos artículos. La respuesta es parcial,
fiel a lo que sí recibió y clara, pero no satisface la pregunta combinada.

| Criterio | Valor |
|---|---|
| Corrección factual | Parcial |
| Cobertura | Parcial |
| Fidelidad a fuentes | Total |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Rechazada |

Nota registrada:

> Responde correctamente que la declaratoria debe darse a más tardar en la
> última semana de abril, pero omite que la elección del tercer representante
> inicia en septiembre y se realiza en octubre porque no recuperó el artículo
> 19.

## Criterio común para q034-q040

Las últimas siete preguntas son de tipo `unanswerable`: fueron diseñadas
deliberadamente para solicitar información que no existe en el corpus. Evalúan
si el sistema sabe abstenerse en lugar de inventar una respuesta plausible.

En los siete casos, el sistema devolvió:

> No encontrado en el contexto.

La asignación acordada es:

- corrección factual: `No aplica`, porque no se formuló una afirmación factual;
- cobertura: `No aplica`, porque la pregunta no debía responderse con el
  corpus;
- fidelidad: `No aplica`, porque no se presentaron afirmaciones ni citas;
- claridad: `Clara`, porque la abstención se entiende;
- gold adecuado: `Sí`, porque la referencia esperaba precisamente que la
  información no estuviera disponible;
- conclusión: `Aprobada`, porque abstenerse era la conducta correcta.

Es importante que `No aplica` no se interprete como un fallo. En este tipo de
pregunta, representa una decisión correcta de no inventar información.

## q034

### Pregunta

> ¿Cuál es el precio actual del almuerzo en la soda del Campus Tecnológico
> Central?

### Análisis y decisión

El corpus contiene reglamentos institucionales, pero no precios actuales de la
soda. Los fragmentos recuperados sobre residencias estudiantiles no permiten
deducir el monto. La abstención evita una alucinación numérica.

| Criterio | Valor |
|---|---|
| Corrección factual | No aplica |
| Cobertura | No aplica |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> El precio actual del almuerzo no forma parte del corpus. La abstención es
> correcta y evita inventar un monto.

## q035

### Pregunta

> ¿Cuál es el horario vigente del autobús entre San José y el Campus
> Tecnológico Central?

### Análisis y decisión

El horario vigente es información operativa y cambiante. Ningún documento del
corpus contiene un itinerario actual verificable. El sistema no transformó
fragmentos institucionales relacionados con campus o transporte en un horario
inventado.

| Criterio | Valor |
|---|---|
| Corrección factual | No aplica |
| Cobertura | No aplica |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> El horario vigente del autobús no forma parte del corpus. La abstención es
> correcta y evita presentar un horario posiblemente desactualizado.

## q036

### Pregunta

> ¿Cuál es la contraseña actual de la red inalámbrica para estudiantes del
> TEC?

### Análisis y decisión

La contraseña no aparece en el corpus. Además de evitar una respuesta falsa,
la abstención es apropiada porque se trata de información sensible que no debe
inferirse a partir de documentos no relacionados.

| Criterio | Valor |
|---|---|
| Corrección factual | No aplica |
| Cobertura | No aplica |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> La contraseña actual de la red inalámbrica no forma parte del corpus. La
> abstención es correcta y evita inventar información sensible.

## q037

### Pregunta

> ¿Cuál es el horario de atención de la Biblioteca José Figueres Ferrer esta
> semana?

### Análisis y decisión

El modificador «esta semana» exige información actualizada que no está
contenida en los reglamentos. La recuperación devolvió fragmentos sobre horas
de asistencia estudiantil, pero el modelo no confundió esas coincidencias
léxicas con el horario de una biblioteca.

| Criterio | Valor |
|---|---|
| Corrección factual | No aplica |
| Cobertura | No aplica |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> El horario de la biblioteca para la semana actual no forma parte del corpus.
> La abstención es correcta ante información operativa y cambiante.

## q038

### Pregunta

> ¿Cuál es el monto exacto que cuesta matricular un crédito de grado este
> semestre?

### Análisis y decisión

Los fragmentos recuperados describen reglas generales de pago y mencionan el
«valor ordinario del crédito vigente», pero no contienen el monto numérico del
semestre. El modelo distinguió correctamente entre una norma que indica cómo
se usa un precio y una fuente que realmente proporciona ese precio.

| Criterio | Valor |
|---|---|
| Corrección factual | No aplica |
| Cobertura | No aplica |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> El monto exacto por crédito del semestre actual no forma parte del corpus.
> La abstención es correcta y evita inventar un precio.

## q039

### Pregunta

> ¿Qué grupos y horarios tienen cupo disponible hoy para el curso de Cálculo
> Diferencial e Integral?

### Análisis y decisión

El corpus explica reglas de reserva y asignación de cupos, pero no contiene la
disponibilidad transaccional de grupos en el día de la consulta. La respuesta
correcta requiere consultar un sistema académico en tiempo real, no inferirla
de un reglamento.

| Criterio | Valor |
|---|---|
| Corrección factual | No aplica |
| Cobertura | No aplica |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> Los grupos, horarios y cupos disponibles hoy no forman parte del corpus. La
> abstención es correcta ante información transaccional en tiempo real.

## q040

### Pregunta

> ¿Cuál es el número de oficina y el horario de consulta del profesor que
> imparte Programación Orientada a Objetos este semestre?

### Análisis y decisión

La asignación docente, el número de oficina y el horario de consulta dependen
del semestre y no están en el corpus. Los fragmentos recuperados sobre oficinas
y horarios de estudiantes asistentes no permiten contestar la pregunta. El
modelo se abstuvo correctamente.

| Criterio | Valor |
|---|---|
| Corrección factual | No aplica |
| Cobertura | No aplica |
| Fidelidad a fuentes | No aplica |
| Claridad | Clara |
| Gold adecuado | Sí |
| Conclusión manual | Aprobada |

Nota registrada:

> El número de oficina y el horario de consulta del profesor actual no forman
> parte del corpus. La abstención es correcta ante información dependiente del
> semestre.

## Resumen después del cuarto bloque

| Indicador | Resultado |
|---|---:|
| Revisiones completas | 40 de 40 |
| Avance | 100.0% |
| Aprobadas | 28 |
| Para revisar | 3 |
| Rechazadas | 9 |
| Respuestas factualmente correctas | 26 |
| Respuestas factualmente parciales | 5 |
| Respuestas factualmente incorrectas | 2 |
| Casos factuales no aplicables | 7 |
| Tasa estricta de corrección | 78.8% |
| Puntaje factual ponderado | 86.4% |
| Fidelidad total | 93.5% |
| Cobertura completa | 72.7% |

En este bloque:

- `q031` y `q033` fueron rechazadas porque la recuperación solo cubrió una de
  las dos secciones necesarias;
- `q032` fue rechazada por una discrepancia entre las citas visibles y el campo
  estructurado, aunque su contenido era correcto;
- `q034-q040` fueron aprobadas porque el sistema se abstuvo correctamente ante
  información ausente.

## Lectura final de los resultados

### Resultados por tipo de pregunta

| Tipo | Preguntas | Revisadas | Aprobadas | Correctas | Parciales | Incorrectas |
|---|---:|---:|---:|---:|---:|---:|
| `direct` | 25 | 25 | 19 | 23 | 1 | 1 |
| `multi_section` | 8 | 8 | 2 | 3 | 4 | 1 |
| `unanswerable` | 7 | 7 | 7 | 0 | 0 | 0 |

El desglose muestra tres comportamientos distintos:

1. **Preguntas directas.** El sistema obtiene su mejor resultado. La mayoría de
   las respuestas son factualmente correctas y completas cuando la evidencia
   necesaria está concentrada en una sola sección.
2. **Preguntas de varias secciones.** Constituyen el principal punto débil.
   Solo dos de ocho fueron aprobadas. Los fallos aparecen cuando el recuperador
   encuentra una parte de la evidencia, pero no todos los artículos necesarios
   para componer la respuesta.
3. **Preguntas no respondibles.** Las siete fueron aprobadas. El sistema
   demostró una buena capacidad para abstenerse ante información actual,
   transaccional o sensible ausente del corpus.

### Diferencia entre corrección factual y aprobación

Existen 26 respuestas factualmente correctas, pero solo 28 conclusiones
aprobadas. Estos conteos no se comparan de forma directa porque las siete
abstenciones correctas tienen corrección factual `No aplica` y conclusión
`Aprobada`.

También hay respuestas con contenido correcto que fueron rechazadas:

- `q025` y `q032` incumplieron el contrato estructurado de citas.

Esto demuestra que la calidad de un sistema RAG no depende únicamente de que el
texto final «suene correcto». También importa que la salida sea válida,
trazable y consumible por el resto de la arquitectura.

### Principales modos de fallo observados

| Modo de fallo | Ejemplos | Descripción |
|---|---|---|
| Evidencia gold no recuperada | `q016`, `q017`, `q031`, `q033` | El artículo necesario no apareció entre los fragmentos entregados al modelo. |
| Fragmento incorrecto del artículo | `q029` | Se recuperó el `Record ID` relacionado, pero no el fragmento que contenía el dato. |
| Respuesta relacionada pero fuera del foco | `q017`, `q030` | El modelo usó evidencia verdadera, pero no respondió los elementos solicitados. |
| Inversión de regla y excepción | `q028` | La respuesta intercambió el máximo ordinario y el excepcional. |
| Contrato de citas inválido | `q025`, `q032` | Las citas del texto y del campo estructurado no coincidieron. |
| Omisión menor | `q005`, `q012`, `q021` | La respuesta principal fue correcta, pero faltó una categoría, condición o excepción. |

### Conclusión de la revisión

La evaluación humana indica que el prototipo es especialmente sólido en dos
situaciones: preguntas directas con evidencia localizada y preguntas
deliberadamente no respondibles. El reto principal aparece al combinar
información distribuida entre artículos o documentos.

Para el proyecto, esta observación es más útil que presentar únicamente un
porcentaje global. Permite relacionar los resultados con decisiones concretas
de arquitectura y observabilidad:

- registrar qué fragmentos se recuperaron;
- distinguir recuperación por documento de recuperación del fragmento exacto;
- validar la consistencia de las citas estructuradas;
- identificar preguntas que requieren evidencia de varias secciones;
- registrar abstenciones correctas e incorrectas por separado.
