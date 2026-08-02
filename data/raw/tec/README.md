# Corpus de normativa estudiantil del TEC

Esta carpeta conserva capturas reproducibles de normativa publicada por el
Tecnológico de Costa Rica. El corpus se utilizará para desarrollar y evaluar un
sistema RAG mínimo y observable.

## Alcance

La captura `2026-07-23` contiene 25 documentos oficiales relacionados con:

- enseñanza, admisión, aptitud académica, graduación, trabajos finales,
  equiparación de asignaturas y reconocimiento de títulos;
- becas de posgrado, horas estudiante, asistencias, fondos solidarios y
  movilidad, además de becas y préstamos estudiantiles;
- residencias, defensoría, convivencia, correo institucional, hostigamiento y
  discriminación;
- elecciones, asambleas y representación estudiantil.

El inventario exacto, las URL y las huellas de los 25 archivos están en
`2026-07-23/manifest.csv`.

Las páginas oficiales publican el contenido normativo como HTML; por eso se
conserva la respuesta HTML original, sin convertirla ni alterar su contenido.
`manifest.csv` registra el origen, versión conocida, fecha de recuperación,
tamaño y SHA-256 de cada archivo.

## Reglas de recolección

- Solo se aceptan páginas HTTPS bajo el dominio oficial `tec.ac.cr`.
- Se conserva la URL canónica y la URL final después de redirecciones.
- La página debe contener el título y los marcadores esperados del reglamento.
- Se rechazan páginas marcadas como `Reglamento derogado` o con vigencia
  finalizada el 31 de diciembre de 2024.
- Cada captura queda en una carpeta fechada. El recolector se niega a
  sobrescribir una captura existente.
- No se incluyen preguntas frecuentes, cápsulas estudiantiles, noticias,
  calendarios ni versiones derogadas dentro del corpus recuperable.
- Las fechas de vigencia y modificación provienen de los metadatos o del texto
  publicado en las páginas oficiales.
- Cada captura queda identificada por su fecha y nunca se sobrescribe.

Dos páginas antiguas fueron excluidas expresamente:

- La versión del Reglamento de Enseñanza-Aprendizaje vigente hasta el 31 de
  diciembre de 2024.
- El antiguo Reglamento del Sistema de Alojamiento y Residencias Estudiantiles,
  cuya página oficial lo identifica como derogado.

## Crear una captura nueva

Desde la raíz del repositorio:

```powershell
python scripts/collect_tec_regulations.py `
  --snapshot-date YYYY-MM-DD
```

El recolector falla si una URL deja el dominio oficial, el servidor no devuelve
HTML, faltan marcadores esperados o la página parece corresponder a una versión
derogada.

## Uso responsable

Estas copias son evidencia del contenido disponible en la fecha de captura y se
mantienen para reproducibilidad académica. No constituyen asesoría ni un canal
oficial del TEC. Antes de tomar decisiones se debe verificar la normativa vigente
en el sitio institucional.
