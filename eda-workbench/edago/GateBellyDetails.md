# Núcleo Cuantitativo por Gate — Cruce con `EDAGuiaGlobal.md`

> **Complemento de `GateGoNoGo.md` y `EDAGuiaGlobal.md`.** > `GateGoNoGo.md` es el esqueleto (la decisión). Este documento es la **pancita**: para cada Gate,
> **qué número se mide, con qué funciones, con qué herramientas, y de qué paso del EDA sale.**
>
> Principio único que gobierna todo el gate:
>
> ```
> EDA computa una cantidad  →  se compara contra un umbral  →  sale el veredicto (GO / COND / NO-GO)
> ```
>
> El veredicto es cualitativo; su **insumo siempre es un número del EDA**.

---

## Herramientas transversales (el ecosistema que sostiene todo)

| Capa                    | Python                                    | R                                  | Para qué                               |
| ----------------------- | ----------------------------------------- | ---------------------------------- | -------------------------------------- |
| Entorno                 | Jupyter / JupyterLab, VS Code             | RStudio, Quarto                    | Iterar por celdas, ver gráficas inline |
| Datos en memoria        | **pandas**, **numpy**                     | data.frame, **tibble** (tidyverse) | La tabla sobre la que todo opera       |
| Cálculo/estadística     | **scipy**, numpy, **statsmodels**         | base R, matrixStats                | Tests, momentos, series de tiempo      |
| Gráficas                | matplotlib, **seaborn**, plotly           | **ggplot2**, plotly                | Ver distribuciones y relaciones        |
| EDA automático          | **ydata-profiling**, Sweetviz             | **DataExplorer**, **skimr**        | Barrido inicial de 30 s                |
| Validación de datos     | **Great Expectations**, **pandera**       | —                                  | Reglas de calidad reproducibles        |
| ML / selección / split  | **scikit-learn**                          | caret, tidymodels                  | Clustering, outliers, `GroupKFold`     |
| Supervivencia (censura) | **scikit-survival** (`sksurv`), lifelines | survival, randomForestSRC          | Cuando no todas las unidades fallaron  |
| Escala (no cabe en RAM) | **Polars**, Dask, PySpark                 | data.table, arrow                  | Datos grandes                          |
| MLOps (Gate 8)          | **MLflow**, Docker, FastAPI               | —                                  | Versionado, empaquetado, servicio      |

> **Barrido inicial (opcional, antes de los gates):** `ProfileReport(df).to_file("report.html")`
> (ydata-profiling) o `sv.analyze(df).show_html()` (Sweetviz) te orientan en segundos, pero **no
> sustituyen** los pasos manuales — sobre todo el temporal (Gate 4/5) y la decisión de modelo.

---

## Mapa : Paso ↔ Gate

Como los Pasos del EDA EDAGuiaGlobal.md se ejecutan implicitamente en los Gates

| Proceso / Paso      | Gates Asociados        | Notas / Observaciones       |
| ------------------- | ---------------------- | --------------------------- |
| Paso 0              | Gate 1                 |                             |
| Pasos 1-2           | Gate 2                 |                             |
| Paso 3 (univariado) | Gate 2, Gate 4         | sirve de apoyo              |
| Paso 4 (target)     | Gate 3, Gate 0, Gate 6 |                             |
| Paso 5 (bi/multi)   | Gate 4                 | Es el "corazón" del proceso |
| Paso 8 (síntesis)   | Gate 7                 |                             |

## Mapa : Gate ↔ Paso del EDA - qué se mide

| Gate                      | Cruce con `EDAGuiaGlobal.md` | Núcleo cuantitativo (la pancita)                                                   |
| ------------------------- | ---------------------------- | ---------------------------------------------------------------------------------- |
| 0 Encuadre de negocio     | — (pre-EDA)                  | ratio costo(FN)/costo(FP)                                                          |
| 1 Accesibilidad y flujo   | **Paso 0** (carga/ingesta)   | frecuencia lograda vs requerida; % uptime pipeline                                 |
| 2 Validez y calidad       | **Pasos 1–2**                | % nulos, # duplicados, # imposibles, # constantes, capping                         |
| 3 Integridad de etiqueta  | **Paso 4** (target)          | # eventos etiquetados, % con timestamp válido, ¿target capado?                     |
| 4 Señal pronóstica        | **Pasos 3, 5, 6**            | \|Pearson\|/\|Spearman\|, PPS/MI, VIF · o monotonicity/trendability/prognosability |
| 5 Horizonte alcanzable    | **Paso 6** (temporal)        | separabilidad por bucket tiempo-a-falla; Prognostic Horizon                        |
| 6 Suficiencia poblacional | **Pasos 1, 4** (conteo)      | N trayectorias, N fallas por modo                                                  |
| 7 Validez de evaluación   | **Paso 8** + práctica ML     | métrica con split por grupo vs baseline ingenuo                                    |
| 8 Desplegabilidad         | — (post-EDA, MLOps)          | latencia (ms), % de alertas accionadas                                             |

> **Regla que hace general al gate:** el número de la pancita **cambia según el tipo de problema**.
> En **tabular estático** (ej. California Housing) el Gate 4 se llena con _correlación con el target_.
> En **prognosis temporal** (tu IIoT) el mismo Gate 4 se llena con _monotonicity/trendability/
> prognosability_. La compuerta es la misma; la métrica que va adentro depende del problema.

---

# Las compuertas por dentro

---

## Gate 0 — Encuadre de negocio

**Cruce EDA:** ninguno (va _antes_ del dato — CRISP-DM Business Understanding).
**Núcleo cuantitativo:** la **asimetría de costo** — `costo_FN / costo_FP`.

No es cálculo de pandas; es aritmética de negocio que fija la métrica de todo lo demás:

- Costo de un **falso negativo** (falla no detectada): paro de línea × horas × $/hora + daños.
- Costo de un **falso positivo** (alarma en vano): revisión innecesaria + tiempo técnico.

**Funciones / herramientas:** hoja de cálculo o `numpy` para la matriz de costo. Define también la
**métrica objetivo** que usarán los Gates 4/5/7: con FN muy caro → **recall / F2 / PR-AUC**, no accuracy.

**Umbral → veredicto:** ratio definido y asimétrico → **GO**. Decisión clara pero costos sin cuantificar
→ **COND**. Sin decisión ni acción → **NO-GO**.

---

## Gate 1 — Accesibilidad y flujo del dato

**Cruce EDA:** **Paso 0 — Carga e ingesta** (DRL Banda C).
**Núcleo cuantitativo:** frecuencia de muestreo lograda vs requerida; % de uptime del pipeline.

**Funciones (Python):**

- `pandas.read_csv()`, `read_parquet()`, `read_excel()`, `read_sql()` — leen cada origen a un DataFrame.
- `parquet` preferible para datos grandes (columnar, tipado, comprimido).
- Parámetros clave: `dtype=` (fuerza tipos, evita corrupción), `parse_dates=` (a datetime), `na_values=`
  (qué cuenta como nulo).

**Funciones (R):** `readr::read_csv()`, `arrow::read_parquet()`, `readxl::read_excel()`,
`data.table::fread()` (rápido para archivos grandes).

**Herramientas:** el conector real a la fuente (PLC/OPC-UA/MTConnect en planta; Pub/Sub, Dataflow en la
nube). Para escala: **Polars / Dask / PySpark**.

**Umbral → veredicto:** frecuencia ≥ la mínima requerida **y** pipeline durable/automatizado → **GO**.
Solo export manual / one-off → **COND**. Dato inaccesible o por debajo de la frecuencia mínima → **NO-GO**.

---

## Gate 2 — Validez y calidad

**Cruce EDA:** **Paso 1 (estructura)** + **Paso 2 (calidad)** (DRL Banda B).
**Núcleo cuantitativo:** % de nulos por columna, # duplicados, # valores imposibles, # columnas
constantes, y **picos en los bordes** (capping).

**Funciones (Python):**

- `df.shape`, `df.info()`, `df.dtypes`, `df.head()` / `df.sample()` — forma, tipos, inspección (Paso 1).
- `df.nunique()` — cardinalidad; detecta IDs y **constantes**.
- `df.isnull().sum()` — conteo de nulos por columna.
- `df.duplicated().sum()` — filas duplicadas.
- `df.describe()` — min/max/media/percentiles; caza **rangos imposibles** (ej. −999 = "sin lectura").
- `df.columns[df.nunique() <= 1]` — columnas constantes (sin señal → se eliminan).
- `df['col'].value_counts()` — **detecta capping**: si un solo valor del borde concentra mucho % (ej.
  `housing_median_age` en 52, o `median_house_value` en 500 001), hay recorte.
- `scipy.stats.skew()` — cuantifica el sesgo (guía la decisión de transformación log más adelante).
- **missingno:** `msno.matrix()` (patrón de huecos), `msno.bar()`, `msno.heatmap()` (¿los nulos de A
  coinciden con los de B?), `msno.dendrogram()`.

**Funciones (R):** `dim()`, `str()`, `glimpse()`, `colSums(is.na(df))`, `sum(duplicated(df))`,
`summary(df)`; **naniar:** `vis_miss(df)`, `gg_miss_var(df)`; `moments::skewness()`.

**Herramientas:** **Great Expectations** / **pandera** para volver las reglas ("esta columna nunca es
negativa") en validación automática cuando el EDA pase a producción.

**Umbral → veredicto:** nulos acotados y explicados, 0 valores imposibles sin explicar, timestamps
consistentes → **GO**. Problemas conocidos con plan de limpieza → **COND**. Dropouts masivos, timestamps
rotos o deriva no corregible → **NO-GO**.

---

## Gate 3 — Integridad de la etiqueta / target

**Cruce EDA:** **Paso 4 — La variable objetivo** (DRL Banda A).
**Núcleo cuantitativo:** # de eventos de falla etiquetados, % con timestamp válido, balance de clases,
y **¿está capado el target?**

**Funciones (Python):**

- `df['y'].value_counts(normalize=True)` — **balance de clases** (un 95/5 cambia toda la estrategia).
- `df['y'].hist()` / `seaborn.kdeplot()` — distribución del target continuo; ¿sesgo?, ¿capping?
  (la línea vertical en el máximo de un scatter es capping hecho gráfico).
- `df['y'].describe()` — rango, y si el máximo concentra masa anómala.
- Si **construyes** el target (RUL, "falla en N horas"), aquí codificas y verificas esas reglas.

**Funciones (R):** `table(df$y)`, `prop.table(table(df$y))`.

**Herramientas:** el **historial de fallas** (CMMS, órdenes de trabajo, log de alarmas) — sin esto no hay
etiqueta. En planta, **este suele ser el asesino silencioso**.

**Umbral → veredicto:** eventos suficientes, bien fechados, modo de falla identificado, target
construible → **GO**. Historial parcial / reconstruible → **COND**. Sin ground truth de fallas → **NO-GO**.

---

## Gate 4 — Contenido de señal pronóstica

**Cruce EDA:** **Paso 3 (univariado)** + **Paso 5 (bi/multivariado)** + **Paso 6 (temporal)**.
**Núcleo cuantitativo — DOS variantes según el problema:**

### 4a. Tabular estático (ej. correlación con el target)

- `df.corr()` — matriz de Pearson (relación **lineal**). `method='spearman'` para monótonas no lineales.
- `df.corr()["target"].sort_values(ascending=False)` — **ranking de features por señal** (esto es el
  Gate 4 en su forma más simple).
- `seaborn.heatmap(df.corr(), annot=True)` — visualiza la matriz; revela **bloques de redundancia**
  (ej. `total_rooms`/`total_bedrooms`/`households` correlacionados 0.9+).
- `seaborn.pairplot()`, `scatterplot()`, `lineplot()` — forma de la relación x vs target.
- **VIF** — `statsmodels.stats.outliers_influence.variance_inflation_factor` — colinealidad; VIF > 5–10
  = features redundantes que podar.
- **PPS / información mutua** — `ppscore.matrix(df)`, `sklearn.feature_selection.mutual_info_regression`
  — captan relaciones **no lineales** que Pearson no ve (una corr ≈ 0 no implica "inútil").

### 4b. Prognosis temporal (métricas PHM — Coble)

- **monotonicity** — ¿la feature tiene tendencia consistente a lo largo de la vida de cada unidad?
- **trendability** — ¿se comporta igual **entre** unidades?
- **prognosability** — ¿el valor en el momento de falla está agrupado en la población?
- Se calculan sobre `df.groupby('unidad')` + `rolling()`; no hay una librería única estándar (se
  implementan a mano o vía toolkits PHM). Rankean sensores objetivamente en vez de a ojo.

**Funciones (R):** `cor()`, `corrplot::corrplot()`, `GGally::ggpairs()`, `car::vif(modelo)`.

**Umbral → veredicto:** ≥1 feature con \|r\|/monotonicity por encima del piso (~0.3 como referencia
gruesa, dependiente del dominio) y VIF < 5–10 tras podar → **GO**. Señal débil/ruidosa → **COND**.
Ninguna feature distinguible del ruido → **NO-GO** (el modo de falla no es observable).

---

## Gate 5 — Horizonte pronóstico alcanzable

**Cruce EDA:** **Paso 6 — Estructura temporal** (métrica PHM — Prognostic Horizon, Saxena).
**Núcleo cuantitativo:** ¿cuánto antes de la falla la señal se separa de forma estable del baseline sano?
Ese punto = horizonte alcanzable. **Se mide, no se fija.**

**Funciones (Python):**

- `df.groupby('unidad')` — operar por unidad.
- `sns.lineplot(data=df, x='tiempo', y='sensor', hue='unidad')` — ¿tendencia (degradación) o ruido plano?
- `df['x'].rolling(window).mean()` / `.rolling(window).std()` — tendencia y ruido bajo la señal.
- `statsmodels.tsa.stattools.adfuller()` — test ADF de estacionariedad.
- `statsmodels.tsa.seasonal.seasonal_decompose()` — separa tendencia / estacionalidad / residuo.
- `statsmodels.graphics.tsaplots.plot_acf()` / `plot_pacf()` — autocorrelación; fuerte ⇒ justifica
  ventanas / LSTM.
- Separabilidad por **bucket de tiempo-a-falla**: agrupar muestras por "horas antes de fallar" y medir
  cuándo la distribución sana y la pre-falla dejan de solaparse (ej. `scipy.stats` para distancia entre
  distribuciones, o AUC de un clasificador simple por bucket).

**Funciones (R):** `dplyr::group_by()`, `tseries::adf.test()`, `forecast::ggAcf()`, `stats::decompose()`,
`stl()`.

**Umbral → veredicto:** horizonte alcanzable ≥ lead time que el negocio necesita para actuar → **GO**.
Horizonte < lo deseado pero > 0 y accionable → **COND**. La señal solo aparece tan cerca de la falla que
no da tiempo a actuar → **NO-GO**.

---

## Gate 6 — Suficiencia poblacional (el problema de "1 trayectoria")

**Cruce EDA:** **Paso 1 (estructura)** + **Paso 4 (target)** — es conteo directo.
**Núcleo cuantitativo:** N de trayectorias run-to-failure independientes; N de fallas por modo.

**Funciones (Python):**

- `df['unidad'].nunique()` — cuántas unidades/activos hay.
- `df.groupby('unidad')['falla'].max().sum()` (o conteo de eventos) — cuántas **trayectorias de falla**.
- `df.groupby('modo_falla').size()` — fallas por modo (para no quedarte corto en un modo raro).

Recuerda: **trayectoria = un ciclo sano→falla**; se acumulan por robots **y** por ciclos de reparación
(ver `GateGoNoGo.md`, Gate 6).

**Umbral → veredicto:** decenas de trayectorias independientes y ~≥20–30 fallas por modo (piso grueso,
dependiente del dominio y el ruido) → **GO**. Pocas → **COND** (considerar supervivencia/censura con
`sksurv`, transfer learning, anomalía no supervisada, o benchmark como CMAPSS para la metodología).
1 (o 0) trayectorias → **NO-GO** para modelar (solo sirve para plumbing).

---

## Gate 7 — Validez de la evaluación

**Cruce EDA:** **Paso 8 (síntesis)** + práctica estándar de ML.
**Núcleo cuantitativo:** la métrica objetivo medida con **split por grupo**, comparada contra un
**baseline ingenuo**; más un chequeo de fuga.

**Funciones (Python):**

- **Split por grupo (sin fuga):** `sklearn.model_selection.GroupKFold`,
  `LeaveOneGroupOut`, `GroupShuffleSplit` — agrupando por `robot_id` / `unit`, para que **todos** los
  ciclos de un activo caigan del mismo lado (ver Gate 7 de `GateGoNoGo.md`).
- **Baseline ingenuo:** `sklearn.dummy.DummyRegressor` / `DummyClassifier`, o una regresión lineal /
  Health Index trivial — el piso que el modelo complejo debe superar.
- **Métrica según Gate 0:** `sklearn.metrics` — `f2`/`fbeta_score`, `average_precision_score` (PR-AUC),
  `recall_score` para desbalance; `mean_squared_error` / RMSE para RUL.
- **Chequeo de fuga:** si un modelo con `robot_id` como feature "predice" demasiado bien, hay huella
  memorizable → confirma la necesidad de split por grupo.

**Funciones (R):** `caret` / `tidymodels` con folds agrupados; `yardstick` para métricas.

**Umbral → veredicto:** el modelo supera al baseline con **split por grupo** y orden temporal respetado
→ **GO**. Esquema definido pero baseline sin medir → **COND**. Solo se puede evaluar con fuga (misma
unidad en ambos lados) → **NO-GO**.

---

## Gate 8 — Desplegabilidad operativa

**Cruce EDA:** ninguno (post-EDA — MLOps; alimenta las Fases 05–06 del roadmap).
**Núcleo cuantitativo:** latencia de inferencia (ms), % de alertas efectivamente accionadas en piloto.

**Funciones / herramientas:**

- **Empaque/servicio:** Docker, FastAPI + TFLite (pod de inferencia), TFLite converter (reducir el
  modelo para edge).
- **Versionado/tracking:** **MLflow** (experimentos, modelos, rollback).
- **Medición:** benchmark de latencia end-to-end (sensor → alerta), y un piloto que registre cuántas
  alertas derivaron en una acción de mantenimiento real.

**Umbral → veredicto:** corre dentro de las restricciones OT/red/latencia **y** hay quién recibe la
alerta y actúa → **GO**. Técnicamente desplegable pero sin dueño de la acción / adopción → **COND**.
Restricciones impiden ejecutar o nadie actuaría → **NO-GO**.

---

## Cómo se usa este documento con los otros dos

```
EDAGuiaGlobal.md          →  CÓMO explorar (el proceso, paso 0–8)
NucleoCuantitativo_por_Gate.md (este)  →  QUÉ número saca cada paso para cada Gate
GateGoNoGo.md             →  QUÉ decides con ese número (umbral → veredicto; global = peor gate)
```

Flujo: corres el EDA → por cada Gate tomas la función/métrica de este documento → aplicas el umbral de
`GateGoNoGo.md` → llenas la tarjeta de veredicto. El veredicto global es la compuerta más débil.

---

_Cruce de `GateGoNoGo.md` × `EDAGuiaGlobal.md` — la métrica de cada Gate cambia entre tabular y prognosis;
la compuerta no._
