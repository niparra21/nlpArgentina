# Póster A0 en LaTeX para Overleaf

Este directorio contiene la versión editable en LaTeX del póster:

> Diseño arquitectónico mínimo para sistemas RAG observables en español
> latinoamericano

El documento conserva el requisito de la Escuela: **A0 vertical**.

## Por qué no se utiliza `IEEEtran` como clase

`IEEEtran` está diseñado para artículos y actas en páginas de tamaño carta o
A4. Forzarlo a A0 produciría un documento difícil de mantener y no aprovecharía
las herramientas específicas para pósteres.

Se utiliza `beamerposter`, recomendado para pósteres científicos de gran
formato. Las convenciones IEEE se aplican en:

- organización numerada de las secciones;
- redacción técnica y concisa;
- separación entre método, resultados, discusión y conclusión;
- citas numéricas;
- bibliografía con `IEEEtran.bst`;
- tipografía de estilo Times;
- figuras y gráficos vectoriales;
- composición editorial en blanco y negro;
- cuerpo en dos columnas;
- títulos de sección centrados y numerados;
- texto justificado con interlineado compacto;
- figuras superiores con pies explicativos al estilo de un artículo técnico.

La referencia visual utilizada fue el artículo *Mütüä: An Easy-Access and
Adaptable Retrieval Augmented Generation LLM Scientific Platform for
Resource-Efficient HPC Infrastructures*. Se imita su lenguaje tipográfico y
editorial, no su contenido.

## Archivos

### `main.tex`

Es el documento principal. Contiene:

1. tamaño A0 y orientación;
2. paquetes de LaTeX;
3. colores y tipografía;
4. comandos reutilizables para métricas y hallazgos;
5. encabezado;
6. cuerpo de dos columnas;
7. figuras de indexación y consulta;
8. tabla y gráfico vectorial de resultados;
9. referencias y pie.

### `figures/figura-a-indexacion-corpus.png`

Representa el procesamiento previo a las consultas:

```text
documentos -> secciones -> fragmentación -> embeddings -> índice local
```

### `figures/figura-b-consulta-observable.png`

Representa la ejecución de una consulta:

```text
usuario -> orquestador -> recuperación -> LLM -> validación -> respuesta
                         \-> traza observable
```

Las dos figuras se mantienen como archivos separados para que puedan
reemplazarse con nuevas exportaciones de Canva sin modificar el código LaTeX.
Los nombres deben conservarse.

### `references.bib`

Contiene las referencias bibliográficas. La línea:

```tex
\bibliographystyle{IEEEtran}
```

indica que BibTeX debe presentarlas con el estilo IEEE.

## Cómo subirlo a Overleaf

1. Comprimir la carpeta `overleaf-ieee` como un archivo ZIP.
2. Entrar a Overleaf.
3. Seleccionar **New Project**.
4. Seleccionar **Upload Project**.
5. Cargar el ZIP.
6. Confirmar que `main.tex` sea el documento principal.
7. En **Menu > Compiler**, seleccionar **pdfLaTeX**.
8. Presionar **Recompile**.
9. Descargar el PDF desde **Download PDF**.

El ZIP debe incluir la carpeta `figures`. La tabla y el gráfico de evaluación
se generan directamente en LaTeX, pero los dos diagramas arquitectónicos se
cargan desde esa carpeta.

## Dónde cambiar el contenido

- Título, autora y evento: sección `4. DATOS DEL POSTER`.
- Encabezado visible: sección `5. ENCABEZADO`.
- Figuras y contenido académico: sección
  `6. CUERPO EN DOS COLUMNAS Y FIGURAS DE ARQUITECTURA`.
- Referencias: archivo `references.bib`.
- Colores: sección `2. PALETA Y TIPOGRAFIA`.

Para actualizar un diagrama, se exporta nuevamente desde Canva y se reemplaza
el archivo correspondiente dentro de `figures`. `main.tex` omite la extensión,
por lo que puede utilizar un PNG o un PDF con el mismo nombre base. Para
impresión A0 se prefiere PDF vectorial o, como segunda opción, PNG de alta
resolución.

## Comprobaciones antes de entregar

- una sola página;
- tamaño A0, 841 × 1189 mm;
- orientación vertical;
- márgenes laterales de 20 mm;
- margen superior de 20 mm;
- margen inferior aproximado de 26 mm;
- título de 74 pt;
- encabezados de sección de 35 pt;
- texto principal de 31 pt;
- pies de figura y nota de tabla de 20 pt;
- bibliografía y aviso inferior de 18 pt;
- las dos figuras están incluidas;
- ningún texto cortado;
- no hay textos superpuestos;
- los rótulos de las figuras pueden leerse a distancia de exposición;
- referencias visibles;
- cifras iguales a los resultados finales;
- PDF aceptado por el formulario;
- archivo cargado antes del 30 de julio de 2026.
