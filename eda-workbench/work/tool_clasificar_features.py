"""
clasificar_features.py
----------------------
Clasifica cada columna de un DataFrame cruzando TRES senales:
    cardinalidad (n_unicos)  +  tipo de dato  +  % de nulos
y emite un veredicto de tratamiento: SI / NO / CON TRABAJO.

Uso rapido:
    import pandas as pd
    from clasificar_features import tabla_features, comentario_features

    df = pd.read_csv("/home/jovyan/work/U4_04_train.csv")
    print(tabla_features(df, target="Survived"))      # DataFrame con el veredicto
    print(comentario_features(df, target="Survived")) # bloque listo para pegar como comentario

Nota: los umbrales son heuristicas orientativas, NO leyes. La senal real
(cuanto predice una feature) se mide en el Paso 5 / Gate 4, no aqui.
"""

import pandas as pd
import numpy as np


def clasificar_columna(df, col, target=None,
                       umbral_id=0.95,      # ratio unicos/filas por encima del cual es ID
                       umbral_baja=10,      # <= esto es categorica de baja cardinalidad
                       umbral_vacia=60.0):  # >= este % de nulos es "casi vacia"
    """Devuelve un dict con el diagnostico de una sola columna."""
    s = df[col]
    n = len(df)
    u = s.nunique(dropna=True)
    ratio = u / n if n else 0.0
    n_nulos = int(s.isna().sum())
    pct_nulos = (n_nulos / n * 100) if n else 0.0
    es_num = pd.api.types.is_numeric_dtype(s)
    es_texto = (s.dtype == object) or (str(s.dtype) == "str")

    nota_nulos = f"; imputar {n_nulos} nulos ({pct_nulos:.1f}%)" if n_nulos > 0 else ""

    # --- arbol de decision ---
    if target is not None and col == target:
        tipo, usar, decision = "TARGET", "-", "variable objetivo (lo que se predice)"
    elif u == 1:
        tipo, usar, decision = "constante", "NO", "varianza 0, sin senal -> eliminar"
    elif pct_nulos >= umbral_vacia:
        tipo, usar, decision = "casi vacia", "CON TRABAJO", \
            f"{pct_nulos:.0f}% nulos -> bandera tiene/no, o descartar"
    elif ratio >= umbral_id:
        tipo, usar, decision = "ID / texto libre", "NO (cruda)", \
            "cardinalidad ~= filas -> feature engineering o descartar"
    elif u == 2:
        tipo, usar, decision = "binaria", "SI", "encoding a 0/1" + nota_nulos
    elif es_num and u > umbral_baja:
        tipo, usar, decision = "numerica continua", "SI", \
            "escalar si el modelo lo requiere" + nota_nulos
    elif u <= umbral_baja:
        tipo, usar, decision = "categorica baja card.", "SI", "one-hot / ordinal" + nota_nulos
    elif es_texto:
        tipo, usar, decision = "categorica alta card.", "CON TRABAJO", \
            "encoding especial (target/hashing) o extraer sub-feature" + nota_nulos
    else:
        tipo, usar, decision = "revisar", "?", "caso no estandar -> inspeccionar a mano"

    return {
        "columna": col, "dtype": str(s.dtype), "unicos": u,
        "ratio": round(ratio, 2), "pct_nulos": round(pct_nulos, 1),
        "tipo": tipo, "usar": usar, "decision": decision,
    }


def tabla_features(df, target=None, **umbrales):
    """Devuelve un DataFrame con el diagnostico de todas las columnas."""
    filas = [clasificar_columna(df, c, target=target, **umbrales) for c in df.columns]
    return pd.DataFrame(filas)


def comentario_features(df, target=None, **umbrales):
    """Devuelve un string con la tabla como bloque de comentarios listo para pegar."""
    t = tabla_features(df, target=target, **umbrales)
    ancho_col = max(t["columna"].str.len().max(), 8)
    lineas = ["# " + "=" * 60,
              "#  DICCIONARIO DE FEATURES (auto-generado)",
              "#  usar: SI = usar | NO = descartar cruda | CON TRABAJO = feature eng.",
              "# " + "-" * 60]
    for _, r in t.iterrows():
        lineas.append(f"#  {r['columna']:<{ancho_col}}  {r['usar']:<11}  {r['decision']}")
    lineas.append("# " + "=" * 60)
    return "\n".join(lineas)


if __name__ == "__main__":
    # Demo con el Titanic si el archivo esta presente
    import sys
    ruta = sys.argv[1] if len(sys.argv) > 1 else "U4_04_train.csv"
    df = pd.read_csv(ruta, na_values=["", " "], keep_default_na=True)
    with pd.option_context("display.width", 200, "display.max_colwidth", 60):
        print(tabla_features(df, target="Survived").to_string(index=False))
    print()
    print(comentario_features(df, target="Survived"))
