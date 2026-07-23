# nlpArgentina

Prototipo académico de una arquitectura RAG mínima y observable sobre normativa
estudiantil del Tecnológico de Costa Rica.

## Corpus

La primera captura reproducible contiene cinco reglamentos oficiales del TEC,
junto con su procedencia, fecha de consulta y suma de verificación. Una segunda
capa derivada organiza el contenido por artículos y transitorios.

- [Metodología de recolección](data/raw/tec/README.md)
- [Captura del 23 de julio de 2026](data/raw/tec/2026-07-23/)
- [Corpus procesado por secciones](data/processed/tec/README.md)

## Reproducir

```powershell
python -m pip install -r requirements.txt
python scripts/process_tec_regulations.py --snapshot-date 2026-07-23
python -m unittest discover -s tests
```

La información almacenada se utiliza únicamente con fines de investigación. Para
tomar decisiones académicas o administrativas se debe consultar siempre la fuente
oficial del TEC.
