# Exploración de Datos (EDA): Proceso Global + Caso Aplicado

Guía en dos partes:

- **Parte 1** — El proceso de EDA paso a paso, de forma general (no atado a un dataset concreto). Para cada paso: qué se hace, qué funciones se usan y qué hacen, en qué lenguaje (Python / R), y qué frameworks aplican y para qué.
- **Parte 2** — El mismo proceso aterrizado en un caso específico: un **elevador de coches** (montacargas que sube un vehículo a un segundo piso).

---

## PARTE 1 — El proceso de EDA, general

El EDA no es "hacer gráficas". Es el proceso de decisión que te lleva de *"tengo un archivo de datos"* a *"sé qué familia de modelos tiene sentido y por qué"*. Cada paso responde una pregunta concreta y descarta o habilita opciones de modelado.

### Herramientas transversales (el ecosistema base)

Antes de los pasos, esto es lo que sostiene todo el flujo:

| Capa | Python | R | Para qué sirve |
|---|---|---|---|
| Entorno | Jupyter Notebook / JupyterLab, VS Code | RStudio, Quarto | Ejecutar código por celdas, ver gráficas inline, iterar |
| Estructura de datos | **pandas** (`DataFrame`), **numpy** (`ndarray`) | **data.frame**, **tibble** (tidyverse) | La tabla en memoria sobre la que todo opera |
| Cálculo numérico | numpy, scipy | base R, matrixStats | Operaciones vectorizadas, estadística |
| Gráficas | matplotlib, **seaborn**, plotly | **ggplot2**, plotly | Visualización estática e interactiva |
| EDA automatizado | **ydata-profiling**, Sweetviz, AutoViz, D-Tale | **DataExplorer**, **skimr** | Generar un reporte completo con una sola línea |

**Frameworks de EDA automatizado — qué hacen exactamente:**
- **ydata-profiling** (antes `pandas-profiling`): con `ProfileReport(df).to_file("report.html")` genera un HTML con distribuciones, correlaciones, nulos, alertas de calidad y cardinalidad de cada columna. Es tu "primer barrido" de 30 segundos.
- **Sweetviz**: `sv.analyze(df).show_html()` — parecido, pero fuerte en **comparar** dos datasets (train vs test) o comparar clases de la variable objetivo.
- **DataExplorer** (R): `create_report(df)` produce el equivalente en R.
- **skimr** (R): `skim(df)` da un resumen tabular rico (mejor que `summary()`) directo en consola.

> Regla práctica: el reporte automático te orienta, pero **no sustituye** los pasos manuales — sobre todo el análisis temporal y la decisión de modelo, que ninguna herramienta automática hace por ti.

---

### Paso 0 — Carga e ingesta

**Qué haces:** meter los datos a memoria en el formato correcto, sin corromper tipos.

**Python:**
- `pandas.read_csv()`, `read_parquet()`, `read_excel()`, `read_sql()` — leen distintos orígenes a un DataFrame. `parquet` es preferible para datos grandes (columnar, tipado, comprimido).
- Parámetros clave: `dtype=` (fuerza tipos), `parse_dates=` (convierte columnas a datetime), `na_values=` (define qué cuenta como nulo).

**R:**
- `readr::read_csv()`, `arrow::read_parquet()`, `readxl::read_excel()`.
- `data.table::fread()` — muy rápido para archivos grandes.

**Frameworks para escala:** si los datos no caben en RAM → **Polars** (Python/Rust, mucho más rápido que pandas), **Dask** o **PySpark** (procesamiento distribuido).

---

### Paso 1 — Estructura y contexto

**Qué haces:** entender la forma y granularidad. ¿Qué representa una fila? ¿Cuántas filas/columnas? ¿Qué es cada columna (ID, categórica, numérica, tiempo)?

**Python:**
- `df.shape` → dimensiones (filas, columnas).
- `df.info()` → tipos de cada columna, no-nulos, memoria.
- `df.head()` / `df.sample(5)` → inspección visual de valores reales.
- `df.dtypes` → tipos de dato.
- `df.nunique()` → cardinalidad (cuántos valores distintos por columna; detecta IDs y constantes).

**R:**
- `dim(df)`, `str(df)`, `glimpse(df)` (dplyr), `head(df)`, `sapply(df, class)`.

---

### Paso 2 — Calidad de datos

**Qué haces:** encontrar problemas que romperían el modelo: nulos, duplicados, columnas constantes, rangos imposibles.

**Python:**
- `df.isnull().sum()` → conteo de nulos por columna.
- `df.duplicated().sum()` → filas duplicadas.
- `df.describe()` → min/max/media/percentiles; detecta rangos imposibles (ej. una temperatura de -999 que en realidad es un código de "sin lectura").
- Columnas constantes: `df.columns[df.nunique() <= 1]` — no aportan señal, se eliminan.
- **missingno** (librería dedicada a nulos): `msno.matrix(df)` (patrón visual de huecos), `msno.bar(df)`, `msno.heatmap(df)` (¿los nulos de A coinciden con los de B?), `msno.dendrogram(df)`.

**R:**
- `colSums(is.na(df))`, `sum(duplicated(df))`, `summary(df)`.
- **naniar**: `vis_miss(df)`, `gg_miss_var(df)` — el equivalente de missingno.

**Frameworks de validación (para pipelines, no solo EDA):** **Great Expectations** o **pandera** (Python) — defines reglas ("esta columna nunca es negativa") y validas automáticamente. Útil cuando el EDA se vuelve producción.

---

### Paso 3 — Análisis univariado

**Qué haces:** entender cada variable por separado: su distribución, escala, forma, colas.

**Python:**
- Numéricas: `df['x'].hist()`, `seaborn.histplot()`, `seaborn.kdeplot()` (densidad suavizada), `seaborn.boxplot()` (mediana, cuartiles, outliers).
- Categóricas: `df['x'].value_counts()`, `seaborn.countplot()`.
- Forma de la distribución: `scipy.stats.skew()` (asimetría — indica si conviene transformación log), `scipy.stats.kurtosis()` (colas pesadas).
- Normalidad: `scipy.stats.shapiro()` o `normaltest()` — si vas a usar métodos que asumen normalidad.

**R:**
- `ggplot2`: `geom_histogram()`, `geom_density()`, `geom_boxplot()`, `geom_bar()`.
- `moments::skewness()`, `moments::kurtosis()`, `shapiro.test()`.

**Decisión que sale de aquí:** ¿necesito escalar/normalizar? ¿aplicar `log`/`Box-Cox` a variables sesgadas? ¿hay multimodalidad (dos picos) que sugiera subpoblaciones/regímenes?

---

### Paso 4 — La variable objetivo (target)

**Qué haces:** analizar a fondo lo que quieres predecir. Este paso define el tipo de problema.

**Python:**
- **Regresión** (target continuo): distribución con `histplot`/`kdeplot`; ¿está sesgado?, ¿necesita transformación?
- **Clasificación** (target categórico): `df['y'].value_counts(normalize=True)` → **balance de clases**. Un 95/5 cambia por completo tu estrategia (métricas, resampling, umbral).
- Si construyes el target (ej. un RUL o un "va a fallar en N horas"), aquí decides las reglas de esa construcción.

**R:** `table(df$y)`, `prop.table(table(df$y))`.

**Decisión que sale de aquí:** regresión vs. clasificación vs. supervivencia; qué **métrica** optimizar. Con desbalance y coste alto de falso negativo → recall, **F2**, **PR-AUC**, y selección de umbral por curva de coste (no F1/accuracy por defecto).

---

### Paso 5 — Análisis bivariado y multivariado

**Qué haces:** relaciones entre variables, y de cada variable con el target. Detectar redundancia (colinealidad).

**Python:**
- `df.corr()` → matriz de correlación (Pearson por defecto; `method='spearman'` para relaciones monótonas no lineales).
- `seaborn.heatmap(df.corr(), annot=True)` → visualiza la matriz.
- `seaborn.pairplot(df)` → todas las dispersiones por pares (caro si hay muchas columnas).
- `seaborn.scatterplot()`, `seaborn.lineplot()` → relación puntual x vs y.
- Colinealidad severa: **VIF** con `statsmodels.stats.outliers_influence.variance_inflation_factor` — si VIF > 5–10, hay features redundantes.
- **Poder predictivo no lineal**: `ppscore` (`pps.matrix(df)`) — a diferencia de la correlación, detecta relaciones no lineales y asimétricas hacia el target.

**R:**
- `cor(df)`, `corrplot::corrplot()`, `GGally::ggpairs()`, `car::vif(modelo)`.

**Decisión que sale de aquí:** ¿la relación feature–target es lineal (favorece modelos lineales) o curva (favorece árboles/gradient boosting/redes)? ¿elimino features redundantes o aplico reducción de dimensión?

---

### Paso 6 — Estructura temporal / agrupada (si aplica)

**Qué haces:** si hay tiempo o grupos (unidades, máquinas, usuarios), analizar cómo evolucionan las variables *dentro* de cada grupo. **Este paso es el que las herramientas automáticas no hacen y el que más decide en mantenimiento predictivo.**

**Python:**
- `df.groupby('unidad')` → operar por grupo.
- Graficar trayectorias: `sns.lineplot(data=df, x='tiempo', y='sensor', hue='unidad')` → ¿el sensor tiene tendencia (degradación) o es ruido plano?
- Tendencia y ruido: media móvil `df['x'].rolling(window).mean()`, desviación móvil `.rolling(window).std()`.
- Estacionariedad: `statsmodels.tsa.stattools.adfuller()` (test ADF — ¿la serie es estacionaria?).
- Descomposición: `statsmodels.tsa.seasonal.seasonal_decompose()` → separa tendencia / estacionalidad / residuo.
- Autocorrelación: `statsmodels.graphics.tsaplots.plot_acf()` / `plot_pacf()` → ¿cuánto influye el pasado en el presente? (justifica ventanas/LSTM).

**R:**
- `dplyr::group_by()`, `tseries::adf.test()`, `forecast::ggAcf()`, `stats::decompose()`, `stl()`.

**Decisión que sale de aquí:** ¿hay señal degradativa monótona (base de un **Health Index** / regresión de tendencia)? ¿dependencia temporal fuerte (ventanas deslizantes, LSTM/Temporal CNN)? ¿debo normalizar *por grupo/régimen* en vez de global?

---

### Paso 7 — Regímenes y outliers

**Qué haces:** detectar subpoblaciones (modos de operación) y valores anómalos.

**Python:**
- Clustering exploratorio: `sklearn.cluster.KMeans`, `DBSCAN` sobre las variables de operación → ¿los datos se agrupan en condiciones distintas?
- Reducción para visualizar: `sklearn.decomposition.PCA`, o `umap-learn` / `sklearn.manifold.TSNE` → proyectar a 2D y ver estructura/clusters.
- Outliers: `IsolationForest`, `LocalOutlierFactor`, o regla IQR (`Q1 - 1.5*IQR`).

**R:** `kmeans()`, `dbscan::dbscan()`, `prcomp()` (PCA), `Rtsne::Rtsne()`.

**Decisión que sale de aquí:** si hay regímenes distintos, la normalización y el modelado deben ser conscientes de ellos (normalizar por régimen). Si no lo haces, el análisis posterior queda contaminado.

---

### Paso 8 — Síntesis y decisión de modelo

**Qué haces:** cerrar el EDA respondiendo, en una frase, **qué señal vas a explotar y por qué**. De ahí se deriva la familia de modelos:

| Hallazgo del EDA | Familia de modelo sugerida |
|---|---|
| Relación feature–target lineal | Regresión lineal / logística, modelos lineales regularizados |
| Relación no lineal, features tabulares mixtas | Random Forest, **Gradient Boosting** (XGBoost/LightGBM/CatBoost) |
| Señal degradativa monótona en el tiempo | Health Index + regresión de tendencia |
| Datos censurados (no todos fallaron) | Análisis de supervivencia (Cox, Weibull, Random Survival Forest) |
| Dependencia temporal fuerte, secuencias | LSTM / GRU / Temporal CNN / Transformers |
| Fuerte desbalance + coste alto de FN | Clasificación con F2/PR-AUC + umbral por coste |

**Regla de cierre:** no toques modelos hasta poder escribir esa frase. Si el EDA no te la da, aún no terminaste.

---
---

## PARTE 2 — Caso aplicado: elevador de coches (montacargas a 2º piso)

**El activo:** un elevador que sube un automóvil de la planta baja a un segundo piso. Puede ser **hidráulico** (pistón + bomba + aceite) o de **tracción** (motor + cables + contrapeso). El objetivo de negocio típico: predecir fallas antes de que el elevador se detenga con un coche dentro (falso negativo = coche atrapado + parada de servicio + posible riesgo de seguridad → coste alto, igual que tu lógica de F2/recall).

### Sensores que instrumentarías (las "columnas")

| Sensor | Qué mide | Por qué importa |
|---|---|---|
| Corriente del motor (A) | Consumo eléctrico | Sube con fricción, carga o desgaste de rodamientos |
| Voltaje (V) | Alimentación | Caídas → problemas eléctricos |
| Temperatura del motor (°C) | Calentamiento | Tendencia al alza = degradación |
| Vibración / acelerómetro (RMS, FFT) | Vibración de motor/rodamientos | Firma clásica de desgaste mecánico |
| Presión hidráulica (bar) | Presión del pistón | Caída = fuga de sello (en hidráulicos) |
| Tensión de cable (N) | Carga en cables | Desgaste de cable (en tracción) |
| Posición / encoder | Altura, piso actual | Deriva de posición, nivelación |
| Tiempo de ascenso (s) | Duración baja→2º piso | Se alarga si la bomba/hidráulica se degrada |
| Ciclos de puerta | Aperturas/cierres | Desgaste de mecanismo de puerta |
| Nº de viajes (contador) | Uso acumulado | Proxy de "edad" / horas de operación |

### Modos de falla (lo que quieres anticipar)

Desgaste de rodamientos del motor, fuga en sellos hidráulicos, desgaste de cable/freno, sobrecorriente por fricción en rieles, fallo de contactores eléctricos.

---

### El EDA aplicado, paso por paso

**Paso 1 — Estructura.** Decides la granularidad: una fila = una muestra a X Hz durante cada viaje, o una fila = un viaje resumido. `df.shape`, `df.info()`. La unidad es *el elevador* (o varios elevadores de un edificio → hay `hue='elevador'`). Identificas: ID de viaje, timestamp, sensores, y el contador de viajes como proxy de vida.

**Paso 2 — Calidad.** `df.isnull().sum()` para detectar dropouts del sensor (frecuente en vibración/acelerómetros baratos). `df.describe()` para cazar lecturas imposibles (presión = 0 durante un viaje activo = sensor caído, no presión real). `msno.matrix()` para ver si los huecos son aleatorios o por bloques (fallo de gateway).

**Paso 3 — Univariado.** Histograma de corriente: casi seguro será **bimodal** — un pico "subida" (motor trabajando contra gravedad) y otro "bajada" (menos esfuerzo). Eso ya te dice que **no puedes analizar la corriente sin separar dirección del viaje**. Boxplot de temperatura, distribución del tiempo de ascenso.

**Paso 4 — Target.** Aquí decides el problema:
- *Opción A — Clasificación:* etiquetar cada viaje como "normal" vs "anómalo/pre-falla". `value_counts(normalize=True)` mostrará desbalance fuerte (las fallas son raras) → F2/PR-AUC, no accuracy.
- *Opción B — Regresión de RUL:* estimar viajes/horas restantes hasta mantenimiento. Requiere historial run-to-failure.
- *Opción C — Supervivencia:* si tienes elevadores que aún no fallan (censurados), modelar probabilidad de falla en el tiempo.

**Paso 5 — Multivariado.** `df.corr()` + heatmap. Esperarías correlación fuerte **corriente ↔ carga ↔ temperatura**. Si la corriente sube pero la carga (peso del coche) es la misma → señal de fricción/desgaste, no de carga. `scatterplot(x='peso_coche', y='corriente', hue='mes')`: si la nube de puntos se desplaza hacia arriba mes a mes con el mismo peso, eso **es** la degradación.

**Paso 6 — Temporal (el paso decisivo aquí).** Agrupas por elevador y grafica en el tiempo:
- **Tiempo de ascenso** vs. fecha: una tendencia lenta al alza en un elevador hidráulico = fuga de sello progresiva. Señal degradativa de oro para un Health Index.
- **Vibración RMS** vs. viajes acumulados: `rolling(window).mean()` para ver la tendencia bajo el ruido. Subida sostenida = rodamiento muriendo.
- **Temperatura del motor** vs. tiempo: deriva al alza.
- `plot_acf()` sobre la vibración: si hay fuerte autocorrelación, justifica un modelo con ventanas temporales (LSTM) en vez de tratar cada viaje como independiente.

**Paso 7 — Regímenes.** Aquí es crítico segmentar por **modo de operación**: subida vs. bajada, cargado vs. vacío, y quizá temperatura ambiente (verano/invierno afecta viscosidad del aceite hidráulico). Un `KMeans` sobre {dirección, peso, temperatura ambiente} confirma los clusters. La normalización de corriente/tiempo debe hacerse **dentro de cada régimen** — si comparas un viaje de subida cargado contra uno de bajada vacío, todo se ve como "anomalía" y no lo es.

**Paso 8 — Síntesis → decisión.**

La frase de cierre podría ser: *"El tiempo de ascenso y la vibración RMS muestran tendencia monótona ascendente por viaje acumulado, correlacionada con desgaste; la corriente depende del régimen (dirección/carga) por lo que se normaliza por régimen."*

De ahí:
- **Health Index** construido a partir de tiempo de ascenso + vibración + temperatura (variables con tendencia degradativa clara) → base para RUL.
- Si el objetivo es alerta binaria pre-falla → **Gradient Boosting** (LightGBM) sobre features por viaje (incluyendo estadísticos de la ventana temporal), optimizando **F2/PR-AUC** con umbral por curva de coste, porque un coche atrapado (FN) cuesta muchísimo más que una revisión innecesaria (FP).
- Si hay dependencia temporal fuerte confirmada por ACF → **LSTM** sobre ventanas de sensores.
- Si tienes flota de elevadores con unos aún sin fallar → **análisis de supervivencia** para modelar el censurado.

---

### Resumen del mapeo caso → decisión

| Lo que el EDA reveló | Lo que decides |
|---|---|
| Corriente bimodal por dirección/carga | Normalizar por régimen antes de modelar |
| Tiempo de ascenso con tendencia al alza | Health Index / señal de fuga hidráulica |
| Vibración RMS creciente con los viajes | Feature de degradación de rodamiento |
| Fallas raras, coste alto de FN | Métrica F2 / PR-AUC + umbral por coste |
| Autocorrelación temporal fuerte | Ventanas deslizantes / LSTM |
| Flota con unidades censuradas | Modelo de supervivencia |
