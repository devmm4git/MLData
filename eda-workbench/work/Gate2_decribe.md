# `df.describe()` como detector de valores imposibles

## Qué hace, por dentro

`df.describe()` calcula, **solo para las columnas numéricas**, un resumen estadístico de cada una:

| Estadístico           | Qué es                                                                           |
| --------------------- | -------------------------------------------------------------------------------- |
| `count`               | cuántos valores no nulos hay                                                     |
| `mean`                | promedio                                                                         |
| `std`                 | desviación estándar (qué tan dispersos están — la raíz de la varianza que vimos) |
| `min`                 | el valor más chico                                                               |
| `25%` / `50%` / `75%` | percentiles (el 50 % es la mediana)                                              |
| `max`                 | el valor más grande                                                              |

## Para qué sirve en el Gate 2

El objetivo aquí **no** es estudiar la distribución (eso es el Paso 3), sino usar **`min` y `max` como detector de valores imposibles o centinela**.

La idea:

`min` y `max` son los **extremos** → si hay un valor absurdo, aparece ahí. Una edad de `-5` o `999`, un precio negativo, una temperatura de `-999` (que en realidad es el código de _"sin lectura"_ del sensor)… todos se delatan en el `min` / `max`.

> **El truco mental:** lee cada `min` y cada `max` y pregúntate _"¿esto es físicamente posible?"_. Si no lo es, es un **error de dato** o un **centinela** disfrazado de número.

### Cómo leerlo en la práctica

```python
df.describe()
```

Recorre la fila `min` y la fila `max` columna por columna y contrástalas con lo que sabes del mundo real:

- **`min` sospechoso** → valores por debajo de lo posible: edades negativas, cantidades o precios en negativo, conteos negativos, ceros donde el cero no tiene sentido.
- **`max` sospechoso** → topes artificiales o códigos centinela: `999`, `9999`, `-999`, `-1`, fechas al año 1900 o 2099, números redondos gigantes que "marcan" un dato faltante.

### Qué es un valor centinela

Un **centinela** es un número real que en realidad significa _"no hay dato"_. En vez de dejar un nulo, algún sistema o sensor rellenó con un valor bandera (`-999`, `9999`, `0`, `-1`). El problema es que **el modelo lo lee como número de verdad** y aprende basura. Por eso hay que cazarlos aquí: no se ven como nulos, pero lo son.

Una vez detectado, el arreglo típico es convertirlo de vuelta a nulo para tratarlo como corresponde:

```python
# ejemplo: -999 es el codigo de "sin lectura" -> convertir a NaN
import numpy as np
df["temperatura"] = df["temperatura"].replace(-999, np.nan)
```

## En una frase

`df.describe()` resume cada columna numérica; en el Gate 2 solo te interesan `min` y `max`, porque son la ventana donde se asoman los valores imposibles y los centinelas disfrazados de número.
