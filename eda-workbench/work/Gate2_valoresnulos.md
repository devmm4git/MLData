# Qué hacer con los valores faltantes (nulos) de una columna

## Guía general de decisión — para cualquier campo y cualquier problema

Cuando una columna de tu dataset tiene nulos (huecos, valores faltantes), tienes tres decisiones posibles, y elegir bien depende sobre todo de **cuánto falta** y de **por qué falta**. Esta guía resume el criterio de forma general, aplicable a cualquier campo —numérico o categórico— en cualquier problema.

Las tres ideas clave:

1. **Imputar sería inventar** — rellenar solo es válido cuando falta poco.
2. **Convertir la ausencia en señal** — cuando no puedes rellenar, la ausencia misma puede ser una feature.
3. **La ausencia puede predecir el objetivo** — que un dato falte a veces carga información real.

---

## 1. Imputar: rellenar apoyándote en lo que sí tienes

**Imputar** = rellenar los huecos con un valor estimado (media, mediana, moda, o algo más elaborado) para que la columna quede completa y el modelo no falle.

Es una operación normal y necesaria… **cuando faltan pocos datos**. La clave no es el número absoluto de nulos, sino **la proporción**.

- Si falta **poco**: te apoyas en la mayoría real que sí existe para estimar la minoría faltante. Rellenas un hueco pequeño. Defendible.
- Si falta **la mayoría**: ya no estás rellenando — estás **construyendo la columna tú mismo**. Cualquier valor que pongas te lo estás inventando para la mayor parte de las filas. El modelo aprendería de tu invento, no de la realidad → basura.

> **Regla mental:** imputar es rellenar un hueco pequeño apoyándote en la mayoría que sí existe. Cuando falta la mayoría, ya no rellenas: fabricas. Y un modelo entrenado sobre datos fabricados aprende ficción.

### Guía práctica por proporción de faltantes

(Son heurísticas, no leyes; ajusta según tu caso.)

| Falta                      | ¿Imputar?           | Cómo                                                                                                     |
| -------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------- |
| < 5 %                      | Sí, casi trivial    | Rellenas con moda/mediana; el 95 %+ real manda.                                                          |
| 5–30 %                     | Sí, con cuidado     | Método razonado (mediana, moda, imputación por grupo o por modelo). Documenta el criterio.               |
| 30–50 %                    | Zona gris           | Evalúa caso por caso: ¿vale la pena la columna?, ¿hay método justificable?, ¿mejor convertirla en señal? |
| > 50 % (sobre todo > 70 %) | No imputes el valor | Imputar sería inventar la mayoría. Convierte en bandera (Sección 2) o descarta.                          |

### Cómo imputar según el tipo de dato

- **Numérica:** la **mediana** suele ser mejor que la media (es robusta a valores extremos). Aún mejor: imputar **por grupo** (p. ej. la mediana dentro de cada categoría relacionada).
- **Categórica:** la **moda** (valor más frecuente), o crear una categoría explícita **"Desconocido"** en vez de adivinar.
- **Avanzada:** KNN, MICE o un modelo predictivo, cuando la columna importa mucho y hay estructura suficiente para estimarla bien.

### Dos errores que debes evitar siempre

1. **Fuga de datos (_data leakage_):** calcula el estadístico de imputación (media, mediana, moda…) **solo con los datos de entrenamiento** y aplícalo a validación/prueba. Si lo calculas con todo el dataset antes de dividir, contaminas la evaluación.
2. **Imputar sin dejar rastro:** a veces conviene imputar el valor **y además** añadir una bandera de "faltaba" (Sección 2), para no perder la información de que ese dato originalmente no existía.

---

## 2. Convertir la ausencia en señal (bandera 0/1)

Si no puedes rellenar el valor y no quieres usarlo crudo… **no tienes que tirar la columna a la basura.** Aquí está el truco elegante.

En lugar de preguntar **"¿qué valor tenía?"** (dato que falta en gran parte de las filas), cambias la pregunta a **"¿tenía valor registrado, sí o no?"**. Y esa pregunta la puedes responder para el **100 %** de las filas, porque solo depende de si el campo está vacío o no.

Así transformas una columna muy vacía e inservible en una columna nueva, **completa y binaria**:

```python
df["tiene_<campo>"] = df["<campo>"].notna().astype(int)
# notna()      -> True si HAY dato, False si es nulo
# astype(int)  -> True = 1, False = 0
```

Resultado: una feature `tiene_<campo>` con **1** (había dato) o **0** (faltaba), **sin un solo hueco**.

> Eso es _"convertir el nulo en señal"_: dejas de ver el vacío como un problema y lo usas como información. **La ausencia del dato es el dato.**

Puedes usar esta bandera **sola** (cuando el valor es irrellenable) o **junto con la imputación** (imputas el valor y conservas la bandera para recordar que faltaba).

---

## 3. La ausencia puede predecir el objetivo

A veces el hecho de que un dato falte **no es aleatorio**: está relacionado con algo real del problema. En ese caso, la ausencia carga información sobre lo que quieres predecir, y la bandera de la Sección 2 se vuelve una feature valiosa.

### Cómo comprobarlo

Cruza la bandera `tiene_<campo>` contra tu variable objetivo y **compara el comportamiento del objetivo en los dos grupos** (con dato vs sin dato):

```python
df.groupby("tiene_<campo>")["<objetivo>"].mean()
```

Interpretación:

- **Las dos cifras se parecen** → la ausencia es prácticamente ruido (falta al azar). La bandera aporta poco.
- **Las dos cifras difieren mucho** → la ausencia es **informativa**. Saber solo si el dato faltaba ya cambia tu predicción. **No tires esa columna.**

### Ejemplo genérico de la lógica

| Grupo                 | Promedio / tasa del objetivo |
| --------------------- | ---------------------------- |
| Tiene dato (`= 1`)    | valor A                      |
| No tiene dato (`= 0`) | valor B                      |

Si **A y B son muy distintos**, la simple presencia/ausencia del dato separa poblaciones que se comportan diferente → es señal útil.

### Por qué ocurre

Muchas veces la ausencia es un **proxy** de otra característica: un segmento de clientes, un canal de captura, un nivel socioeconómico, un tipo de registro, o un proceso que solo aplica a ciertos casos. El dato falta **sistemáticamente** para cierto subgrupo, y ese subgrupo se comporta distinto respecto al objetivo.

### Matiz importante: cuidado con la redundancia

Si la bandera predice bien **porque es proxy de otra columna que ya tienes** (p. ej. un campo de "categoría" o "segmento"), puede que estés metiendo **la misma información dos veces** (colinealidad). Verifícalo midiendo la correlación entre features y conserva solo lo que aporta valor propio.

---

## Marco formal: los tres mecanismos de ausencia

Para dar rigor, la estadística clasifica _por qué_ falta un dato (tipología de Rubin):

- **MCAR** (falta completamente al azar): la ausencia no depende de nada. Imputar es seguro; la bandera aporta poco.
- **MAR** (falta al azar condicionado): la ausencia depende de **otras variables observadas**. La imputación por grupos funciona bien; la bandera puede aportar.
- **MNAR** (falta no al azar): la ausencia depende **del valor faltante mismo** o del objetivo. Aquí la ausencia es lo más informativo; la bandera es clave y la imputación simple es peligrosa (sesga).

En la práctica: si al cruzar `tiene_<campo>` con el objetivo las tasas difieren mucho, estás probablemente ante MAR o MNAR — y ahí la ausencia vale como feature.

---

## Árbol de decisión (resumen operativo)

Ante cualquier columna con nulos, pregúntate en orden:

1. **¿Qué proporción falta?**

   - Poca (≲ 30 %) → **imputa** con un método razonado (y, si quieres, añade la bandera). Fin.
   - Mucha (≳ 50 %) → no imputes el valor; pasa al punto 2.

2. **¿La ausencia es informativa?** Cruza `tiene_<campo>` con el objetivo.

   - Las tasas difieren → crea la **bandera 0/1** y úsala como feature.
   - Las tasas son iguales y la columna es irrellenable → **descártala**.

3. **¿La bandera es redundante** con otra columna que ya tienes? → revisa correlación; **conserva solo lo que aporta** información propia.

---

## Las tres ideas en una frase cada una

- **Imputar sería inventar** → rellenar la mayoría de una columna es fabricar el dato sin base real; solo es válido cuando falta poco.
- **Convertir en señal** → cambia _"¿qué valor tenía?"_ por _"¿tenía valor? (0/1)"_, que sí se responde al 100 %.
- **La ausencia predice** → si el objetivo se comporta distinto entre "con dato" y "sin dato", la ausencia es información, no basura.
