# Entorno de Exploración de Datos (EDA) — Setup para el equipo

> **Para qué es esto.** Un entorno reproducible que soporta las tres guías del flujo:
> `EDAGuiaGlobal.md` (cómo explorar) → `NucleoCuantitativo_por_Gate.md` (qué número saca cada paso) →
> `GateGoNoGo.md` (qué se decide con ese número). Todo developer debe poder levantar el mismo entorno,
> abrir un notebook y seguir la guía sin pelear con dependencias.

---

## Decisión rápida: Docker o local

- **Docker (recomendado para el equipo).** Mismo entorno para todos, cero "en mi máquina sí funciona".
  Además la imagen base `datascience-notebook` ya trae **Python + R**, así que las columnas en R de la
  guía funcionan sin instalar nada extra.
- **Local (venv/conda).** Más rápido para trabajar en una sola máquina; sirve si no quieres Docker.

No existe un "contenedor oficial de EDA" con ydata-profiling, sweetviz, etc. ya incluidos. La práctica
profesional es: **partir de la imagen Jupyter oficial y montarle encima las librerías de EDA** (eso es lo
que hace el Dockerfile de abajo).

---

## Opción A — Docker (recomendada)

### A.1 Imagen base

Las imágenes oficiales de Jupyter viven en **Quay.io** (desde 2023-10-20 ya no se actualizan en Docker Hub):

| Imagen | Incluye | Cuándo usarla |
|---|---|---|
| `quay.io/jupyter/datascience-notebook` | Python + **R (tidyverse)** + Julia, JupyterLab, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, statsmodels | **Recomendada** — soporta las columnas R de la guía |
| `quay.io/jupyter/scipy-notebook` | Solo Python (mismo stack científico), más ligera | Si no vas a usar R |

Usa siempre un **tag de fecha** (no `latest`) para reproducibilidad. Al momento de escribir, un tag válido
reciente es `2026-07-28`; revisa el más nuevo en Quay.io y fíjalo.

Prueba de humo sin construir nada:

```bash
docker run -it --rm -p 10000:8888 -v "${PWD}":/home/jovyan/work \
  quay.io/jupyter/datascience-notebook:2026-07-28
```

Abre `http://localhost:10000/?token=<token que imprime la consola>`. Tu carpeta actual queda montada en
`/home/jovyan/work`.

### A.2 Dockerfile del proyecto (con los extras de EDA)

```dockerfile
# Dockerfile
FROM quay.io/jupyter/datascience-notebook:2026-07-28
# Alternativa solo-Python, más ligera:
# FROM quay.io/jupyter/scipy-notebook:2026-07-28

# El base YA trae: pandas, numpy, scipy, matplotlib, seaborn, scikit-learn,
# statsmodels, JupyterLab (y R+tidyverse en datascience-notebook).
# Aquí solo montamos los extras de EDA que no vienen incluidos.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
```

### A.3 docker-compose (para el equipo)

```yaml
# docker-compose.yml
services:
  eda:
    build: .
    image: eda-workbench:latest
    ports:
      - "10000:8888"
    volumes:
      - ./work:/home/jovyan/work        # notebooks y datos persisten aquí
    environment:
      - JUPYTER_TOKEN=eda-dev           # token fijo compartido (cámbialo)
```

Levantar:

```bash
docker compose build
docker compose up
# -> http://localhost:10000/?token=eda-dev
```

---

## Opción B — Entorno local

### B.1 Con venv (pip)

```bash
python3.12 -m venv .venv          # Python 3.11 o 3.12 recomendado
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name eda --display-name "Python (EDA)"
jupyter lab
```

### B.2 Con conda / mamba

```yaml
# environment.yml
name: eda
channels: [conda-forge]
dependencies:
  - python=3.12
  - pandas
  - numpy
  - scipy
  - statsmodels
  - matplotlib
  - seaborn
  - plotly
  - scikit-learn
  - missingno
  - polars
  - pyarrow
  - jupyterlab
  - ipywidgets
  - pip
  - pip:
      - ydata-profiling
      - sweetviz
      - ppscore
      - scikit-survival
      - lifelines
      - pandera
      - great-expectations
```

```bash
conda env create -f environment.yml   # o: mamba env create -f environment.yml
conda activate eda
jupyter lab
```

---

## requirements.txt (copiar tal cual)

```text
# ============================================================
#  Entorno EDA — soporta EDAGuiaGlobal / NucleoCuantitativo / GateGoNoGo
#  (En Docker con datascience-notebook, los del bloque "Core" y "Viz"
#   ya vienen en la imagen; pip los verá satisfechos.)
# ============================================================

# --- Core: la tabla y la estadística (Gates 2, 4, 5) ---
pandas
numpy
scipy
statsmodels            # VIF, ADF, ACF/PACF, seasonal_decompose

# --- Visualización (Pasos 3, 5, 6) ---
matplotlib
seaborn
plotly

# --- EDA automatizado: barrido inicial de 30 s ---
ydata-profiling        # ProfileReport(df).to_file("report.html")
sweetviz               # sv.analyze(df) / comparar train vs test

# --- Datos faltantes (Gate 2) ---
missingno              # msno.matrix / bar / heatmap / dendrogram

# --- Señal y selección de features (Gate 4) ---
scikit-learn           # mutual_info, clustering, GroupKFold, baseline, métricas
ppscore                # poder predictivo no lineal (lo que Pearson no ve)

# --- Supervivencia / censura (Gate 6, cuando faltan trayectorias) ---
scikit-survival        # import sksurv  (requiere compilación; ver notas)
lifelines

# --- Validación de datos reproducible (Gates 1–2 hacia producción) ---
pandera
great-expectations

# --- Escala: datos que no caben en RAM (Paso 0 / Gate 1) ---
polars
pyarrow                # leer/escribir parquet

# --- Notebook / kernel ---
jupyterlab
ipykernel
ipywidgets             # barras de progreso de ydata-profiling

# --- Series de tiempo extra (opcional) ---
# sktime

# --- MLOps (Gate 8 — más para despliegue que para EDA; opcional aquí) ---
# mlflow
```

---

## Catálogo — qué librería alimenta qué Gate

| Librería | Para qué sirve | Gate / Paso |
|---|---|---|
| pandas, numpy | La tabla en memoria; toda operación | Todos |
| scipy | `skew`, `kurtosis`, tests de normalidad, distancias | 2, 4 |
| statsmodels | VIF, ADF, ACF/PACF, `seasonal_decompose` | 4, 5 |
| matplotlib, seaborn, plotly | Histogramas, heatmap, boxplot, líneas, scatter | 2, 3, 4, 5 |
| ydata-profiling, sweetviz | Reporte automático inicial | Barrido previo |
| missingno | Patrón de nulos (¿aleatorios o por bloques?) | 2 |
| scikit-learn | `mutual_info`, KMeans/DBSCAN, `IsolationForest`, `GroupKFold`/`LeaveOneGroupOut`, `Dummy*`, métricas | 4, 6, 7 |
| ppscore | Relaciones no lineales feature→target | 4 |
| scikit-survival, lifelines | Modelado con censura cuando hay pocas trayectorias | 6 |
| pandera, great-expectations | Convertir reglas de calidad en validación automática | 1, 2 |
| polars, pyarrow | Datos grandes / parquet | 0-Paso, 1 |
| mlflow (opcional) | Tracking, versionado, rollback | 8 |

---

## Verificación (smoke test)

Guarda como `verificar_entorno.py` y córrelo dentro del entorno / contenedor:

```python
import importlib

libs = ["pandas","numpy","scipy","statsmodels","matplotlib","seaborn","plotly",
        "ydata_profiling","sweetviz","missingno","sklearn","ppscore",
        "sksurv","lifelines","pandera","polars","pyarrow"]

for name in libs:
    try:
        m = importlib.import_module(name)
        print(f"OK    {name:16} {getattr(m, '__version__', '?')}")
    except Exception as e:
        print(f"FALLA {name:16} -> {type(e).__name__}: {e}")

# Prueba real: un ProfileReport mínimo debe generarse sin error
import pandas as pd, numpy as np
from ydata_profiling import ProfileReport
df = pd.DataFrame({"x": np.random.randn(200), "y": np.random.randint(0, 3, 200)})
ProfileReport(df, minimal=True).to_file("smoke_report.html")
print("ProfileReport OK -> smoke_report.html")
```

Nombres de import que no coinciden con el de pip: `ydata-profiling` → `ydata_profiling`,
`scikit-learn` → `sklearn`, `scikit-survival` → `sksurv`.

---

## Notas de compatibilidad (léelas, ahorran horas)

- **ydata-profiling es la dependencia más quisquillosa.** Pinea versiones de pandas/numpy/matplotlib con
  rangos estrechos y a veces choca con lo que trae la imagen base. Si el build falla o degrada paquetes:
  instálala primero y **congela** el entorno alrededor de ella, o aíslala en su propio env solo para
  generar reportes.
- **scikit-survival compila código** (necesita toolchain C/C++ y a veces `osqp`/`ecos`). En Docker suele
  ir bien; en local Windows puede dar guerra. Si no vas a usar censura todavía, coméntala.
- **Python 3.11 o 3.12.** Evita el más nuevo del mes hasta que las librerías de EDA lo alcancen.
- **Fija versiones para reproducir.** Tras un build exitoso, genera el lock:
  ```bash
  pip freeze > requirements.lock.txt
  ```
  Aún mejor, gestiona `requirements.txt` (sin pins) → `requirements.lock.txt` (con pins) usando
  **pip-tools** (`pip-compile`) o **uv** (`uv pip compile`). El equipo instala desde el `.lock`.
- **No uses el tag `latest`** de la imagen; usa el tag de fecha para que todos tengan lo mismo.

---

## Onboarding — cómo lo usa un developer

1. Clona el repo (los tres `.md` de guía + carpeta `work/` para notebooks).
2. `docker compose up` (o activa el venv). Abre JupyterLab.
3. Crea **un notebook por dataset**, con las secciones nombradas como los **Pasos 0–8** de
   `EDAGuiaGlobal.md`.
4. En cada Gate, toma la función/métrica de `NucleoCuantitativo_por_Gate.md`, computa el número.
5. Aplica el umbral de `GateGoNoGo.md` y llena la **tarjeta de veredicto**. El veredicto global = la
   compuerta más débil.
6. Antes de entrenar, escribe la **frase de cierre** obligatoria (señal a explotar, horizonte, familia
   de modelo y por qué).

Convención sugerida de repo:

```
repo/
├── guias/
│   ├── EDAGuiaGlobal.md
│   ├── NucleoCuantitativo_por_Gate.md
│   └── GateGoNoGo.md
├── work/                 # notebooks + datos (montado en Docker)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── verificar_entorno.py
```

---

*Entorno reproducible para el flujo EDA → Gate. Imagen base: `quay.io/jupyter/datascience-notebook`
(Python + R). Congela versiones antes de repartir al equipo.*
