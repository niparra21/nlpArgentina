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
6. arquitectura central;
7. cuerpo en dos columnas;
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

Dibuja el pipeline RAG y el gráfico de aprobación como vectores. Un vector no
depende de una resolución fija, por lo que mantiene bordes nítidos al imprimir.

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
- diagrama central en blanco y negro con el rótulo `Fig. 1`;
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

El pipeline se dibuja con siete nodos TikZ:

```text
Fuentes -> Secciones -> Índice -> Recuperación
        -> Generación -> Validación -> Salida
```

Cada nodo muestra el artefacto o decisión más importante de esa etapa.

Debajo aparece la traza observable:

```text
pregunta -> fragmentos -> contexto -> respuesta
         -> estado -> citas -> tiempos
```

### Dos columnas

La primera columna explica el problema, corpus, método, evaluación humana y
resultados principales.

La segunda presenta rendimiento, interpretación de métricas, hallazgos,
conclusión, limitaciones y repositorio.

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
- no contiene cajas `Overfull` ni `Underfull`;
- no tiene citas indefinidas.

### Revisión estética basada en el artículo

Se sustituyó la primera estética del póster, que utilizaba bloques de color,
por una composición editorial:

1. se convirtió la paleta a blanco y negro;
2. se eliminaron los encabezados de sección con fondo;
3. se cambió de tres a dos columnas;
4. se ajustó el cuerpo a 31/35 puntos;
5. se centraron los títulos con numeración romana;
6. se añadió un pie de figura al pipeline;
7. se eliminaron los colores de citas, enlaces y listas;
8. se aumentó el título a 74/80 puntos;
9. se corrigió la sangría accidental de la regla del encabezado.

Después de estos cambios, la compilación no reportó cajas `Overfull`,
`Underfull` ni citas indefinidas.

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
- las flechas avanzan de izquierda a derecha;
- no hay texto cortado ni superposiciones;
- las referencias `[1]`, `[2]` y `[3]` son visibles;
- el PDF final y el PDF compilado tienen el mismo SHA-256.

## Cómo abrirlo en Overleaf

1. Entrar a Overleaf.
2. Seleccionar **New Project**.
3. Seleccionar **Upload Project**.
4. Cargar:

   ```text
   outputs/poster-overleaf-20260729/
   poster-rag-observable-overleaf-source.zip
   ```

5. Abrir **Menu**.
6. Confirmar `main.tex` como documento principal.
7. Seleccionar **pdfLaTeX** como compilador.
8. Presionar **Recompile**.
9. Descargar el PDF.

## Qué archivo se entrega

El archivo para imprenta y para el formulario es:

```text
outputs/poster-overleaf-20260729/
poster-rag-observable-ieee-a0.pdf
```

El ZIP es para editar en Overleaf, no para la imprenta.

## Estado pendiente

Todavía se debe:

1. revisar el contenido visual con Nicole;
2. comprobar el límite y tipo de archivo permitido por el formulario;
3. subir el PDF antes del 30 de julio;
4. confirmar que la carga terminó correctamente.

No se ha enviado automáticamente ningún archivo.
