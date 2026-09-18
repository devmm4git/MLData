# La varianza en el preprocesamiento de datos

## Qué es la varianza (la intuición)

La varianza mide **qué tanto se dispersan los valores de una columna alrededor de su promedio**. En una frase: cuánto varían los datos entre sí.

- **Varianza alta** → los valores están muy regados (unos chicos, otros grandes).
- **Varianza baja** → los valores están apretados, parecidos entre sí.
- **Varianza cero** → todos los valores son idénticos. No hay ninguna dispersión porque no hay nada que disperse.

Por eso _"constante"_ y _"varianza cero"_ son la misma cosa dicha de dos formas: si todas las filas tienen el mismo valor (`pais = "México"`), no hay variación → la varianza da exactamente **0**.

## Sí, es un cálculo (la fórmula, sin miedo)

Se calcula en tres pasos:

1. Sacas el **promedio** de la columna.
2. A cada valor le **restas el promedio y elevas al cuadrado** esa diferencia (así todas las diferencias son positivas y las grandes pesan más).
3. **Promedias** todas esas diferencias al cuadrado. Ese promedio es la varianza.

La clave para entender el "cero": en el paso 2, cada valor menos el promedio da **0** cuando todos los valores son iguales (porque el promedio de un montón de "México" es "México", y México − México = 0). Cero al cuadrado sigue siendo cero, y el promedio de puros ceros es cero. Ahí nace la varianza cero.

### Un ejemplo numérico de bolsillo

```
Columna A = [5, 5, 5, 5]      promedio = 5
  diferencias: (5-5), (5-5), (5-5), (5-5) = 0, 0, 0, 0
  al cuadrado: 0, 0, 0, 0
  varianza = promedio(0,0,0,0) = 0      ← CONSTANTE

Columna B = [2, 4, 6, 8]      promedio = 5
  diferencias: -3, -1, 1, 3
  al cuadrado: 9, 1, 1, 9
  varianza = promedio(9,1,1,9) = 5      ← SÍ varía
```

## Compruébalo con tus datos

Córrelo y verás el `pais` en 0 y el resto con números > 0:

```python
# varianza de las columnas numericas del experimento
df_mexico.var(numeric_only=True)
```

```python
# la varianza de una constante es 0; comparala con una que si varia
import numpy as np
print("varianza de pais (constante):", np.var(df_mexico["pais"].astype("category").cat.codes))
print("varianza de Age (varia):     ", round(df["Age"].var(), 2))
print("varianza de Fare (varia):    ", round(df["Fare"].var(), 2))
```

Deberías ver algo como: `pais` → 0.0, `Age` → ~211, `Fare` → ~2469. El 0 confirma numéricamente lo que la función de constantes detectó "por conteo".

## Por qué esto importa para el modelo

Aquí se cierra el círculo con lo de _"no aporta señal"_:

Un modelo aprende de la **variación**. Busca patrones del tipo _"cuando esta columna sube/cambia, el resultado tiende a cambiar así"_. Si una columna no varía (varianza 0), no hay ningún _"cuando cambia"_ que observar → literalmente **no hay nada que aprender de ella**. Por eso se elimina: matemáticamente no puede contribuir.

De hecho, hay una técnica de selección de features llamada **`VarianceThreshold`** (en scikit-learn) que automatiza justo esto: tira las columnas cuya varianza está por debajo de un umbral. La versión más agresiva (umbral 0) elimina exactamente las constantes.

## ¿Si la varianza es mayor a cero, es buena para el modelo?

**No necesariamente.** Que la varianza sea > 0 es una condición **necesaria pero no suficiente**.

Piénsalo así: varianza > 0 solo garantiza que _"hay algo que observar"_, **no** que ese algo tenga relación con lo que quieres predecir. Son dos cosas distintas:

- La **varianza** mide cuánto varía la columna **consigo misma** (dispersión interna).
- El **poder predictivo** mide cuánto se relaciona la columna **con el objetivo**.

Una columna puede tener muchísima varianza y aun así ser **puro ruido**. Ejemplo clásico: un identificador aleatorio (un `UUID`, un folio, un número de serie) varía enormemente entre filas, pero no dice nada sobre el objetivo. Alta varianza, cero utilidad.

> **Regla:** varianza 0 → descarta con seguridad (no puede aportar nada). Varianza > 0 → es solo una **candidata**; todavía falta comprobar si de verdad se relaciona con el objetivo.

Dos trampas más que conviene tener presentes:

1. **La varianza depende de la escala/unidades.** La misma información medida en metros vs milímetros tiene varianzas radicalmente distintas sin haber cambiado su contenido. Por eso **comparar varianzas crudas entre columnas es engañoso**, y por eso `VarianceThreshold` con umbral > 0 exige normalizar primero (ver abajo).
2. **"Aporta señal" no se decide con la varianza.** Cuánto predice de verdad cada columna se mide con herramientas de relación con el objetivo: correlación, _mutual information_, importancia de features de un modelo, etc. (eso corresponde al **Paso 5 / Gate 4**). La varianza sola no lo dice; solo sirve para tirar el caso extremo de varianza 0 (o casi 0).

En corto: **la varianza es un filtro barato de descarte, no un medidor de calidad.** Elimina lo que con seguridad no sirve (constantes); no promueve nada a "buena feature".

## Cómo usar `VarianceThreshold`

`VarianceThreshold` es un selector de scikit-learn que **elimina las columnas cuya varianza cae por debajo de un umbral**. Con `threshold=0.0` quita exactamente las constantes.

**Uso básico (eliminar solo constantes):**

```python
import pandas as pd
from sklearn.feature_selection import VarianceThreshold

# 1. Solo columnas numericas (VarianceThreshold no acepta texto)
X = df.select_dtypes(include="number")

# 2. Umbral 0 = elimina unicamente las columnas constantes (varianza exacta 0)
selector = VarianceThreshold(threshold=0.0)
selector.fit(X)

# 3. Ver que columnas sobreviven y cuales se van
mask = selector.get_support()          # array de True (se queda) / False (se va)
cols_conservadas = X.columns[mask]
cols_eliminadas  = X.columns[~mask]
print("Se eliminan:", list(cols_eliminadas))

# 4. Aplicar la transformacion (devuelve un numpy array)
X_reducido = selector.transform(X)

# 5. Recuperar los nombres de columna (transform pierde el DataFrame)
X_reducido = pd.DataFrame(X_reducido, columns=cols_conservadas, index=X.index)
```

**En un flujo train/test (evita fuga de datos):** ajusta el selector **solo con entrenamiento** y aplícalo tal cual a prueba, sin recalcular.

```python
selector = VarianceThreshold(threshold=0.0)
selector.fit(X_train)                    # aprende que columnas quitar SOLO del train
X_train_sel = selector.transform(X_train)
X_test_sel  = selector.transform(X_test) # mismas columnas, sin volver a decidir
```

**Si vas a usar un umbral > 0, normaliza primero.** Como la varianza depende de la escala, un umbral fijo no es comparable entre columnas en unidades distintas. Escala todo al mismo rango y entonces el umbral tiene sentido:

```python
from sklearn.preprocessing import MinMaxScaler

X_scaled = MinMaxScaler().fit_transform(X)      # todo a [0, 1]
selector = VarianceThreshold(threshold=0.01)    # ahora 0.01 es comparable entre columnas
selector.fit(X_scaled)
```

**Caso especial: columnas binarias (0/1).** Aquí la varianza es `p * (1 - p)`, donde `p` es la proporción de unos. Eso permite fijar un umbral con interpretación directa: por ejemplo, para quitar columnas donde **más del 80 %** de los valores son iguales, usa `threshold = 0.8 * (1 - 0.8) = 0.16`.

```python
# elimina features binarias que son iguales en > 80% de las filas (casi constantes)
selector = VarianceThreshold(threshold=(0.8 * (1 - 0.8)))
```

Recuerda el matiz de la sección anterior: `VarianceThreshold` **solo descarta** lo que casi no varía. Lo que sobrevive sigue siendo un conjunto de candidatas que aún debes evaluar por su relación con el objetivo.

## El matiz honesto

Dos cosas para que no te quede una idea incompleta:

- La varianza solo se calcula directo sobre **números**. Para columnas de texto como `pais`, primero se convierten a códigos (por eso en el ejemplo usé `.cat.codes`), o simplemente se detectan con `nunique() <= 1` — que es más simple y funciona para cualquier tipo.
- **Varianza baja (pero no cero) no significa "inútil".** Una columna puede variar poquísimo y aun así predecir bien. El _"se elimina"_ aplica al caso extremo de varianza exactamente 0 (o casi-casi 0). Cuánto predice de verdad cada columna se mide formalmente en el **Paso 5 / Gate 4** — la varianza sola no lo dice.

## En una frase

La varianza es el promedio de las distancias al cuadrado respecto a la media; da **0** cuando todos los valores son iguales, y una columna con varianza 0 no tiene ninguna variación de la cual el modelo pueda aprender. Que la varianza sea **> 0 no la vuelve buena** por sí solo: solo la deja pasar como candidata a evaluar.
