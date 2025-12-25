# 🛡️ Control de Plataforma Xtrim

> **Radiografía Ejecutiva de Infraestructura, FinOps y Gobierno de Datos.**

Dashboard profesional desarrollado en **Python + Streamlit** para la gestión integral del inventario de servidores de Xtrim. Proporciona visibilidad en tiempo real sobre capacidad, riesgos operativos, costos (FinOps) y calidad de los datos.

---

## 📋 Características Principales

### 📊 Visualización Ejecutiva

* **KPIs de Alto Nivel:** Total de servidores, mix físico/virtual, cobertura de backups y capacidad total (RAM/CPU).
* **Gráficos Interactivos:** Sunburst (Jerarquía), Treemap y Barras Apiladas para análisis profundo.
* **Filtros Avanzados:** Por Ubicación (UIO/GYE), Segmento de Red, Sistema Operativo y Criticidad.

### 💰 FinOps & Costos

* **Calculadora TCO:** Proyección de costos mensuales/anuales basada en recursos (vCPU/RAM).
* **Simulación:** Permite ingresar costos unitarios y sobreescribir la capacidad total para escenarios *"What-If"*.

### 🔍 Gobierno de Datos

* **Auditor Automático:** Detecta servidores sin IP, sin Hostname o con SO desconocido.
* **Exportación de Errores:** Descarga un Excel limpio con los registros que requieren corrección manual.

### 📄 Reportes Automatizados

* **Generador PDF:** Crea reportes ejecutivos listos para imprimir con un solo clic.
* **Timezone Aware:** Ajustado automáticamente a la zona horaria de Ecuador (America/Guayaquil).

---

## 🚀 Instalación y Ejecución

### Opción A: Docker (Recomendada)

La forma más rápida y estable de ejecutar el proyecto.

1. **Requisitos:** Docker Desktop instalado.
2. **Ejecutar:**

    ```bash
    docker-compose up --build
    ```

3. **Acceder:** Abrir [http://localhost:8501](http://localhost:8501) en tu navegador.

### Opción B: Desarrollo Local

Para modificar el código o correr sin contenedores.

1. **Instalar dependencias:**

    ```bash
    pip install uv
    uv venv
    uv pip install -r pyproject.toml
    ```

2. **Ejecutar aplicación:**

    ```bash
    .venv/Scripts/streamlit run src/app.py
    ```

---

## 📂 Estructura del Proyecto

```text
.
├── data/               # Fuente de datos (Excel: INVENTARIO SRV.xlsx)
├── src/
│   ├── core/           # Lógica de Negocio
│   │   ├── cleaner.py  # Limpieza y Normalización
│   │   ├── metrics.py  # Cálculos de KPIs y FinOps
│   │   ├── reporter.py # Generador de PDF (fpdf2)
│   │   └── loader.py   # Carga de archivos
│   ├── ui/             # Interfaz Gráfica
│   │   ├── charts.py   # Gráficos Plotly Premium
│   │   └── layout.py   # Estructura del Dashboard
│   └── app.py          # Punto de entrada
├── tests/              # Pruebas automatizadas
└── Dockerfile          # Configuración de despliegue
```

---

## 🛠️ Tecnologías

* **Core:** Python 3.12, Pandas.
* **UI:** Streamlit.
* **Viz:** Plotly Express / Graph Objects.
* **Reportes:** FPDF2, XlsxWriter.
* **Infra:** Docker, Docker Compose.

---

## 👤 Créditos

Desarrollado y mantenido por **Ronny Ortiz**.
*Control de Plataforma Xtrim - 2025*
