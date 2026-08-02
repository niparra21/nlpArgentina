# Modelo generativo local con Ollama

Fecha de la instalación y prueba: **27 de julio de 2026**.

> Nota de seguimiento: el 28 de julio el actualizador de Ollama ya había
> aplicado la versión `0.32.5`. La versión `0.32.4` indicada en esta guía
> corresponde al momento exacto de la instalación inicial.

Esta guía documenta la incorporación del modelo generativo local. Al terminar
esta etapa todavía no existe el RAG completo: ya existe el recuperador semántico
y ahora también existe un generador comprobado, pero el siguiente paso será
conectar ambas piezas.

## 1. Qué problema resuelve esta etapa

El sistema ya podía convertir una pregunta en un vector y encontrar los cinco
fragmentos normativos más cercanos. Sin embargo, recuperar fragmentos no es lo
mismo que redactar una respuesta.

El modelo generativo recibirá posteriormente:

```text
pregunta
   ↓
cinco fragmentos recuperados
   ↓
instrucciones para usar solamente esos fragmentos
   ↓
respuesta con citas o abstención
```

El objetivo de esta etapa fue comprobar por separado que el modelo puede:

1. ejecutarse completamente en la computadora local;
2. seguir instrucciones en español;
3. responder usando un contexto suministrado;
4. incluir un identificador de evidencia;
5. abstenerse cuando el contexto no contiene la respuesta;
6. devolver métricas básicas de tiempo y cantidad de tokens.

Probar esta capa de forma aislada evita atribuirle al recuperador un error que en
realidad provenga del prompt o del generador.

## 2. Dos modelos diferentes dentro del proyecto

Es importante no confundir los dos modelos:

| Función | Modelo | Qué produce |
|---|---|---|
| Recuperación | `intfloat/multilingual-e5-small` | Un vector de 384 números |
| Generación | `qwen3.5:9b` | Una respuesta redactada en español |

`multilingual-e5-small` no responde preguntas. Convierte cada fragmento y cada
consulta en vectores comparables. `qwen3.5:9b` no reemplaza esos embeddings:
recibe el texto que el primer modelo ayudó a recuperar y redacta la respuesta.

Por esa razón no se reconstruyó el índice existente. Sus 1,259 fragmentos y sus
embeddings siguen siendo válidos.

## 3. Equipo experimental detectado

La plataforma principal del experimento es:

| Componente | Valor observado |
|---|---|
| Sistema | Windows |
| CPU | AMD Ryzen 7 5700X3D, 8 núcleos y 16 hilos |
| RAM | 15.9 GB |
| GPU | NVIDIA GeForce RTX 3060 |
| VRAM | 12,288 MiB |
| Controlador NVIDIA | 580.88 |
| CUDA anunciada por el controlador | 13.0 |

Antes de instalar el modelo había aproximadamente 10,450 MiB de VRAM libres.
La VRAM es la memoria propia de la tarjeta gráfica. Mantener los pesos y el
contexto en esa memoria evita transferencias constantes entre CPU y GPU.

El comando de diagnóstico utilizado fue:

```powershell
nvidia-smi `
  --query-gpu=name,memory.total,memory.free,driver_version `
  --format=csv,noheader
```

`nvidia-smi` es una utilidad incluida con el controlador de NVIDIA. No modifica
nada: solamente informa el estado de la GPU.

## 4. Software y modelo seleccionados

Se utilizó Ollama como servidor local de modelos y Qwen 3.5 9B como generador.

| Elemento | Valor comprobado |
|---|---|
| Ollama | `0.32.4` |
| Etiqueta del modelo | `qwen3.5:9b` |
| Digest completo | `6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7` |
| Familia | `qwen35` |
| Parámetros informados | `9.7B` |
| Cuantización | `Q4_K_M` |
| Tamaño descargado | 6,594,474,711 bytes, aproximadamente 6.6 GB |
| Contexto máximo anunciado | 262,144 tokens |
| Contexto elegido para el proyecto | 8,192 tokens |

### Qué significa `Q4_K_M`

La cuantización representa los pesos del modelo con menos bits. Esto reduce el
espacio en disco y la memoria necesaria para ejecutarlo. `Q4_K_M` es una
cuantización de aproximadamente cuatro bits con un esquema que conserva más
precisión en partes importantes del modelo.

No significa que el modelo tenga cuatro mil millones de parámetros. El modelo
sigue teniendo aproximadamente 9.7 mil millones; lo que cambia es la cantidad
de memoria utilizada para guardar cada peso.

### Por qué no se usa el contexto máximo

Que un modelo anuncie 262,144 tokens no significa que debamos reservarlos. La
memoria utilizada por el contexto crece con su longitud. Para una pregunta y
cinco fragmentos normativos, 8,192 tokens proporcionan un margen razonable y
caben completamente en la RTX 3060.

## 5. Instalación de Ollama

Primero se comprobó que Ollama no estuviera instalado:

```powershell
Get-Command ollama -ErrorAction SilentlyContinue
winget list --id Ollama.Ollama --exact
```

Después se instaló desde el catálogo de `winget`:

```powershell
winget install `
  --id Ollama.Ollama `
  --exact `
  --accept-package-agreements `
  --accept-source-agreements `
  --silent
```

Significado de cada parte:

- `winget install`: solicita al administrador de paquetes de Windows una
  instalación.
- `--id Ollama.Ollama`: identifica el paquete sin depender de una búsqueda por
  nombre.
- `--exact`: evita instalar otro paquete con un nombre parecido.
- `--accept-package-agreements`: acepta los términos del paquete.
- `--accept-source-agreements`: acepta los términos del catálogo.
- `--silent`: utiliza el instalador sin ventanas interactivas.

La descarga del instalador fue grande, por lo que el primer comando superó el
tiempo de espera de la terminal. El proceso de `winget` continuó correctamente
en segundo plano. No se inició otra instalación; se esperó hasta que
`OllamaSetup.exe` terminara.

La instalación se comprobó con:

```powershell
winget list --id Ollama.Ollama --exact
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
```

El uso de la ruta completa fue necesario porque una terminal abierta antes de la
instalación todavía no había actualizado su variable `PATH`. En una terminal
nueva normalmente basta con:

```powershell
ollama --version
```

## 6. El servicio local

Ollama inicia un proceso que escucha solamente en la computadora:

```text
http://127.0.0.1:11434
```

Se comprobó con:

```powershell
Invoke-RestMethod `
  -Uri "http://localhost:11434/api/version" `
  -TimeoutSec 10
```

La respuesta fue:

```json
{"version":"0.32.4"}
```

Esto demuestra tres cosas:

1. el programa fue instalado;
2. el servidor está iniciado;
3. otros programas locales, como nuestro código Python, pueden comunicarse con
   él.

No es una API alojada en internet. Los prompts y fragmentos enviados a esa
dirección permanecen en la computadora.

## 7. Descarga del modelo

El comando ejecutado fue:

```powershell
ollama pull qwen3.5:9b
```

En la terminal original se utilizó la ruta completa equivalente:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" pull qwen3.5:9b
```

`pull` descarga las capas del modelo, comprueba su SHA-256 y registra un
manifiesto local. La descarga principal fue de aproximadamente 6.6 GB.

Los archivos se guardaron bajo:

```text
C:\Users\nicop\.ollama\models\
```

No se guardan dentro del repositorio y no se suben a GitHub. Git conserva el
código y la configuración necesaria para volver a descargar el modelo, no una
copia de sus pesos.

La instalación del modelo se verificó con:

```powershell
ollama list
```

El resultado relevante fue:

```text
NAME          ID              SIZE
qwen3.5:9b    6488c96fa5fa    6.6 GB
```

El identificador permite detectar en el futuro si una etiqueta apunta a una
versión diferente.

## 8. Configuración inicial

Las solicitudes de prueba utilizaron:

```text
num_ctx       = 8192
temperature   = 0.1
seed          = 42
num_predict   = 128
think         = false
keep_alive    = 5m
```

Significado:

- `num_ctx`: cantidad máxima de tokens disponibles para instrucciones,
  fragmentos, pregunta y respuesta.
- `temperature`: controla variación. Un valor bajo favorece respuestas
  consistentes.
- `seed`: fija la semilla aleatoria para mejorar reproducibilidad.
- `num_predict`: limita la longitud de la respuesta generada.
- `think = false`: utiliza respuesta directa, con menor latencia y sin incluir
  un proceso de razonamiento innecesario.
- `keep_alive`: conserva el modelo cargado cinco minutos después de responder.

## 9. Prueba controlada y aprendizaje del primer fallo

El primer contexto artificial decía:

```text
[F1] El Laboratorio Aurora abre de lunes a viernes de 8:00 a 16:00.
No abre los fines de semana.
```

La primera pregunta fue si el laboratorio abría el domingo. El prompt inicial
indicaba que debía responder “no encontrado” cuando la respuesta no estuviera en
el contexto. El resultado fue:

```text
No encontrado.
```

El modelo buscó una mención suficientemente literal de “domingo” y no aplicó la
relación entre domingo y fin de semana. Este resultado no se descartó: mostró
que la redacción del prompt define el criterio de uso de evidencia.

El prompt se precisó para permitir conclusiones directas inequívocamente
respaldadas y exigir una forma exacta de abstención. Después se probaron:

1. una pregunta literal sobre el horario, que debía incluir `[F1]`;
2. una pregunta sobre un teléfono que no aparecía en el contexto.

Resultados con el modelo ya cargado:

| Caso | Resultado | Tiempo total | Velocidad |
|---|---|---:|---:|
| Evidencia literal | Horario correcto y cita `[F1]` | 1.30 s | 52.87 tokens/s |
| Sin evidencia | `No encontrado en el contexto.` | 0.74 s | 55.04 tokens/s |

Ambos casos superaron sus comprobaciones.

## 10. Carga fría y carga caliente

La primera solicitud tardó 212.68 segundos, de los cuales 186.69 correspondieron
a la carga inicial del modelo. Esto se denomina **carga fría**: los pesos aún no
estaban preparados en memoria.

Las solicitudes siguientes tardaron menos de dos segundos porque Ollama mantuvo
el modelo cargado. Esto se denomina **carga caliente**.

Para una demostración en vivo convendrá enviar una consulta de calentamiento
antes de que empiece la presentación. No se debe presentar la carga fría como el
tiempo normal de respuesta de cada pregunta, pero sí registrarla de forma
separada por transparencia.

## 11. Comprobación del uso de GPU

Después de la primera respuesta se ejecutó:

```powershell
ollama ps
```

El resultado fue:

```text
NAME          SIZE      PROCESSOR    CONTEXT
qwen3.5:9b    5.9 GB    100% GPU     8192
```

El registro de Ollama también indicó que las 34 capas fueron asignadas a CUDA.
Por tanto, el modelo se ejecutó completamente en la RTX 3060.

En ese momento `nvidia-smi` informó:

```text
VRAM usada:   8,325 MiB
VRAM libre:   3,791 MiB
Uso de GPU:   100% durante la generación
Temperatura:  42 °C
```

La VRAM total usada incluye otros programas de la computadora, no solamente
Ollama. El valor `5.9 GB` de `ollama ps` es una mejor aproximación al tamaño de
la carga del modelo y su contexto.

## 12. Script reproducible creado

La prueba dejó de ser un comando temporal y quedó implementada en:

```text
scripts/check_local_model.py
```

El script usa únicamente la biblioteca estándar de Python. Hace lo siguiente:

1. consulta la versión de Ollama;
2. obtiene la lista de modelos instalados;
3. confirma que `qwen3.5:9b` exista;
4. ejecuta una pregunta con evidencia;
5. verifica horario y cita;
6. ejecuta una pregunta sin evidencia;
7. verifica la abstención exacta;
8. imprime latencias, tokens y velocidad;
9. devuelve un código de error si alguna prueba falla.

Para ejecutarlo desde la raíz del repositorio:

```powershell
python scripts/check_local_model.py
```

Opciones disponibles:

```powershell
python scripts/check_local_model.py --help
python scripts/check_local_model.py --model qwen3.5:9b
python scripts/check_local_model.py --num-ctx 8192
```

El script no accede todavía a los documentos del TEC. Es deliberadamente una
prueba pequeña de la capa generativa.

## 13. Pruebas automáticas sin cargar el modelo

También se creó:

```text
tests/test_check_local_model.py
```

Estas pruebas comprueban la lógica del script sin necesitar Ollama ni gastar
tiempo cargando Qwen. Validan:

- extracción del nombre del modelo instalado;
- exigencia de contenido y cita;
- forma exacta de abstención;
- cálculo de tokens por segundo.

Se ejecutan junto con las demás pruebas:

```powershell
python -m unittest discover -s tests
```

La distinción es importante:

- las pruebas unitarias verifican nuestro código rápidamente;
- `check_local_model.py` realiza una prueba de integración real contra Ollama.

## 14. Archivos añadidos en esta etapa

```text
nlpArgentina/
├── docs/
│   ├── README.md
│   └── 01-modelo-local-con-ollama.md
├── scripts/
│   └── check_local_model.py
└── tests/
    └── test_check_local_model.py
```

No se modificaron los documentos originales, el corpus procesado, los embeddings
ni la evaluación de recuperación.

## 15. Diagnóstico rápido

Si el script informa que no puede contactar Ollama:

```powershell
ollama --version
Invoke-RestMethod http://localhost:11434/api/version
```

Si Ollama está activo pero falta el modelo:

```powershell
ollama list
ollama pull qwen3.5:9b
```

Para comprobar dónde se ejecuta un modelo cargado:

```powershell
ollama ps
nvidia-smi
```

Si `ollama` no se reconoce inmediatamente después de instalarlo, se puede abrir
una nueva terminal o utilizar temporalmente:

```powershell
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" --version
```

## 16. Estado al terminar

Quedaron comprobadas las dos partes independientes:

```text
pregunta ──→ multilingual-e5-small ──→ cinco fragmentos

contexto de prueba ──→ Qwen 3.5 9B ──→ respuesta o abstención
```

El siguiente paso técnico será unirlas:

```text
pregunta
   ↓
recuperación top-5
   ↓
construcción del prompt con identificadores y metadatos
   ↓
Qwen 3.5 9B
   ↓
respuesta, citas, tiempos y registro observable
```
