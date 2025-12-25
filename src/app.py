import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.config import EXCEL_FILE
from src.core.loader import load_data
from src.core.cleaner import clean_data
from src.core.metrics import InventoryMetrics
from src.ui import layout

def main():
    st.set_page_config(
        page_title="Platform Dashboard",
        page_icon="🛡️",
        layout="wide"
    )

    # Sidebar: File Upload
    with st.sidebar:
        st.header("📂 Configuración")
        uploaded_file = st.file_uploader("Cargar Inventario Actual (Excel)", type=["xlsx"], key="current")
        
        # Historical Comparison
        st.markdown("---")
        st.subheader("📊 Comparación Histórica")
        st.caption("Sube un archivo de mes anterior para ver cambios.")
        previous_file = st.file_uploader("Inventario Anterior (Opcional)", type=["xlsx"], key="previous")
        st.divider()

    try:
        # Determine Source for CURRENT data
        source = uploaded_file if uploaded_file else EXCEL_FILE
        
        # Load Data
        with st.spinner("Cargando inventario actual..."):
            # Check existence only if using default file
            if source == EXCEL_FILE and not EXCEL_FILE.exists():
                st.error(f"❌ No se encontró el archivo de datos en: {EXCEL_FILE}")
                st.info("Por favor mapea el volumen 'data' conteniendo 'INVENTARIO SRV.xlsx' o sube un archivo.")
                return

            raw_df = load_data(source)
            df = clean_data(raw_df)
            current_metrics = InventoryMetrics(df)

        # Load PREVIOUS data if provided
        previous_metrics = None
        if previous_file:
            with st.spinner("Cargando inventario anterior para comparación..."):
                prev_raw_df = load_data(previous_file)
                prev_df = clean_data(prev_raw_df)
                previous_metrics = InventoryMetrics(prev_df)

        # Render UI with both current and optional previous metrics
        layout.render(current_metrics, previous_metrics)
        
    except Exception as e:
        st.error(f"Error crítico en la aplicación: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

