# El sesgo (_skewness_) y cuándo una variable es continua

## Qué mide el sesgo

El **sesgo** (_skewness_) mide **qué tan asimétrica es la distribución de una variable numérica**. Es decir: ¿los valores se reparten parejos a ambos lados del centro, o se amontonan de un lado con una **"cola"** larga hacia el otro?

`skew()` te devuelve **un solo número por columna**.

## Cómo se lee el número

| Valor del sesgo    | Qué significa                 | Forma                                     |
| ------------------ | ----------------------------- | ----------------------------------------- |
| **≈ 0**            | simétrica (tipo campana)      | 🔔 pareja                                 |
| **> 0** (positivo) | cola larga a la **derecha**   | mayoría de valores bajos, pocos muy altos |
| **< 0** (negativo) | cola larga a la **izquierda** | mayoría de valores altos, pocos muy bajos |

**Regla práctica de magnitud** (aproximada):

- `|skew| < 0.5` → casi simétrica → **no hay que hacer nada**.
- `0.5 – 1` → sesgo **moderado**.
- `> 1` → sesgo **fuerte** → **candidata a transformación**.

### El truco visual para "ver" el sesgo

Si la graficas (histograma + KDE), la relación entre la **media** y la **mediana** te delata la forma:

- **Sesgo positivo** (cola a la derecha): la **media** queda a la **derecha** de la mediana (los pocos valores altos jalan el promedio hacia arriba).
- **Casi simétrica**: media y mediana casi encimadas.
- **Sesgo negativo** (cola a la izquierda): la media queda a la **izquierda** de la mediana.

La **cola larga** hacia un lado es la firma visual del sesgo.

## Para qué sirve en el EDA

Dos cosas:

1. **Decide si conviene una transformación (log).** Muchos modelos y métricas asumen distribuciones más o menos simétricas. Una variable muy sesgada (un precio, donde casi todos pagan poco y unos pocos pagan carísimo) puede distorsionar el modelo. Aplicarle `log` la **"comprime"** y la vuelve más simétrica. El sesgo es el número que te dice si vale la pena esa transformación.
2. **Te anticipa la forma antes de graficar.** Es el complemento numérico del histograma: `skew()` te da el número; el histograma te da la imagen.

> **Alcance:** en esta etapa solo **medimos y anotamos** el sesgo (para el plan). La transformación en sí es **preparación de datos** (post-EDA), igual que la imputación.

```python
from scipy.stats import skew

# sesgo de las numericas continuas (las que podrian necesitar log)
for col in columnas_numericas_continuas:
    s = skew(df[col].dropna())          # dropna(): skew no admite nulos
    print(f"{col:12} sesgo = {s:.2f}")
```

## ¿A qué variables se les calcula el sesgo?

**Solo a las numéricas continuas** (o casi continuas). El sesgo mide la **forma de una distribución sobre una escala numérica**, así que solo tiene sentido donde los valores representan una **cantidad medible en un continuo**.

El criterio es el **tipo de variable**, no directamente la cardinalidad:

| Tipo de columna                                           | ¿Calcular sesgo? | Por qué                                                                           |
| --------------------------------------------------------- | ---------------- | --------------------------------------------------------------------------------- |
| Numérica **continua** (precio, edad, peso)                | ✅ sí            | tiene forma/cola que medir                                                        |
| **Entera discreta** (conteos: nº de hijos, nº de pedidos) | ⚠️ se puede      | el sesgo se calcula, pero se interpreta con cuidado (son conteos, no un continuo) |
| Categórica **ordinal** (niveles 1/2/3)                    | ❌ no            | el "sesgo" de 3 valores no dice nada útil                                         |
| Categórica de **texto**                                   | ❌ no            | ni siquiera son números                                                           |
| **Target binario** (0/1)                                  | ❌ no            | su "balance" se mide aparte, no con skew                                          |
| **ID** / **texto libre**                                  | ❌ no            | su distribución no significa nada                                                 |

**La conexión con la cardinalidad** (que a veces se intuye): sí existe, pero es **indirecta**. Las continuas tienden a tener cardinalidad alta _porque_ son continuas. Pero no todas las de cardinalidad alta llevan sesgo (un campo de nombres tiene cardinalidad altísima y no tiene sesgo: es texto), y no todas las de cardinalidad baja se excluyen (un conteo de baja cardinalidad sí admite el cálculo). Por eso la regla correcta es **por tipo (continua) → sí**; la cardinalidad no es el criterio directo.

## ¿Cómo sé si una variable numérica es continua o discreta?

Este concepto base decide qué análisis aplica a cada columna.

### La definición

- **Continua** = puede tomar **cualquier valor dentro de un rango**, incluyendo decimales/fracciones. Entre dos valores siempre cabe otro. **Mides** sobre una escala sin "escalones".
  _Ejemplos:_ peso (70.4 kg), temperatura (36.6 °C), precio (7.25), edad exacta (0.42 años).
- **Discreta** = solo toma valores **contables y separados**, normalmente enteros, sin nada intermedio. **Cuentas** unidades, no mides.
  _Ejemplos:_ número de hijos (0, 1, 2… nunca 2.5), número de hermanos, cantidad de puertas de un coche.

### La prueba mental más simple

**¿Tiene sentido un valor con decimales?**

- _"2.5 hijos"_ → no tiene sentido → **discreta**.
- _"36.6 grados"_ → sí tiene sentido → **continua**.

### Dos pistas prácticas para reconocerlas

1. **El `dtype`:** una columna `float64` suele ser **continua** (los decimales delatan la medición); una `int64` suele ser **discreta**. No es ley absoluta, pero es un buen primer indicio.
2. **Cardinalidad + sentido:** muchos valores distintos y con decimales → continua; pocos valores enteros contables → discreta. (Aquí se conecta con lo anterior: las continuas tienden a tener cardinalidad alta porque admiten infinitos valores intermedios.)

Un código para verlo de un vistazo:

```python
for col in columnas_numericas:
    tiene_decimales = (df[col].dropna() % 1 != 0).any()   # ¿algún valor NO entero?
    print(f"{col:12} dtype={str(df[col].dtype):8} unicos={df[col].nunique():3}  "
          f"{'CONTINUA (tiene decimales)' if tiene_decimales else 'discreta (solo enteros)'}")
```

`(x % 1 != 0)` pregunta _"¿el residuo de dividir entre 1 es distinto de cero?"_ — o sea, _"¿hay decimales?"_.

### El matiz honesto (la frontera es borrosa)

- **La distinción no siempre es tajante.** Un conteo entero (nº de hermanos) es técnicamente discreto, pero como es numérico y ordenado, para algunos análisis se trata **como si** fuera continuo (por eso el sesgo en conteos va "con matiz"). No es pecado; solo hay que saber que es un conteo.
- **Lo importante no es la etiqueta, sino qué análisis habilita:**

  - **Continuas** → histograma, KDE, sesgo, boxplot, escalado, transformación log.
  - **Discretas de pocas categorías** → se pueden tratar como categóricas (`value_counts`, one-hot).

  El sesgo y el log tienen sentido pleno en las continuas porque miden la forma de una **curva suave**. En una discreta de pocos valores, la "curva" es más bien un **conteo de barras**.

## Cómo interpretarlo y qué acción tomar

Una lectura intuitiva común es: _"cuando la distribución es más simétrica, distorsiona menos a los modelos; cuando no es simétrica, distorsiona más."_ Es **correcta en la dirección**, pero con un **matiz enorme que lo cambia todo: depende del tipo de modelo.** No es _"simétrico = bueno para todos"_, sino _"simétrico = importa para algunos modelos, y para otros da igual"_.

| Familia de modelo                              | ¿Le molesta el sesgo? | ¿Necesita transformación log? |
| ---------------------------------------------- | --------------------- | ----------------------------- |
| **Lineales** (regresión lineal / logística)    | Sí, mucho             | Sí, ayuda                     |
| **Basados en distancias** (KNN, SVM)           | Sí                    | Sí, ayuda                     |
| **Árboles** (Random Forest, XGBoost, LightGBM) | No, les da igual      | No la necesitan               |

- **Por qué a los lineales sí les molesta:** un modelo lineal traza una relación tipo "recta". Si una variable está muy sesgada, los pocos valores extremos de la cola **jalan la recta** de forma desproporcionada — el modelo se obsesiona con esos pocos puntos y ajusta peor la mayoría. Al aplicar `log`, comprimes la cola, la relación se vuelve más "recta", y el modelo la aprovecha mejor. **Ahí la intuición es 100 % correcta.**
- **Por qué a los árboles les da igual:** un árbol no traza rectas, hace **cortes** (_"¿valor > X? sí/no"_). Un corte funciona igual esté sesgada o no la variable — lo único que importa es el **orden** de los valores, y `log` **no cambia el orden**. Por eso a un Random Forest le das la variable cruda o transformada y da el **mismo resultado**; transformarla sería trabajo inútil.

### La consecuencia práctica

El sesgo **no dispara una acción automática**. Dispara una **acción condicional**:

> **SI** al final eliges un modelo lineal (o basado en distancias), **ENTONCES** transformas las variables muy sesgadas.

Por eso en el EDA **solo medimos y anotamos**, no transformamos nada. Lo dejamos como una nota del tipo: _"variable X tiene sesgo ~4.8 → candidata a log si se usa un modelo lineal."_ La decisión final espera a saber qué modelo se usará.

La transformación típica es `log1p` (que es `log(1 + x)`), porque funciona aunque haya ceros:

```python
import numpy as np
x_log = np.log1p(df["<columna>"])   # log1p = log(1+x): sirve aunque haya valores = 0
# una variable con sesgo ~4.8 puede bajar a ~0.4 tras el log -> casi campana
```

## En una frase

El **sesgo** es un número que mide la asimetría de una variable **numérica continua**: `≈ 0` es simétrica, `> 0` tiene cola a la derecha y `< 0` a la izquierda. Un sesgo fuerte (`> 1`) la vuelve **candidata a transformación log**, pero esa es una **acción condicional al modelo**: ayuda a los lineales y a los de distancias, y a los árboles les da igual.
