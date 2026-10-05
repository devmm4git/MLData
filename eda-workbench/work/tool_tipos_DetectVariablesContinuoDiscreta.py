"""
tipos_numericos.py
------------------
Clasifica las columnas NUMERICAS de un DataFrame en 'continua' o 'discreta',
y marca cuales conviene evaluar con skew() (las continuas).

Criterio (combina 3 senales, no una sola):
  1. ¿Es numerica?            -> si no, se descarta (texto/categoria no lleva sesgo)
  2. ¿Tiene decimales reales?  -> si algun valor no es entero -> CONTINUA
  3. Si son enteros: cardinalidad
        - pocos valores distintos (<= umbral_discreta) -> DISCRETA (conteo/categoria)
        - muchos valores distintos                     -> CONTINUA (ej. un ID daria continua,
                                                          por eso se excluyen IDs aparte)

Uso:
    from tipos_numericos import clasificar_numericas, columnas_para_sesgo
    clasificar_numericas(df)                 # tabla completa
    columnas_para_sesgo(df)                  # solo la lista de continuas (para skew)
    clasificar_numericas(df, excluir=["PassengerId"])   # ignora IDs
"""

import pandas as pd
import numpy as np


def clasificar_numericas(df, umbral_discreta=15, excluir=None):
    """Devuelve un DataFrame clasificando cada columna numerica como continua/discreta."""
    excluir = set(excluir or [])
    filas = []
    for col in df.columns:
        if col in excluir:
            continue
        s = df[col]
        if not pd.api.types.is_numeric_dtype(s):
            continue  # solo numericas

        datos = s.dropna()
        u = datos.nunique()
        # ¿hay algun valor con parte decimal? (x % 1 != 0)
        tiene_decimales = bool((datos % 1 != 0).any())

        if tiene_decimales:
            tipo = "continua"
            motivo = "tiene valores con decimales"
        elif u <= umbral_discreta:
            tipo = "discreta"
            motivo = f"solo enteros y pocos unicos ({u} <= {umbral_discreta})"
        else:
            tipo = "continua"
            motivo = f"enteros pero muchos unicos ({u} > {umbral_discreta})"

        filas.append({
            "columna": col,
            "dtype": str(s.dtype),
            "unicos": u,
            "tiene_decimales": tiene_decimales,
            "tipo": tipo,
            "evaluar_sesgo": "SI" if tipo == "continua" else "no",
            "motivo": motivo,
        })
    return pd.DataFrame(filas)


def columnas_para_sesgo(df, umbral_discreta=15, excluir=None):
    """Devuelve solo la lista de columnas continuas (las candidatas a skew/log)."""
    t = clasificar_numericas(df, umbral_discreta=umbral_discreta, excluir=excluir)
    return t.loc[t["tipo"] == "continua", "columna"].tolist()


if __name__ == "__main__":
    import sys
    from scipy.stats import skew
    ruta = sys.argv[1] if len(sys.argv) > 1 else "U4_04_train.csv"
    df = pd.read_csv(ruta, na_values=["", " "])

    print("== Clasificacion de columnas numericas ==")
    tabla = clasificar_numericas(df, excluir=["PassengerId"])
    with pd.option_context("display.width", 200, "display.max_colwidth", 50):
        print(tabla.to_string(index=False))

    print("\n== Columnas continuas -> evaluar sesgo ==")
    continuas = columnas_para_sesgo(df, excluir=["PassengerId"])
    for col in continuas:
        s = skew(df[col].dropna())
        print(f"  {col:8} sesgo = {s:.2f}")