"""Smoke test del EDA Workbench.
Corre DENTRO del contenedor:  python verificar_entorno.py
Marca [OPCIONAL] las librerias fragiles que pueden no haberse instalado."""
import importlib

SOLIDAS = ["pandas","numpy","scipy","statsmodels","matplotlib","seaborn",
           "plotly","missingno","sklearn","ppscore","lifelines",
           "pandera","great_expectations","polars","pyarrow"]
OPCIONALES = ["ydata_profiling","sweetviz","sksurv"]

def check(name, opcional=False):
    tag = "[OPCIONAL] " if opcional else ""
    try:
        m = importlib.import_module(name)
        print(f"OK    {tag}{name:20} {getattr(m,'__version__','?')}")
        return True
    except Exception as e:
        estado = "AVISO" if opcional else "FALLA"
        print(f"{estado} {tag}{name:20} -> {type(e).__name__}")
        return opcional  # un opcional ausente NO invalida el entorno

print("=== EDA Workbench :: verificacion ===\n-- Solidas --")
ok = all([check(n) for n in SOLIDAS])
print("-- Opcionales --")
for n in OPCIONALES: check(n, opcional=True)

# Prueba real minima
import pandas as pd, numpy as np
df = pd.DataFrame({"x": np.random.randn(200), "y": np.random.randint(0,2,200)})
assert df.corr().shape == (2,2)
print("\nPrueba pandas/corr OK")
print("\nRESULTADO:", "ENTORNO LISTO ✔" if ok else "FALTAN SOLIDAS -> revisa el build")
