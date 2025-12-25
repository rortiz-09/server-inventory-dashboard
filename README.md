# 🛡️ Platform Control Dashboard

Dashboard ejecutivo para el control de inventario de servidores, riesgos y cumplimiento.

## 📋 Características

- **Ingesta de Datos:** Carga tolerante a fallos de Excel desordenado (`data/INVENTARIO SRV NAC 2025.xlsx`).
- **Limpieza Automática:** Normalización de nombres de host, direcciones IP, tipos de servidor y sistemas operativos.
- **Métricas de Control:**
  - Distribución Físico vs Virtual.
  - Compliance de Respaldos.
  - Análisis de Obsolescencia/Riesgo por SO.
- **Tecnología:** Python 3.12, Streamlit, Plotly, Pandas, Docker.

## 🚀 Ejecución Rápida (Docker)

1. **Requisitos:** Docker & Docker Compose.
2. **Setup de Datos:**
   Asegúrate de que el archivo `INVENTARIO SRV NAC 2025.xlsx` esté en la carpeta `data/`.
3. **Arrancar:**

   ```bash
   docker-compose up --build
   ```

4. **Acceder:**
   Abrir [http://localhost:8501](http://localhost:8501).

## 🛠️ Desarrollo Local

1. **Instalar dependencias (`uv`):**

   ```bash
   pip install uv
   uv venv
   uv pip install -r pyproject.toml
   ```

2. **Ejecutar:**

   ```bash
   .venv/Scripts/streamlit run src/app.py
   ```

## 🧪 Tests

```bash
uv run pytest
```

## 📂 Estructura del Proyecto

```text
.
├── data/               # Volumen de persistencia (Excel)
├── src/
│   ├── core/           # Lógica de Negocio (Backend puro)
│   │   ├── loader.py   # Ingesta
│   │   ├── cleaner.py  # Limpieza
│   │   └── metrics.py  # KPIs
│   ├── ui/             # Capa de Presentación
│   │   ├── charts.py   # Componentes Visuales
│   │   └── layout.py   # Composición de Pantalla
│   └── app.py          # Entrypoint
├── tests/              # Tests Unitarios
└── Dockerfile          # Definición de Contenedor
```
