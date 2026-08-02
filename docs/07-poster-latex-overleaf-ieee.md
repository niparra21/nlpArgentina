# Póster en LaTeX, Overleaf y estilo IEEE

## Objetivo de esta etapa

El póster se migró desde una maqueta editable en PowerPoint a un proyecto
LaTeX que puede abrirse y modificarse en Overleaf.

La nueva versión conserva:

- el título oficial;
- el formato A0 vertical solicitado por la Escuela;
- la arquitectura RAG como elemento central;
- los resultados de la evaluación automática y humana;
- la sesión 2 y el orden 12.

También incorpora convenciones académicas de IEEE:

- secciones numeradas;
- citas numéricas como `[1]`;
- referencias procesadas con `IEEEtran.bst`;
- redacción técnica y concisa;
- separación explícita entre metodología, resultados, interpretación,
  conclusión y trabajo futuro;
- tipografía de estilo Times.

## Por qué no se utilizó `IEEEtran` como clase

La clase `IEEEtran` está diseñada para artículos y actas de congreso en páginas
de tamaño carta o A4. No está diseñada para distribuir un póster A0 con
diagramas de gran formato.

La solución utilizada es:

```tex
\documentclass[final]{beamer}
\usepackage[orientation=portrait,size=a0,scale=1.0]{beamerposter}
```

`beamerposter` extiende Beamer para trabajar con formatos como A0 y A1. La guía
oficial de Overleaf presenta `beamerposter` y `tikzposter` como las dos opciones
principales para pósteres científicos:

<https://www.overleaf.com/learn/latex/Posters>

La decisión consiste en usar:

- `beamerposter` para el tamaño físico y la distribución;
- `IEEEtran.bst` para las referencias;
- convenciones IEEE para organizar el contenido.

Esto evita confundir **formato de página** con **estilo académico**.

## Árbol de archivos

```text
poster/
└── overleaf-ieee/
    ├── figures/
    │   ├── figura-a-indexacion-corpus.png
    │   └── figura-b-consulta-observable.png
    ├── main.tex
    ├── references.bib
    ├── README.md
    └── .gitignore
```

### `main.tex`

Es el documento principal. Está dividido mediante comentarios numerados:

1. formato general;
2. paleta y tipografía;
3. comandos reutilizables;
4. datos del póster;
5. encabezado;
6. cuerpo en dos columnas y figuras;
8. referencias IEEE y pie.

Los comentarios que comienzan con `%` explican el código, pero no aparecen en
el PDF.

### `references.bib`

Contiene las fuentes bibliográficas en formato BibTeX:

- artículo original de RAG;
- reporte técnico de Multilingual E5;
- fuente institucional del corpus.

La combinación:

```tex
\bibliographystyle{IEEEtran}
\bibliography{references}
```

ordena y presenta las referencias con estilo IEEE. Las citas se insertan en el
texto con:

```tex
\cite{lewis2020rag}
```

La guía oficial de referencias de IEEE explica el uso de números consecutivos:

<https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf>

### `figures/`

Contiene las dos ilustraciones exportadas desde Canva:

- `figura-a-indexacion-corpus.png`: procesamiento e indexación del corpus;
- `figura-b-consulta-observable.png`: consulta, generación, validación y
  registro de la traza.

La separación entre LaTeX e ilustraciones permite volver a editar el contenido
visual en Canva y sustituir únicamente la exportación. `main.tex` utiliza
rutas relativas, por lo que Overleaf encuentra las imágenes siempre que la
carpeta `figures` esté dentro del proyecto.

### `README.md`

Explica cómo cargar el proyecto en Overleaf, seleccionar el compilador y
encontrar cada parte editable.

### `.gitignore`

Evita que Git registre archivos auxiliares generados por LaTeX, por ejemplo:

```text
*.aux
*.log
*.bbl
*.blg
```

Estos archivos se regeneran al compilar y no forman parte del contenido fuente.

## Paquetes principales

### `beamerposter`

Define el tamaño A0 y la orientación vertical.

### `tikz`

Dibuja el gráfico de aprobación como vector. Un vector no depende de una
resolución fija, por lo que mantiene bordes nítidos al imprimir. Los diagramas
arquitectónicos se incorporan con `graphicx` porque proceden de Canva.

### `newtxtext` y `newtxmath`

Proporcionan una familia tipográfica similar a Times, compatible con el estilo
editorial habitual de IEEE.

### `cite`

Gestiona citas numéricas y agrupación de referencias.

### `babel`

Configura reglas de escritura y separación silábica para español.

## Adaptación visual del artículo IEEE de referencia

Nicole proporcionó como referencia visual el artículo:

> *Mütüä: An Easy-Access and Adaptable Retrieval Augmented Generation LLM
> Scientific Platform for Resource-Efficient HPC Infrastructures*

El PDF se estudió por su forma, no por su contenido. Se revisaron la portada,
una página de desarrollo, una página con arquitectura y la página de
referencias.

Las características observadas fueron:

- página tamaño carta;
- dos columnas de texto;
- familia tipográfica Nimbus Roman, equivalente visual a Times;
- cuerpo principal de 10 puntos;
- separación vertical aproximada de 11,1 puntos entre líneas de texto;
- título principal centrado y sin una negrita pesada;
- nombres de autores centrados;
- afiliaciones en cursiva;
- títulos principales centrados, numerados con romanos y en versalitas;
- subtítulos en cursiva;
- texto justificado;
- fondo blanco y texto negro;
- figuras en blanco y negro con pie inferior;
- uso mínimo de elementos decorativos.

Estas reglas no se copiaron literalmente porque el póster debe leerse a mayor
distancia. Se trasladaron proporcionalmente a A0:

- cuerpo de 31 puntos con interlineado de 35 puntos;
- títulos de sección de 35 puntos con interlineado de 39 puntos;
- título principal de 74 puntos con interlineado de 80 puntos;
- familia `newtxtext`, similar a Times;
- dos columnas equilibradas de 48,5 % del ancho;
- secciones centradas y numeradas;
- resumen, objetivo y palabras clave con etiquetas en negrita cursiva;
- dos diagramas en blanco y negro con los rótulos `Fig. 1` y `Fig. 2`;
- referencias y vínculos en negro;
- eliminación de las franjas, tarjetas y fondos de color.

La razón de conservar dos columnas es doble: reproduce la lógica editorial del
artículo y utiliza mejor la altura del A0 que la versión anterior de tres
columnas. El interlineado mantiene una proporción cercana a la del artículo:

```text
Artículo: 10 / 11,1 ≈ 1,11
Póster:   31 / 35   ≈ 1,13
```

La relación es similar, pero el tamaño absoluto del póster es mucho mayor.

## Cómo está construido el póster

### Encabezado

El encabezado contiene:

- evento y año;
- título oficial;
- autora;
- indicación de trabajo independiente;
- caso de estudio;
- caso de estudio.

### Arquitectura

La arquitectura se separa en dos figuras para distinguir dos momentos que no
ocurren al mismo tiempo.

La figura A representa el procesamiento fuera de línea:

```text
25 documentos -> 1 184 secciones -> fragmentación
              -> embeddings normalizados -> 1 259 fragmentos indexados
```

La figura B representa la ejecución de una consulta:

```text
pregunta -> embedding -> búsqueda top-5 -> contexto
         -> generación local -> validación -> respuesta
```

En paralelo, el orquestador registra:

```text
pregunta -> fragmentos -> contexto -> respuesta
         -> estado -> citas -> tiempos
```

### Dos columnas

Cada columna comienza con una figura y su pie. Esta ubicación reproduce la
práctica del artículo de referencia: la imagen aparece antes del texto que la
explica y puede citarse como `Fig. 1` o `Fig. 2`.

La primera columna presenta introducción, corpus, diseño, protocolo de
evaluación y definición de la traza observable.

La segunda presenta resultados, interpretación de métricas, discusión,
limitaciones, conclusión y repositorio.

### Tabla de resultados

La `Tabla I` reúne las mediciones que antes aparecían repartidas entre cifras
grandes y párrafos. Utiliza tres columnas:

```text
Indicador | Casos | Resultado
```

La columna `Casos` conserva el numerador y el denominador. Esto permite
distinguir, por ejemplo:

```text
31/33 = 93,9 % de preguntas respondibles con evidencia en top-5
35/40 = 87,5 % de decisiones de estado correctas
7/7   = 100 % de abstenciones correctas
```

La tabla se divide en tres grupos:

1. evaluación automática: validez estructural, estado, recuperación y citas;
2. revisión humana: corrección, puntaje ponderado, fidelidad, cobertura y
   aprobación;
3. latencia: búsqueda, generación y tiempo total.

Los denominadores no se mezclan. Recuperación y citas utilizan las 33 preguntas
respondibles; la revisión factual y de cobertura también excluye las siete
preguntas donde la corrección factual no aplica. La fidelidad utiliza 31
respuestas con afirmaciones evaluables. La latencia de generación se calcula
sobre las 37 salidas generadas; la recuperación y el tiempo total consideran
las 40 consultas.

La tabla sigue la composición de IEEE: título superior, ausencia de líneas
verticales y reglas horizontales de `booktabs`.

Las cifras se verificaron contra:

```text
results/rag-evaluation/2026-07-28/
qwen3.5-9b-normalized-citations/summary.json

outputs/rag-manual-review-20260728/
revision_manual_rag_completada.xlsx

docs/05-bitacora-revision-manual.md
```

### Gráfico

El gráfico no es una imagen PNG. Se construye con rectángulos y texto TikZ:

- directas: 76 %;
- varias secciones: 25 %;
- no respondibles: 100 %.

Esto permite modificar cifras y colores desde `main.tex`.

## Compilación local realizada

La computadora no tenía una distribución LaTeX instalada. Para validar el
proyecto se utilizó Tectonic 0.17.0 como compilador portátil.

El ejecutable se descargó desde el repositorio oficial:

<https://github.com/tectonic-typesetting/tectonic>

Se verificó el SHA-256 del archivo descargado:

```text
F61CE51F0B0ADE1015B7DE7EF368541C5424E9756ECBD0D7AF97D6D48030845F
```

El comando equivalente utilizado para compilar fue:

```powershell
tectonic.exe main.tex --outdir tmp\poster-latex-build `
  --keep-logs --keep-intermediates
```

Tectonic ejecutó automáticamente:

1. LaTeX;
2. BibTeX;
3. las recompilaciones necesarias para resolver las citas;
4. la generación del PDF.

## Correcciones realizadas durante la revisión

### Primera compilación

El gráfico ocupaba más ancho que su columna y las referencias no aparecían.

Se corrigió:

- el ancho horizontal del gráfico;
- la posición de la etiqueta de 100 %;
- la inclusión de citas dentro del texto.

### Segunda compilación

El texto era más legible, pero un estiramiento vertical desplazó el encabezado
fuera del lienzo.

Se eliminó el estiramiento.

### Tercera compilación

Se probó una franja adicional de diagnóstico. El contenido excedió la altura
segura de una sola página y Beamer recortó elementos.

La franja se retiró porque repetía hallazgos que ya estaban presentes.

### Versión estable

La versión estable:

- conserva todo el encabezado;
- mantiene la arquitectura completa;
- no invade columnas vecinas;
- muestra las tres referencias;
- no contiene cajas `Overfull`;
- no tiene citas indefinidas.

### Revisión estética basada en el artículo

Se sustituyó la primera estética del póster, que utilizaba bloques de color,
por una composición editorial:

1. se convirtió la paleta a blanco y negro;
2. se eliminaron los encabezados de sección con fondo;
3. se cambió de tres a dos columnas;
4. se ajustó el cuerpo a 31/35 puntos;
5. se centraron los títulos con numeración romana;
6. se añadieron pies descriptivos a las dos figuras;
7. se eliminaron los colores de citas, enlaces y listas;
8. se aumentó el título a 74/80 puntos;
9. se corrigió la sangría accidental de la regla del encabezado.

Después de estos cambios, la compilación no reportó cajas `Overfull` ni citas
indefinidas. Los dos avisos `Underfull` aparecen al cerrar el marco de Beamer y
no corresponden a texto visible mal compuesto.

### Reorganización para incorporar las dos figuras

La arquitectura inicial ocupaba una sola franja construida directamente en
LaTeX. Después de completar los diagramas editables en Canva se reorganizó la
página:

1. la figura de indexación se colocó al inicio de la columna izquierda;
2. la figura de consulta observable se colocó al inicio de la columna derecha;
3. cada figura recibió un pie descriptivo breve;
4. el resumen y la contribución se integraron en la introducción;
5. el método se redactó como prosa técnica, no como una lista de componentes;
6. la observabilidad recibió una sección propia;
7. resultados, discusión, limitaciones y conclusión se mantuvieron separados.

La redacción se revisó siguiendo el estilo del artículo de referencia:

- afirmaciones directas y verificables;
- párrafos justificados y compactos;
- términos técnicos definidos cuando aparecen por primera vez;
- separación entre lo implementado, lo medido y lo interpretado;
- cifras acompañadas de su significado;
- limitaciones expresadas de forma explícita;
- pies de figura que explican el flujo sin repetir todos los rótulos internos.

La reorganización no cambia las cifras del experimento. Su propósito es
presentar con mayor claridad la relación entre la arquitectura implementada,
la traza observable y los resultados de evaluación.

## Ajuste de legibilidad para impresión A0

Se revisaron los tamaños tipográficos utilizando como referencia indicaciones
oficiales de congresos IEEE para pósteres. Estas guías coinciden en que el
texto de lectura no debe bajar de 18 puntos y recomiendan títulos y encabezados
considerablemente mayores:

- IEEE-CYBER recomienda al menos 70 puntos para el título y 18 puntos para el
  texto:
  <https://ewh.ieee.org/soc/ras/conf/financiallycosponsored/cyber/2017/ieee-cyber.org/2017/indexd74f.html?page_id=196>
- IEEE IVEC indica al menos 30 puntos para encabezados y 18 puntos para texto:
  <https://www.ewh.ieee.org/conf/ivec/2020/assets/2020-Poster-Presentation-Instructions.pdf>
- IEEE NSS/MIC advierte que el texto menor de 18 puntos es difícil de leer y
  propone entre 24 y 40 puntos para elementos destacados:
  <https://ewh.ieee.org/soc/nps/nss-mic/2016/presentationguidelines.php.html>

La jerarquía final controlada desde `main.tex` es:

| Elemento | Tamaño final |
|---|---:|
| Título principal | 74 pt |
| Nombre de la autora | 29 pt |
| Encabezados de sección | 35 pt |
| Texto principal | 31 pt |
| Contenido de la tabla | 21 pt |
| Pies de figura | 20 pt |
| Nota de la tabla | 20 pt |
| Bibliografía | 18 pt |
| Aviso inferior | 18 pt |

Los pies de figura aumentaron de 18 a 20 puntos, la nota de la tabla de 18 a
20 puntos, la bibliografía de 16 a 18 puntos y el aviso inferior de 15 a 18
puntos. El texto principal y los encabezados se conservaron porque ya cumplían
holgadamente las recomendaciones. Para compensar el aumento sin reducir
tipografías se retiraron 0,15 cm de espacio vacío antes del pie inferior.

Los rótulos incluidos dentro de los dos PNG no se modifican desde LaTeX. Se
corrigen en Canva y luego se reemplazan las imágenes dentro de `figures`,
conservando sus nombres.

## Márgenes y equilibrio de columnas

La primera versión utilizaba los márgenes predeterminados de Beamer. La
medición del PDF mostraba aproximadamente 9,7 mm a la izquierda, 8,2 mm a la
derecha, 1 mm arriba y 1,6 mm abajo. Aunque el contenido no estaba cortado,
quedaba demasiado cerca de los límites físicos del papel.

La versión ajustada define explícitamente los márgenes laterales:

```tex
\setbeamersize{text margin left=2cm,text margin right=2cm}
```

También reserva 1,9 cm al inicio del `frame`. Ese espacio, sumado a la altura
real de las letras, deja cerca de 20 mm de margen superior. Los primeros 1,4 cm
se compensaron redistribuyendo los espacios internos del encabezado, sin
reducir el título ni las demás tipografías. Los 5 mm finales desplazan el
contenido completo hacia abajo y equilibran los márgenes superior e inferior.

El menor ancho disponible produjo nuevos saltos de línea y aumentó la altura de
la columna derecha. La primera compilación con márgenes generó un
desbordamiento vertical de 46,4 puntos. No se solucionó reduciendo la letra:
el bloque `Código, datos y documentación` se trasladó desde la columna derecha
al espacio libre de la columna izquierda. Así se equilibraron las columnas y
se conservó todo el contenido.

La medición final del área ocupada por texto es:

| Margen | Medición final aproximada |
|---|---:|
| Izquierdo | 19,7 mm |
| Derecho | 18,1 mm |
| Superior | 20,0 mm |
| Inferior | 26,4 mm |

La pequeña diferencia lateral se debe a la forma de algunos caracteres y a la
expansión tipográfica, no a que las cajas principales atraviesen el margen de
2 cm. El margen inferior conserva unos milímetros adicionales para mantener
las referencias, el aviso y el número de sesión lejos del borde de impresión.

## Validaciones del PDF

El PDF final reporta:

```text
Pages:     1
Page size: 2383.94 x 3370.39 pts (A0)
Page rot:  0
```

También se comprobó:

- todas las tipografías están incrustadas;
- el ZIP coloca `main.tex` en la raíz del proyecto;
- el ZIP contiene las dos figuras dentro de `figures`;
- las flechas avanzan de izquierda a derecha;
- no hay texto cortado ni superposiciones;
- las referencias `[1]`, `[2]` y `[3]` son visibles;
- el PDF final y el PDF compilado tienen el mismo contenido.

## Cómo abrirlo en Overleaf

1. Entrar a Overleaf.
2. Seleccionar **New Project**.
3. Seleccionar **Upload Project**.
4. Cargar:

   ```text
   outputs/poster-overleaf-20260730-margenes-ieee-final/
   poster-rag-observable-overleaf-margenes-ieee-final.zip
   ```

5. Abrir **Menu**.
6. Confirmar `main.tex` como documento principal.
7. Seleccionar **pdfLaTeX** como compilador.
8. Presionar **Recompile**.
9. Descargar el PDF.

## Qué archivo se entrega

El archivo para imprenta y para el formulario es:

```text
outputs/poster-overleaf-20260730-margenes-ieee-final/
poster-rag-observable-ieee-a0-margenes-ieee-final.pdf
```

El ZIP es para editar en Overleaf, no para la imprenta.

## Estado pendiente

Todavía se debe:

1. revisar el PDF completo con Nicole;
2. si es posible, reemplazar los PNG de Canva por exportaciones PDF o PNG de
   mayor resolución para la impresión A0;
3. comprobar el límite y tipo de archivo permitido por el formulario;
4. subir el PDF antes del 30 de julio;
5. confirmar que la carga terminó correctamente.

No se ha enviado automáticamente ningún archivo.
