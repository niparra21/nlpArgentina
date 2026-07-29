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
- texto justificado con interlineado compacto.

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
6. arquitectura RAG dibujada con TikZ;
7. cuerpo de dos columnas;
8. gráfico vectorial de resultados;
9. referencias y pie.

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

No se necesitan imágenes externas: el diagrama y el gráfico se crean dentro de
LaTeX. Esto reduce la posibilidad de que Overleaf reporte archivos faltantes.

## Dónde cambiar el contenido

- Título, autora y evento: sección `4. DATOS DEL POSTER`.
- Encabezado visible: sección `5. ENCABEZADO`.
- Pipeline RAG: sección `6. ARQUITECTURA CENTRAL`.
- Contenido académico: sección `7. CUERPO EN DOS COLUMNAS`.
- Referencias: archivo `references.bib`.
- Colores: sección `2. PALETA Y TIPOGRAFIA`.

## Comprobaciones antes de entregar

- una sola página;
- tamaño A0, 841 × 1189 mm;
- orientación vertical;
- ningún texto cortado;
- flechas del pipeline de izquierda a derecha;
- referencias visibles;
- cifras iguales a los resultados finales;
- PDF aceptado por el formulario;
- archivo cargado antes del 30 de julio de 2026.
