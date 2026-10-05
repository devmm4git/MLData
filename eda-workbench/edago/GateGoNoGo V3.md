# Capa de Decisión: Go / Go-Conditional / No-Go para Modelado Predictivo

> **Complemento de `EDAGuiaGlobal.md`.**
> La guía de EDA *describe* cómo se comportan los datos. Esta capa *decide* si esos datos
> alcanzan para arriesgar el entrenamiento de un modelo. El EDA alimenta al gate con
> evidencia; el gate convierte la evidencia en una decisión defendible.
> **General**: aplica a cualquier proyecto de mantenimiento predictivo / ML sobre telemetría,
> no a un dataset concreto.

---

## Marcos de referencia (el fundamento)

Este gate no es una invención ad-hoc: cada compuerta se apoya en un marco publicado y establecido.
Los tres, en el orden en que "entran" en un proyecto:

### 1. CRISP-DM — el proceso que envuelve todo

*Cross-Industry Standard Process for Data Mining.* Estándar de facto de proyectos de datos desde hace
~25 años. Define seis fases cíclicas:

`Business Understanding → Data Understanding → Data Preparation → Modeling → Evaluation → Deployment`

- La fase **Data Understanding** (recolectar, describir, explorar, verificar calidad) es, en esencia,
  lo que hace tu `EDAGuiaGlobal.md`.
- La fase **Business Understanding** es lo que este gate añade *antes* del dato: sin una decisión de
  negocio definida, ningún dato está "listo".

**Qué aporta al gate:** el encuadre (Gate 0) y el orden — negocio antes que dato, evaluación antes que
despliegue.
**Referencia:** Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* SPSS Inc.

### 2. Data Readiness Levels (DRL) — ¿está el dato listo?

Propuesto por **Neil D. Lawrence (2017)** por analogía con los *Technology Readiness Levels* de la NASA.
Da un lenguaje común para hablar de la madurez del dato, en tres bandas (de peor a mejor):

| Banda | Nombre | Pregunta |
|---|---|---|
| **C** | Accesibilidad | ¿Existe y puedo cargarlo en formato digital usable? (nivel más bajo C-4 = "me dijeron que hay datos" / *hearsay*) |
| **B** | Validez | ¿El dato es fiel a lo que dice ser? ¿Entiendo nulos, ruido, representatividad? |
| **A** | Utilidad en contexto | ¿Está listo para *esta* pregunta específica? |

Idea central: la prontitud es **relativa a la tarea** — el mismo dato puede ser A-listo para una
pregunta y no para otra. Y subir de banda **cuesta trabajo real** (suele ser lo que hunde el cronograma).

**Qué aporta al gate:** el lenguaje de las compuertas de dato — accesibilidad (Gate 1 ← Banda C),
validez (Gate 2 ← Banda B) y dato-en-contexto-de-tarea (Gate 3 ← Banda A).
**Referencia:** Lawrence, N. D. (2017). *Data Readiness Levels.* arXiv:1705.02245 — https://arxiv.org/abs/1705.02245

### 3. Métricas PHM — ¿hay señal, y hasta cuándo se puede predecir?

Del campo *Prognostics and Health Management*. Dos familias, de dos fuentes:

- **Selección de features (antes de modelar) — Coble (2010).** Tres métricas que rankean qué tan útil es
  cada sensor para prognosis: **monotonicity** (¿tiene tendencia consistente a lo largo de la vida?),
  **trendability** (¿se comporta igual entre unidades?) y **prognosability** (¿el valor en el momento de
  falla está agrupado en la población?). Convierten "elegir los 8 sensores" en un número, no en un ojímetro.
- **Evaluación de predicciones (después de modelar) — Saxena et al. (2008).** Miden qué tan buenas son
  las predicciones de RUL; la principal es el **Prognostic Horizon** — cuánto antes de la falla el modelo
  predice dentro de una banda de error aceptable. Es la formalización de *"hasta cuándo se puede predecir"*
  y el porqué de que el horizonte se **mida**, no se fije en 48h.

**Qué aporta al gate:** el contenido de señal (Gate 4 ← Coble) y el horizonte alcanzable (Gate 5 ← Saxena).
**Referencias:**
- Coble, J. (2010). *Merging Data Sources to Predict Remaining Useful Life — An Automated Method to Identify Prognostic Parameters.* Tesis doctoral, University of Tennessee, Knoxville.
- Saxena, A., Celaya, J., Balaban, E., Saha, B., Saha, S., Goebel, K. (2008). *Metrics for evaluating performance of prognostic techniques.* Int. Conf. on Prognostics and Health Management (PHM08), NASA Ames Research Center.

### Crosswalk marco → compuerta

| Marco | Qué aporta | Compuertas |
|---|---|---|
| CRISP-DM | Negocio antes que dato; proceso completo | Gate 0 |
| Data Readiness Levels (C/B/A) | Madurez del dato relativa a la tarea | Gates 1, 2, 3 |
| Métricas PHM (Coble / Saxena) | Ranking de señal + horizonte pronóstico | Gates 4, 5 |

*(Gates 6–8 — suficiencia poblacional, validez de evaluación y desplegabilidad — se apoyan en práctica
estándar de ML/MLOps más que en un solo marco citado.)*

---

## Cómo se usa

- Se corre **al terminar el EDA** (después del Paso 8 de `EDAGuiaGlobal.md`), *antes* de comprometer
  tiempo de entrenamiento.
- Son **9 compuertas** (Gate 0–8). Cada una produce un veredicto: **GO / CONDITIONAL / NO-GO**.
- **Regla del eslabón más débil:** el veredicto global = **la peor** de las 9 compuertas.
  Un solo NO-GO hace el proyecto NO-GO. Un CONDITIONAL sin GO por debajo hace el proyecto
  CONDITIONAL.
- **CONDITIONAL** no es "tal vez": es **GO con una condición nombrada, un dueño y un plazo**.
  Si la condición no se cumple en el plazo, degrada a NO-GO.
- Cada compuerta indica **cómo se mide** (mapeada al paso del EDA que produce la evidencia).

---

## Las 9 compuertas

### Gate 0 — Encuadre de negocio
*(CRISP-DM Business Understanding)*
**Pregunta:** ¿Existe una decisión concreta que el modelo informa, y una acción que dispara?
**Cómo se mide:** conversación con el dueño del proceso, no datos. Define: decisión, acción, dueño,
y **asimetría de costo** (¿cuánto cuesta un falso negativo vs. un falso positivo?).

- **GO** — decisión + acción + dueño + costo FN/FP conocidos.
- **CONDITIONAL** — decisión clara pero costos aún no cuantificados.
- **NO-GO** — "queremos usar IA" sin decisión ni acción definida. (Ningún dato salva esto.)

---

### Gate 1 — Accesibilidad y flujo del dato
*(DRL Banda C)*
**Pregunta:** ¿Puedo obtener el dato, de forma **durable** y automatizada, a la frecuencia necesaria,
hacia adelante (no un export único)?
**Cómo se mide:** EDA Paso 0 (ingesta). ¿Hay pipeline desde la fuente (PLC/robot/sensor) al almacenamiento?

- **GO** — pipeline durable, automatizado, reproducible, a la frecuencia mínima requerida.
- **CONDITIONAL** — datos accesibles pero por **export manual / one-off**.
- **NO-GO** — dato atrapado en el equipo sin salida, o no capturable a la frecuencia mínima.

---

### Gate 2 — Validez y calidad
*(DRL Banda B, EDA Paso 2)*
**Pregunta:** ¿El dato es fiel a la realidad?
**Cómo se mide:** EDA Paso 2. Nulos/dropouts, valores imposibles, integridad de timestamps,
unidades consistentes, deriva/descalibración de sensor.

- **GO** — nulos caracterizados y acotados, sin valores imposibles sin explicar, timestamps consistentes,
  calibración verificada.
- **CONDITIONAL** — problemas conocidos y acotados, con plan de limpieza definido.
- **NO-GO** — dropouts masivos no caracterizados, timestamps rotos, o deriva de sensor no corregible.

---

### Gate 3 — Integridad de la etiqueta / target
*(DRL Banda A — el dato en contexto de la tarea)*
**Pregunta:** ¿Tengo ground truth? ¿Sé **cuándo** falló cada activo, con precisión suficiente?
**Cómo se mide:** EDA Paso 4 (target). Historial de fallas fechado, modo de falla identificado,
target construible (RUL, "falla en N horas", clase pre-falla).

- **GO** — eventos de falla registrados y fechados; modo de falla identificado; target construible.
- **CONDITIONAL** — historial parcial o reconstruible desde CMMS / órdenes de trabajo / alarmas.
- **NO-GO** — sin ground truth de fallas. **En planta, este suele ser el asesino silencioso:**
  hay telemetría en vivo pero nadie registró cuándo falló nada.

---

### Gate 4 — Contenido de señal pronóstica
*(Métricas PHM — Coble; EDA Pasos 3, 5, 6)*
**Pregunta:** ¿Existe una señal de degradación **detectable** en los sensores?
**Cómo se mide:** EDA Paso 6 (temporal) + ranking con las métricas de Coble (ver abajo). Se calcula
**monotonicity, trendability y prognosability** por feature.

- **GO** — una o más features con monotonicity y trendability altas y prognosability razonable;
  señal separable del ruido.
- **CONDITIONAL** — señal débil/ruidosa; puede requerir más sensores o mejor feature engineering.
- **NO-GO** — ninguna feature muestra tendencia distinguible del ruido → el modo de falla **no es
  observable** con la instrumentación actual. (No es problema de modelo; es de sensores.)

---

### Gate 5 — Horizonte pronóstico alcanzable
*(Métricas PHM — Prognostic Horizon, Saxena)*
**Pregunta:** ¿**Cuánto antes** de la falla la señal se vuelve fiablemente detectable?
**El horizonte NO se fija de antemano — se descubre.**
**Cómo se mide:** EDA Paso 6 + baseline. ¿En qué punto antes de la falla la señal se separa de forma
estable del baseline sano? Ese punto es el horizonte alcanzable. Luego se compara contra el
**lead time accionable** (cuánto tiempo necesita mantenimiento para actuar).

- **GO** — horizonte alcanzable ≥ lead time que el negocio necesita para actuar.
- **CONDITIONAL** — horizonte < lo deseado pero > 0 y accionable en algún flujo.
- **NO-GO** — la señal solo aparece tan cerca de la falla que **no da tiempo a actuar**.
  Un aviso que llega tarde es inútil aunque el modelo sea preciso.

> Nota: aquí es donde se resuelve la tensión "48h vs. lo que se pueda". No impongas el número;
> mide el horizonte real y deja que el negocio decida si alcanza.

---

### Gate 6 — Suficiencia poblacional (el problema de "1 trayectoria")
**Pregunta:** ¿Tengo **suficientes trayectorias run-to-failure independientes** y suficientes eventos
por modo de falla para entrenar **y** validar sin fuga?
**Cómo se mide:** conteo directo. Una *trayectoria* = la historia completa de un activo de sano a falla.

- **GO** — decenas de trayectorias independientes; suficientes fallas por modo (piso muy aproximado:
  ~20–30 fallas por modo, más es mejor — depende del dominio y del ruido).
- **CONDITIONAL** — pocas trayectorias → considerar **supervivencia/censura**, transfer learning,
  detección de anomalías no-supervisada, o usar un **benchmark** (p. ej. CMAPSS) para la metodología.
- **NO-GO** — **1 (o 0) trayectorias de falla** → no se puede aprender ni validar. Solo sirve para
  probar la tubería (plumbing), no para modelar.

> "Una sola trayectoria" = tienes un único ejemplo del viaje a la falla. Las fallas son heterogéneas:
> un ejemplo no enseña la variabilidad, y no deja nada que apartar para test.

#### Qué cuenta como una trayectoria

Una **trayectoria** = un ciclo completo **sano → falla**. La reparación reinicia el reloj de salud:
termina una trayectoria y arranca la siguiente. Las trayectorias se acumulan tanto por
**robots** como por **ciclos de reparación** de cada robot.

```
salud
 sano ┤╲            ╲              ╲
      │ ╲            ╲              ╲
      │  ╲            ╲              ╲
falla ┤───●───────────●──────────────●──→  tiempo / uso
          ↑ reparan   ↑ reparan
       Trayectoria 1   Trayectoria 2   Trayectoria 3
       (sano→falla)    (sano→falla)    (sano→falla)
```

Cada bajada hasta el umbral de falla (●) es **una** trayectoria = **un** ejemplo run-to-failure.

Conteo:

```
trayectorias_totales = Σ (ciclos falla-repara-falla de cada robot)

  1 robot   × 3 ciclos  =   3 trayectorias
  100 robots × 1 ciclo  = 100 trayectorias   (caso CMAPSS: 1 motor = 1 trayectoria)
  100 robots × 3 ciclos = 300 trayectorias
```

**Condición para contar como trayectoria independiente:** la reparación debe devolver el activo a
estado *sano* de verdad. Si solo se reemplaza una pieza y el resto sigue degradado (p. ej. cambian
el reductor del eje 3 pero el servo del eje 5 sigue gastado), el "sano" no se reinicia limpio y esas
trayectorias arrancan contaminadas.

> **Trayectoria = unidad de conteo (Gate 6). Robot/activo = unidad de split (Gate 7).** No las confundas.

---

### Gate 7 — Validez de la evaluación
*(disciplina de ML; EDA como soporte)*
**Pregunta:** ¿Puedo evaluar **honestamente**, sin fuga de datos?
**Cómo se mide:** diseño del split. **Split por unidad/activo** (ninguna unidad en train y test a la vez),
orden temporal respetado, y un **baseline ingenuo** definido y superado.

- **GO** — split por unidad, orden temporal respetado, baseline definido y superado.
- **CONDITIONAL** — esquema de validación definido pero baseline aún no medido.
- **NO-GO** — solo puedes evaluar con fuga (misma unidad en ambos lados) → cualquier métrica **miente**.

> Baseline ingenuo = ¿un modelo trivial (RUL constante, o regresión lineal sobre un Health Index)
> ya da un piso? Si el baseline casi iguala al modelo complejo, el modelo complejo no es GO todavía.

#### Trayectoria = unidad de conteo · Robot = unidad de split

La trampa más común. Un robot con 5 ciclos aporta **5 trayectorias** al conteo del Gate 6, pero para
partir train/test la unidad **no es la trayectoria — es el robot**.

**Por qué los ciclos del mismo robot NO son independientes:** comparten una *huella* fija que la
reparación no borra — tolerancias de fabricación de esa unidad, montaje/alineación, la tarea que
ejecuta (carga, trayectoria, velocidad), operador, y ambiente de su ubicación. Un modelo puede
**memorizar esa huella**. Si pones ciclos del Robot-80 en train y otros ciclos del **mismo** Robot-80
en test, el modelo lo "reconoce" y la métrica sale inflada → **fuga de datos**. La reparación
reinicia el reloj de salud, no la identidad del robot.

**Independencia aquí significa:** el test mide si el modelo generaliza a un robot que **nunca vio**.
Eso solo se logra si **todos** los ciclos de un robot caen del **mismo lado** del split.

```
Robot-80 con 5 ciclos:

  ✗ MAL:  3 ciclos de Robot-80 en train + 2 ciclos de Robot-80 en test   → fuga
  ✓ BIEN: los 5 ciclos de Robot-80 van completos a un solo lado

Split por activo (100 robots):

  train = robots 1–79    (con TODOS sus ciclos)
  test  = robots 80–100  (con TODOS sus ciclos)
```

**Técnica:** split por grupo — `GroupKFold` / `LeaveOneGroupOut` en scikit-learn, agrupando por
`robot_id`. Mejor que un corte fijo: **rotar** qué robots se apartan (validación cruzada por grupo),
para no depender de que los robots 80–100 resulten "fáciles" o "difíciles" por azar.

> Consecuencia práctica: muchas trayectorias de **pocos** robots dan volumen de aprendizaje pero
> validación débil (no sabes si generaliza a otro activo). El ideal es **muchos robots, cada uno con
> varios ciclos**.

---

### Gate 8 — Desplegabilidad operativa
*(que funcione **de verdad** en planta)*
**Pregunta:** ¿El modelo puede **correr donde se necesita** y alguien **actuará** sobre su salida?
**Cómo se mide:** restricciones OT/red/latencia + dueño de la acción + plan de adopción.

- **GO** — corre en el entorno objetivo (latencia/red/OT), hay quién recibe la alerta, hay flujo de acción,
  y adopción plausible.
- **CONDITIONAL** — técnicamente desplegable, pero sin dueño de la acción o sin plan de adopción.
- **NO-GO** — restricciones OT/seguridad impiden ejecutar o actuar, o nadie actuaría sobre la alerta.

---

## Tarjeta de veredicto (plantilla)

| Gate | Compuerta | Veredicto | Evidencia (del EDA) | Condición / dueño / plazo |
|---|---|---|---|---|
| 0 | Encuadre de negocio | ⬜ GO / COND / NO-GO | | |
| 1 | Accesibilidad y flujo | ⬜ GO / COND / NO-GO | | |
| 2 | Validez y calidad | ⬜ GO / COND / NO-GO | | |
| 3 | Integridad de etiqueta | ⬜ GO / COND / NO-GO | | |
| 4 | Señal pronóstica | ⬜ GO / COND / NO-GO | | |
| 5 | Horizonte alcanzable | ⬜ GO / COND / NO-GO | | |
| 6 | Suficiencia poblacional | ⬜ GO / COND / NO-GO | | |
| 7 | Validez de evaluación | ⬜ GO / COND / NO-GO | | |
| 8 | Desplegabilidad | ⬜ GO / COND / NO-GO | | |

**Veredicto global = la peor compuerta.**
Frase de cierre (obligatoria antes de modelar):
*"El proyecto es [GO / CONDITIONAL / NO-GO] porque la compuerta limitante es [Gate N], por [razón].
La señal a explotar es [X]; el horizonte alcanzable es [Y]; se modela con [familia] porque [evidencia]."*

---

## Métricas PHM — definiciones para Gate 4 y Gate 5

Las tres primeras (Coble) **rankean sensores/features antes de modelar**. La cuarta (Saxena)
**evalúa las predicciones después de modelar**.

- **Monotonicity (monotonicidad).** Mide si una feature tiene tendencia consistente (siempre sube o
  siempre baja) a lo largo de la vida del activo. Intuición: por unidad, |fracción de diferencias
  consecutivas positivas − fracción negativas|, promediado sobre unidades. **0** = ruido sin dirección;
  **1** = perfectamente monótona. Alta → buena para Health Index / RUL.

- **Trendability (tendenciabilidad).** Mide si la **misma** feature se comporta parecido **entre**
  unidades (todas las trayectorias con forma similar). Se estima como la correlación (mínima o típica)
  de la feature entre unidades tras alinearlas en longitud. Alta → la señal **generaliza** entre activos,
  no es idiosincrática de uno.

- **Prognosability (pronosticabilidad).** Mide qué tan **agrupado** está el valor de la feature en el
  **momento de falla** a través de la población, relativo a su rango de variación. Baja dispersión en la
  falla → existe un **umbral de falla estable y predecible**.

- **Prognostic Horizon (horizonte pronóstico).** Cuánto tiempo **antes** de la falla las predicciones de
  RUL del modelo entran y se **mantienen** dentro de una banda de error aceptable (±α). Es la
  formalización de *"hasta cuándo se puede predecir"*. **Se mide, no se asume**, y luego se compara
  contra el lead time accionable (Gate 5).

> Fórmulas exactas: Coble (2010, tesis, Univ. Tennessee) para las tres primeras; Saxena et al. (2008,
> PHM'08) para Prognostic Horizon y familia (α-λ accuracy, relative accuracy, convergence).

---

## Apéndice — aplicación a "lo que tienes hoy" (ilustrativo)

Cómo puntúan tus dos activos actuales bajo este gate. Sirve para *entender* el gate por contraste.

### NASA CMAPSS (FD001) — set de modelado
| Gate | Veredicto | Por qué |
|---|---|---|
| 1 Accesibilidad | GO | Dataset estático, cargable, limpio |
| 2 Validez | GO | Bien formado; 7 sensores planos se filtran en EDA Paso 2/3 |
| 3 Etiqueta | GO | Run-to-failure completo; RUL construible por diseño |
| 4 Señal | GO | Varios sensores con monotonicity clara (2,3,4,8,9,11,13,15,17 suben; 7,12,20,21 bajan) |
| 5 Horizonte | GO/COND | Se mide con el modelo; hay señal temprana en la mayoría de motores |
| 6 Población | GO | 100 trayectorias run-to-failure |
| 7 Evaluación | GO | Split por `unit` disponible (train/test separados por motor) |
| 0 / 8 | N/A | Es benchmark académico, no despliegue real |

**Veredicto:** GO **para desarrollar metodología**. Por eso es el activo de modelado del MVP.

### Simulador de 3 robots — set de plumbing
| Gate | Veredicto | Por qué |
|---|---|---|
| 1 Accesibilidad | GO | Fluye por NATS→Faust→InfluxDB en tiempo real |
| 2 Validez | GO | Datos sintéticos limpios |
| 3 Etiqueta | COND/NO-GO | Solo Robot-03 tiene un evento de "falla" (degradación a CRITICAL) |
| 6 Población | **NO-GO** | **1 sola trayectoria de falla** (Robot-03); Robot-01/02 son ruido sano |
| 7 Evaluación | NO-GO | Con 1 trayectoria no hay nada que apartar para test |

**Veredicto:** **NO-GO para modelar, GO para plumbing.** El simulador prueba que la tubería
edge→dashboard funciona (los datos fluyen, el dashboard se pone rojo). El aprendizaje del modelo
vive en CMAPSS. Son roles complementarios, no redundantes.

---

*Capa de gate general — úsese junto a `EDAGuiaGlobal.md`. Veredicto global = la compuerta más débil.*
