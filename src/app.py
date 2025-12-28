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
        st.header("📂 Gestión de Datos")
        
        # Scenario: User uploads a NEW file to compare against existing data
        st.info("💡 Para comparar cambios, carga el nuevo archivo aquí:")
        uploaded_file = st.file_uploader("Cargar Nuevo Inventario (Excel)", type=["xlsx"], key="current")
        
        st.markdown("---")
        if uploaded_file:
            st.warning("⚠️ Modo Comparación Activo\n(Nuevo vs Base)")
        else:
            st.success("✅ Modo Base Activo\n(Visualizando Datos del Sistema)")


    try:
        # 1. Siempre cargamos la BASE del sistema (Previous/Baseline)
        base_df = None
        base_metrics = None
        
        if EXCEL_FILE.exists():
            base_raw = load_data(EXCEL_FILE)
            base_df = clean_data(base_raw)
            base_metrics = InventoryMetrics(base_df)
        else:
            if not uploaded_file:
                st.error(f"❌ No se encuentra el archivo base: {EXCEL_FILE}")
                return

        # 2. Determinamos qué mostrar
        current_metrics = None
        previous_metrics = None

        if uploaded_file:
            # Caso: Comparación
            with st.spinner("Procesando nuevo archivo..."):
                curr_raw = load_data(uploaded_file)
                curr_df = clean_data(curr_raw)
                current_metrics = InventoryMetrics(curr_df)
                
                # La base se convierte en "Anterior"
                previous_metrics = base_metrics
        else:
            # Caso: Normal
            current_metrics = base_metrics
            previous_metrics = None

        if current_metrics:
            # Render UI
            layout.render(current_metrics, previous_metrics)
        
    except Exception as e:
        st.error(f"Error crítico en la aplicación: {e}")
        import traceback
        st.code(traceback.format_exc())

if __name__ == "__main__":
    main()

