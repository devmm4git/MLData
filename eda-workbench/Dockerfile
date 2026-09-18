# ============================================================
#  EDA Workbench - imagen unica reproducible
#  Base: Jupyter datascience-notebook (Python + R + tidyverse)
#  Hornea los requirements para que NO se pierdan al reiniciar
#  (a diferencia de 'docker run --rm' + pip manual).
# ============================================================
FROM quay.io/jupyter/datascience-notebook:2026-07-28

# 1) Requisitos SOLIDOS: si estos fallan, el build debe fallar (los quieres saber).
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# 2) Requisitos FRAGILES (pins estrechos / compilan C): best-effort.
#    Si alguno falla, el build NO se cae; verificar_entorno.py te dira cual falto.
COPY requirements-optional.txt /tmp/requirements-optional.txt
RUN pip install --no-cache-dir -r /tmp/requirements-optional.txt \
    || echo ">>> AVISO: uno o mas paquetes OPCIONALES no se instalaron. Revisa requirements-optional.txt"
