# Detectar _capping_ (topes artificiales) en una columna

## Qué es el capping

**Capping** es cuando una variable tiene un **tope artificial**: todos los valores más allá de cierto límite se aplastan en un mismo punto de borde (o en un código), en vez de conservar su valor real. Puede pasar en el extremo superior (un techo, sobre el `max`) o en el inferior (un piso, sobre el `min`).

La huella es siempre la misma: **muchos registros amontonados exactamente en el valor del borde**, como si hubiera un muro. Ejemplos generales:

- Una edad que aparece como `90+` (todas las edades mayores colapsadas en 90).
- Un precio o salario capturado como `"$500,000 o más"`.
- Una temperatura que nunca pasa de `50` porque el sensor no mide más.

## ¿Quién lo hizo? Capping de la fuente vs. capping tuyo

La pregunta central es **quién lo hizo**. Casi siempre viene **ya en la fuente de datos** — no es algo que tú provoques sin querer con una función. Se hace de forma deliberada, antes de que el dataset llegue a tus manos. Conviene separar dos naturalezas muy distintas:

|               | Capping en la fuente                        | Capping que **tú** haces                     |
| ------------- | ------------------------------------------- | -------------------------------------------- |
| **Quién**     | Quien publicó los datos                     | Tú, con una función (`.clip()`)              |
| **Cuándo**    | Antes de que lleguen a ti                   | En la preparación de datos (post-EDA)        |
| **Por qué**   | Privacidad, instrumento, regla de negocio   | Domar outliers para que no dominen el modelo |
| **En el EDA** | Lo **detectas** (es un problema a entender) | Aún **no** lo aplicas                        |

El que cazas durante el EDA es el **de la fuente** — el que ya venía. Es un problema de calidad que hay que conocer, porque significa que tu variable tiene un tope falso y el modelo aprenderá ese muro como si fuera real.

El que tú harías más adelante (con `.clip()` en pandas) es una **técnica de tratamiento de outliers**, intencional y controlada por ti. Son la misma operación mecánica, pero con dueño, momento y motivo opuestos.

### Las tres causas típicas del capping de la fuente

1. **Privacidad / anonimización.** La más común. Quien publica los datos agrupa los extremos a propósito para que no se pueda identificar a nadie. Ejemplo: un censo reporta las edades muy altas como `90+`, porque una persona de 108 años en un pueblo chico sería identificable.
2. **Límite del instrumento de medición.** Un sensor que solo mide hasta cierto punto. Un termómetro que llega a 50 °C reporta como `50` todo lo que sea más caliente, porque no puede medir más. El tope es físico, del aparato.
3. **Regla de captura / negocio.** El sistema que capturó el dato tenía una regla. Un formulario donde el ingreso máximo seleccionable es `"$500,000 o más"`: todos los que ganan más quedan en esa categoría.

En los tres casos el recorte ya venía hecho cuando recibiste el archivo. Tú no lo provocas — tú lo **detectas** para que no engañe a tu modelo.

## Por qué importa detectarlo

Si una columna tiene capping de la fuente y no lo notas:

- El modelo cree que existe un **"muro" real** en ese valor y aprende un patrón falso.
- Las **estadísticas se distorsionan** (la media, la desviación, la correlación con el objetivo).
- Peor aún: si el tope concentra una fracción grande de los datos en un solo punto, el modelo puede **sobreajustarse a ese pico artificial**.

## Cómo detectarlo (el método general)

Se detecta **combinando dos vistas**: una te dice _dónde_ está el borde y la otra _cuántos_ hay amontonados ahí.

### 1. `describe()` — localiza el borde

```python
df["<columna>"].describe()
```

Mira el `min` y el `max`: son los candidatos a tope. Un extremo "redondo" o sospechosamente limpio (`90`, `50`, `500000`, `-1`) ya levanta la ceja.

### 2. `value_counts()` — cuenta cuántos se amontonan en el borde

```python
df["<columna>"].value_counts().sort_index()   # ordena por valor para ver los extremos
```

Fíjate en la frecuencia **justo en el valor máximo (o mínimo)**. Si un solo valor de borde acumula una porción anormalmente alta del total, esa es la firma del recorte.

### La señal / la huella

> **La huella del capping:** un **pico de frecuencia anormalmente alto justo en el valor del borde** (el máximo o el mínimo). Los datos reales rara vez se apilan de golpe en un único punto extremo; cuando lo hacen, es porque algo los empujó ahí.

Un chequeo cuantitativo útil es ver **qué proporción del total cae en el extremo**:

```python
tope = df["<columna>"].max()
frac = (df["<columna>"] == tope).mean()
print(f"{frac:.1%} de los registros están exactamente en {tope}")
```

Si ese porcentaje es llamativamente grande (no un puñado de filas, sino un bloque), es capping, no azar.

### Capping vs. outlier normal

La distinción clave está en **cuántos** hay en el extremo:

- **Muchos** registros pegados al mismo valor máximo/mínimo → **capping** (tope artificial).
- **Pocos** valores extremos, dispersos y distintos entre sí → **outliers normales** (colas de la distribución).

Por eso `describe()` solo no basta: te muestra el borde, pero no cuántos hay ahí. `value_counts()` es quien resuelve la duda.

## Los dos usos de `value_counts()`

`value_counts()` sirve para **dos revisiones distintas**, y conviene tener claro en cuál estás. Es la misma función, pero mirada con dos intenciones opuestas: en una te interesan los **extremos numéricos**; en la otra, la **lista completa de categorías** y sus conteos.

| Uso                                | Qué revisa                                     | Sobre qué columnas               |
| ---------------------------------- | ---------------------------------------------- | -------------------------------- |
| **Uso 1 — Capping**                | ¿hay un pico artificial en el borde (mín/máx)? | numéricas continuas              |
| **Uso 2 — Higiene de categóricas** | ¿typos, espacios, categorías raras?            | categóricas de baja cardinalidad |

Todo lo anterior de este documento es el **Uso 1**. El **Uso 2** es el complemento natural del Gate 2, y va aquí.

### Uso 2 — Higiene de categóricas: qué revisa

Aquí `value_counts()` te lista cada categoría con su frecuencia, y esa lista delata los problemas de calidad típicos de las columnas categóricas / de texto:

- **Typos y variantes de escritura.** El mismo valor escrito de formas distintas se cuenta como categorías separadas: `"México"`, `"Mexico"`, `"mexico"` salen en tres líneas cuando deberían ser una. Un conteo alto en una y conteos de 2–3 en las variantes es la pista.
- **Espacios y mayúsculas invisibles.** `"activo"` y `"activo "` (con espacio al final), o `"Sí"` y `"SÍ"`, se ven idénticos a simple vista pero son líneas distintas en el censo. Son la causa #1 de categorías duplicadas.
- **Categorías raras o inesperadas.** Un valor que aparece 2 veces cuando esperabas solo un conjunto conocido → posible error de captura, o una categoría legítima pero tan rara que habrá que agrupar.
- **Cardinalidad que no cuadra.** Esperabas _N_ categorías y salen _N + 3_: las tres de más suelen ser typos o basura.

Cómo se lee: revisa la **cola** de la lista (los conteos más chicos), que es donde se esconden las variantes:

```python
df["<categorica>"].value_counts(dropna=False)   # dropna=False muestra tambien los nulos
```

Arreglos generales una vez detectados: normalizar espacios y mayúsculas (`.str.strip()`, `.str.lower()`), mapear sinónimos a un valor único, y agrupar las categorías muy raras en un `"Otros"`.

> **Regla:** si una columna es categórica de baja cardinalidad y sus valores "limpios" caben en una lista corta, `value_counts()` debe devolver **exactamente** esa lista. Cualquier línea de más es un problema de higiene.

## A qué columnas aplicar `value_counts()`

`value_counts()` sirve donde **los valores se repiten**. Si cada valor es casi único, te devuelve cientos de líneas con conteo `1` — ruido puro, cero información. La regla general:

- **Para higiene (typos, categorías raras)** → categóricas de **baja cardinalidad** (sexo, país, categoría, nivel, conteos pequeños). Ahí se esconden los errores de escritura y las categorías extrañas.
- **Para chequeo de capping** → numéricas **continuas** (edad, precio, temperatura, ingreso), mirando si hay un pico en el borde.
- **Nunca** → identificadores ni texto libre (nombres, folios, tickets, IDs). Cada valor es único; el "censo" no aporta nada.

## Qué hacer cuando lo detectas

En el **EDA solo lo documentas**: anotas que la variable tiene un tope artificial y qué fracción de datos está en el borde. El tratamiento viene después, y depende de la causa:

- Si el tope es un **código centinela** (`-1`, `999`) → conviértelo a nulo y trátalo como dato faltante.
- Si es un **agrupamiento real de la fuente** (`90+`, `"$500k o más"`) → decides si lo dejas como está, lo modelas como categoría de borde, o creas una bandera `es_tope` para que el modelo sepa que ese valor es especial.
- El capping **que tú aplicas** a outliers (`.clip()`) es otra decisión distinta, del Paso de preparación, no del EDA.

## En una frase

El capping es un tope artificial en una columna; se detecta combinando `describe()` (dónde está el borde) con `value_counts()` (cuántos hay amontonados ahí): **muchos registros pegados al máximo/mínimo = capping; pocos y dispersos = outliers normales.**
