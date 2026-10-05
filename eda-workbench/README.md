# EDA Workbench — entorno unico y reproducible

Un solo contenedor (Python + R) que usan por igual **JupyterLab** y **VS Code**.
Soporta el flujo `EDAGuiaGlobal.md` -> `NucleoCuantitativo_por_Gate.md` -> `GateGoNoGo.md`.

## Estructura
```
eda-workbench/
├── Dockerfile                 # hornea los requirements en la imagen
├── docker-compose.yml         # levanta y mantiene vivo el contenedor
├── requirements.txt           # paquetes SOLIDOS (build falla si estos fallan)
├── requirements-optional.txt  # paquetes FRAGILES (best-effort, no tumban el build)
├── verificar_entorno.py       # smoke test
├── .devcontainer/
│   └── devcontainer.json      # VS Code "Reopen in Container" (misma imagen)
└── work/                      # << AQUI van tus notebooks y datos (persisten en disco)
```

## Uso (3 comandos)
```bash
cd eda-workbench
docker compose build      # 1. construye la imagen con TODOS los requirements dentro
docker compose up -d      # 2. corre en segundo plano (queda vivo)
# 3. abre:  http://localhost:10000/?token=eda-dev
```
Apagar: `docker compose down`  ·  Reconstruir tras cambiar requirements: repite `build`.

> **Puerto:** el navegador usa **10000** (lado izquierdo del `-p`). El `8888` que
> imprime Jupyter es su vista interna; ignoralo.

## Poner tus datos
Copia `U4_04_train.csv` (y tus notebooks) dentro de `work/`. Todo lo que esta en
`work/` vive en tu disco real y sobrevive reinicios. Lo de afuera de `work/`, no.

## Verificar
En una terminal de Jupyter (o `docker compose exec eda bash`):
```bash
python /home/jovyan/work/verificar_entorno.py   # si lo copiaste a work/
```

## Conectar VS Code (elige una)
- **Rapida (kernel remoto):** extension *Jupyter* -> abre un `.ipynb` -> "Select Kernel"
  -> "Existing Jupyter Server" -> pega `http://localhost:10000/?token=eda-dev`.
- **Gold standard (Dev Containers):** extension *Dev Containers* -> "Reopen in Container".
  Usa el `.devcontainer/devcontainer.json` (misma imagen que Jupyter = unicidad total).

## Reproducibilidad (congela versiones antes de repartir al equipo)
Tras un build exitoso:
```bash
docker compose exec eda pip freeze > requirements.lock.txt
```
El equipo instala desde el `.lock` para tener bit-a-bit lo mismo.

## Nota sobre paquetes fragiles
`ydata-profiling`, `sweetviz` y `scikit-survival` estan en *optional* porque
tienen pins estrechos o compilan C. Si fallan en el build, el entorno igual queda
listo; `verificar_entorno.py` te dira cuales faltaron. Para el caso Titanic (tabular)
NO son necesarios.
