# Gate 3 — La etiqueta (_ground truth_) y el tipo de target

## Qué verifica el Gate 3, en una frase

Que tienes la **"respuesta correcta"** (el _ground truth_) para poder aprender de ella, y que sabes **de qué tipo es**, porque eso define todo lo que sigue.

Un modelo supervisado aprende de **ejemplos etiquetados**: le muestras casos donde ya sabes el resultado y aprende el patrón. Sin esas etiquetas, o con etiquetas de mala calidad, **no hay nada que aprender** — por muy bueno que sea el dato de entrada.

> **El Gate 3 hace dos preguntas:** > **A.** ¿Sé, para cada caso del pasado, cuál fue el desenlace real? _(¿existe y es confiable la etiqueta?)_ > **B.** ¿De qué tipo es ese desenlace? _(¿binario/categórico o continuo? → define clasificación vs regresión)_

---

## Paso A — ¿Existe la etiqueta y es confiable?

Hay dos escenarios, y la diferencia entre ellos es lo que hace al Gate 3 trivial o mortal.

**Etiqueta que viene dada.** _(ej. tabular: `Survived` = 0/1)_
Ya está en el dataset. Para cada caso histórico sabes el resultado. Riesgo casi nulo → **GO fácil**.

**Etiqueta que hay que reconstruir.** _(ej. mantenimiento: telemetría + órdenes de trabajo)_
No viene regalada. Hay que **construirla** cruzando fuentes: la telemetría del sensor (los inputs) con el registro de fallas / CMMS (cuándo se rompió algo). Ese cruce te dice _"en esta fecha falló"_ → y con eso etiquetas: _"las horas antes = pre-falla; el resto = sano"_.

### El contraste clave

|                     | Etiqueta dada (tabular) | Etiqueta reconstruida (planta)         |
| ------------------- | ----------------------- | -------------------------------------- |
| **¿Existe ya?**     | Sí, es una columna      | No — hay que reconstruirla             |
| **¿De dónde sale?** | viene en el dataset     | del cruce de varias fuentes            |
| **Riesgo típico**   | casi ninguno            | que nadie haya registrado el desenlace |
| **Veredicto usual** | GO fácil                | CONDITIONAL o NO-GO                    |

> **El asesino silencioso:** hay toneladas de datos de entrada (telemetría en vivo) pero **nadie apuntó cuándo pasó el evento**. Sin ese registro no puedes etiquetar → no puedes entrenar. **El dato de entrada es inútil sin la respuesta.**

---

## Paso B — ¿De qué tipo es el target?

Antes de medir nada, ubica el target en el mapa de tipos, porque de ahí depende si haces **clasificación** o **regresión**.

```
VARIABLE
├── NUMÉRICA (números que miden/cuentan cantidad)
│    ├── continua  → cualquier valor, con decimales   (edad exacta, precio)
│    └── discreta  → enteros contables, separados      (nº de hijos, nº de pedidos)
│
└── CATEGÓRICA (etiquetas, no cantidades)
     ├── binaria   → exactamente 2 categorías          (sobrevivió sí/no, sexo)
     ├── nominal   → varias categorías SIN orden        (país, color)
     └── ordinal   → varias categorías CON orden        (nivel bajo/medio/alto)
```

### Continuo vs binario (son opuestos, no uno dentro del otro)

Una duda muy común es _"¿lo continuo incluye lo binario?"_. **No** — viven en familias distintas:

- **Continuo** = variable **numérica** que puede tomar **infinitos valores** en un rango, con decimales. Mides una **cantidad** en una escala sin escalones. Entre 22 y 23 existen 22.4, 22.7, 22.999…
- **Binario** = variable **categórica** con **exactamente 2 valores**, que son **etiquetas, no cantidades**. El `0` y el `1` son códigos para _"No"_ y _"Sí"_; no existe el _"0.5 sobrevivido"_, no hay nada entre medias.

|                               | Continuo                     | Binario                                    |
| ----------------------------- | ---------------------------- | ------------------------------------------ |
| **¿Cuántos valores?**         | infinitos (en un rango)      | exactamente 2                              |
| **¿Hay valores intermedios?** | sí (22.5, 22.7…)             | no (solo 0 o 1)                            |
| **¿El número mide cantidad?** | sí (38 > 22 significa "más") | no (1 no es "más" que 0, es otra etiqueta) |
| **Se trata de…**              | **cuánto** (magnitud)        | **cuál** (categoría)                       |

> **Truco para no confundirte:** aunque un binario se escriba con números (0 y 1), **no es numérico**. Son disfraces de "No" / "Sí". Si en vez de `0/1` dijera `"muerto"/"vivo"`, verías clarísimo que es una **categoría**. Los `0/1` son solo por comodidad de cómputo.

### Por qué el tipo del target lo decide todo

| Si el target es…         | El problema es…   | Métrica típica       | Qué le aplicas al target                  |
| ------------------------ | ----------------- | -------------------- | ----------------------------------------- |
| **binario / categórico** | **clasificación** | accuracy, F1, recall | `value_counts()` → **balance de clases**  |
| **continuo**             | **regresión**     | RMSE, MAE            | `describe()`, histograma, KDE → **forma** |

La razón: `hist`/`kde`/`describe` sirven para estudiar **la forma de una distribución continua**. En un target binario de 2 valores **no hay "forma" que estudiar**, solo 2 barras → lo único que se mide es el **balance** entre ellas. (Es el mismo principio del sesgo: continuo y binario son mundos distintos.)

---

## Los 4 chequeos cuantitativos del Gate 3

| Chequeo                        | Qué preguntas                               | Nota                                                                |
| ------------------------------ | ------------------------------------------- | ------------------------------------------------------------------- |
| **# de eventos etiquetados**   | ¿cuántos casos con desenlace conocido hay?  | pocos casos = problema, sea cual sea el tipo                        |
| **% con timestamp válido**     | ¿los eventos están bien fechados?           | solo aplica a problemas **temporales**; N/A en una foto estática    |
| **Balance de clases**          | ¿cuántos de cada clase (ej. 50/50 vs 95/5)? | solo para **clasificación**; es el corazón del Paso 4 (Target)      |
| **¿Target capado / truncado?** | ¿tiene un tope artificial o valores raros?  | ej. un RUL truncado, o un binario que traiga valores fuera de {0,1} |

El **balance** no cambia _si tienes_ etiqueta, sino **qué tan difícil será el problema y qué métrica usar** — y eso conecta con el **Gate 0** (costo de falsos negativos vs falsos positivos): un 95/5 con FN caros exige mirar _recall_, no _accuracy_.

---

## Cómo se decide el veredicto

- **GO** → la etiqueta viene dada, está **completa** (0 o casi 0 nulos), su **dominio es limpio** (ej. exactamente `{0,1}`), y el balance es manejable. Sabes si es clasificación o regresión.
- **CONDITIONAL** → la etiqueta **se puede reconstruir** pero cuesta trabajo, o hay algunos nulos/valores raros en el target, o el balance es tan extremo que exige una estrategia especial (remuestreo, métrica adecuada, umbral).
- **NO-GO** → **no hay forma de etiquetar**: nadie registró los desenlaces, o la etiqueta es tan incompleta/poco confiable que no se puede confiar en ella. Aquí se para: sin respuesta correcta no hay modelo.

### Checklist rápido

- [ ] ¿Existe una etiqueta para cada caso del pasado? _(dada o reconstruible)_
- [ ] ¿Está completa? _(nulos en el target)_
- [ ] ¿Su dominio es limpio? _(sin valores fuera de lo esperado / sin capping raro)_
- [ ] ¿Es binaria/categórica o continua? → **clasificación** o **regresión**
- [ ] Si es clasificación: ¿cuál es el **balance** de clases?
- [ ] Si es temporal: ¿los eventos tienen **timestamp válido**?

---

## En una frase

El Gate 3 confirma que existe una etiqueta **completa, limpia y confiable** para cada caso del pasado y que sabes **de qué tipo es**: si viene dada en el dataset es un GO casi automático, si hay que reconstruirla ahí vive el riesgo real, y su tipo —**binario/categórico → clasificación**, **continuo → regresión**— decide qué mides, qué métrica usas y todo lo que sigue.
