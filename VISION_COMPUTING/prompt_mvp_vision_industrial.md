# Prompt — MVP de análisis de video industrial con IA (local, MacBook Pro)

> Pégalo completo como primer mensaje en Claude Code (o tu asistente de código) dentro de una carpeta vacía.

---

## Rol

Actúa como ingeniero senior de visión por computadora y MLOps. Vamos a construir juntos, desde cero y paso a paso, un MVP de análisis de video con IA que corre 100% en local en mi MacBook Pro. Explícame brevemente cada decisión importante, pero prioriza código funcionando sobre teoría.

## Contexto

Quiero una alternativa open source y de bajo costo a NVIDIA VSS (Video Search and Summarization) para plantas industriales. El sistema convierte cámaras (primero simuladas, después las ya instaladas en planta) en sensores inteligentes que detectan eventos, los describen en lenguaje natural y permiten hacer preguntas sobre lo ocurrido.

### Arquitectura objetivo (multimodelo)

```
Cámaras + MediaMTX        → reciben y graban streams RTSP
        ↓
Lector de video           → decodifica cada frame UNA sola vez
        ↓ (fan-out en paralelo)
[Seguridad EPP] [Orden 5S] [Calidad] [Salidas]   → detectores especializados
        ↓ (fan-in)
Motor de reglas + cola    → eventos etiquetados por dominio (Redis)
        ↓
VLM                       → describe el fragmento con un prompt según el dominio
        ↓
PostgreSQL + pgvector     → detecciones, descripciones, embeddings, rutas a clips
        ↓
LLM + interfaz + alertas  → timeline, alertas en tiempo real y chat (RAG)
```

Principios de diseño:

1. El frame se decodifica una vez y se reparte a varios detectores.
2. Cada detector tiene su propia frecuencia y su propia lista de cámaras (configurable en YAML). EPP: varias veces por segundo. Salidas: cada pocos segundos. 5S: cada varios minutos. Calidad: por evento.
3. Cada evento sale etiquetado con su dominio. Las alertas críticas (salida bloqueada) se disparan sin esperar al VLM.
4. Todas las detecciones se guardan en la base aunque no pasen al VLM. Además hay un muestreo de respaldo: un fragmento al VLM cada N minutos por cámara aunque no haya eventos.
5. Todo se comunica por interfaces estándar (RTSP, API compatible con OpenAI, SQL) para que migrar de la Mac a un servidor con GPU NVIDIA solo cambie configuración, no código.

## Mi entorno

- MacBook Pro con Apple Silicon (sin GPU NVIDIA: no usar CUDA, vLLM, NVDEC ni DeepStream).
- **Antes de empezar, verifica chip y RAM** (`sysctl -n machdep.cpu.brand_string`, `sysctl hw.memsize`) y ajusta el tamaño de los modelos a la memoria disponible.
- Tengo Homebrew. Si falta Docker, propón Docker Desktop u OrbStack.

## Stack definido

| Pieza | MVP en Mac |
|---|---|
| Cámaras | Simuladas: MP4 en bucle publicados a MediaMTX con `ffmpeg -re -stream_loop -1 ... -f rtsp` |
| Servidor de video | MediaMTX (con grabación habilitada) |
| Lectura de video | PyAV (o GStreamer vía `gst-python` si conviene), decodificación con VideoToolbox |
| Detector general | Detector de objetos preentrenado (personas, vehículos, objetos) en PyTorch con backend MPS |
| Tracking y zonas | `supervision` (ByteTrack + zonas poligonales) |
| Cola | Redis Streams |
| VLM | Qwen3-VL 8B cuantizado vía Ollama (o `mlx-vlm` si rinde mejor); verifica el tag exacto disponible |
| Embeddings | bge-m3 (Ollama o sentence-transformers) |
| Base de datos | PostgreSQL 16 + pgvector en Docker |
| LLM | Modelo de texto ~8B vía Ollama |
| Interfaz | Streamlit |
| Python | 3.11+, gestionado con `uv` |

### Restricción de licencias

Ultralytics YOLO es AGPL-3.0. Pon el detector detrás de una interfaz (`Detector.detect(frame) -> list[Detection]`) para poder cambiarlo. En el MVP puedes usar Ultralytics por rapidez, pero deja lista una implementación alternativa con RT-DETR de Hugging Face Transformers (Apache 2.0). Revisa también la licencia de cualquier dataset que propongas y avísame si restringe uso comercial.

## Estructura del repositorio

```
vision-mvp/
├── docker-compose.yml        # postgres+pgvector, redis, mediamtx
├── config/
│   ├── cameras.yaml          # cámaras, URLs RTSP, detectores activos y frecuencias
│   ├── zones.yaml            # polígonos por cámara (salidas, áreas 5S)
│   └── rules.yaml            # reglas por dominio
├── prompts/                  # un prompt por dominio (epp, salidas, 5s, calidad, respaldo)
├── scripts/                  # simulate_cameras.sh, setup, utilidades
├── src/
│   ├── ingest/               # lectura RTSP, muestreo de frames, fragmentos y clips
│   ├── detectors/            # interfaz Detector + implementaciones por dominio
│   ├── rules/                # motor de reglas y emisión de eventos
│   ├── vlm/                  # worker que consume la cola y llama al VLM
│   ├── storage/              # esquema SQL, repositorios, embeddings
│   ├── rag/                  # búsqueda híbrida + LLM
│   └── ui/                   # app Streamlit
├── data/                     # videos de prueba, clips, miniaturas (en .gitignore)
└── tests/
```

## Fases (avanza una a la vez)

**Fase 0 — Entorno.** Verifica hardware, instala dependencias, crea el repo con `uv`, `docker-compose.yml` y `.env.example`.
✔ `docker compose up` levanta Postgres, Redis y MediaMTX sin errores.

**Fase 1 — Cámaras simuladas.** Script que publica 4 videos MP4 en bucle como `rtsp://localhost:8554/cam1..cam4`. Sugiéreme fuentes de video industrial de uso libre. Grabación de MediaMTX activa.
✔ Los 4 streams se ven en VLC y `ffprobe` responde.

**Fase 2 — Ingesta.** Un lector por cámara que decodifica una vez, muestrea frames según configuración y corta fragmentos de 10–20 s guardando clip y miniatura. Reconexión automática si el stream cae.
✔ Los fragmentos aparecen en `data/` con timestamps correctos; métricas de fps por cámara en logs.

**Fase 3 — Detección general, zonas y reglas.** Detector general + ByteTrack + zonas de `zones.yaml`. Dominio "Salidas": alerta si hay un objeto en la zona de salida más de X segundos. Eventos etiquetados por dominio publicados en Redis; todas las detecciones guardadas en Postgres.
✔ Al poner un objeto en la zona de salida del video de prueba se genera un evento `salidas` y una alerta.

**Fase 4 — Seguridad EPP.** Detector especializado de cascos y chalecos (fine-tuning sobre un dataset público de EPP, revisando licencia). Evita el olvido de clases: o dataset combinado o dos modelos. Reporta mAP en validación.
✔ Evento `epp` cuando una persona no trae casco o chaleco.

**Fase 5 — VLM y almacenamiento.** Worker que consume la cola, toma 4–8 frames del fragmento, aplica el prompt del dominio y exige salida JSON validada con Pydantic (descripción, personas/objetos, acciones, anomalía, relevancia), con reintentos. Genera embedding y guarda todo en Postgres con pgvector (índice HNSW, tabla particionada por fecha). Incluye el muestreo de respaldo.
✔ Cada evento tiene descripción, JSON válido y embedding; latencia del VLM por fragmento medida y registrada.

**Fase 6 — RAG, interfaz y alertas.** Búsqueda híbrida (vector + filtros SQL por cámara, dominio y tiempo + full-text). Streamlit con: alertas en vivo, timeline de eventos con clip, y chat que responde citando los eventos y mostrando el video.
✔ Puedo preguntar "¿hubo personas sin casco en cam2 en la última hora?" y obtengo respuesta con clips.

**Fase 7 (stretch) — 5S y Calidad.** 5S: snapshot periódico comparado contra imagen de referencia + VLM con checklist. Calidad: detección de anomalías con Anomalib sobre un dataset de ejemplo (revisar licencia).
✔ Eventos `5s` y `calidad` visibles en la interfaz.

**Fase 8 — Preparación para producción.** Documenta cómo conectar cámaras reales (URLs RTSP por marca, uso de substream, VPN/VLAN) y cómo migrar a GPU NVIDIA (vLLM, NVDEC). Script de benchmark: fragmentos/min que entran vs. que el VLM procesa, profundidad de cola y uso de memoria.

## Reglas de trabajo

- Trabaja **una fase a la vez**. Al terminar cada fase: muéstrame cómo probarla, corre los tests y espera mi confirmación antes de seguir.
- Toda configuración en YAML o `.env`; nada de credenciales en el código.
- Código tipado, con logs claros y tests mínimos por módulo.
- Mantén un `README.md` actualizado con cómo levantar y probar cada fase.
- Si una decisión depende de mi hardware o de una licencia, pregúntame antes de continuar.
- Si algo del stack no funciona bien en Apple Silicon, dímelo y propón la alternativa más cercana.

**Empieza con la Fase 0.**
