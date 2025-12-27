"""
layout.py - Dashboard Ejecutivo Premium (Theme Aware)

Interfaz corporativa optimizada para Dark/Light mode y alta densidad de datos.

Autor: Sistema de Gestión de Plataforma Xtrim
Fecha: Diciembre 2024
"""

import streamlit as st
import pandas as pd
from typing import Optional

from src.core.metrics import InventoryMetrics
from src.ui import charts
import src.core.reporter as reporter
from src.core.comparator import InventoryComparator
from src.core.risk import RiskRadar
import io


def aplicar_estilos():
    """Estilos CSS que respetan el tema de Streamlit (Dark/Light)."""
    st.markdown("""
    <style>
        /* === VARIABLES QUE SE ADAPTAN AL TEMA === */
        
        /* === CONTENEDOR PRINCIPAL === */
        .block-container {
            padding: 1.5rem 2rem !important;
            max-width: 1500px !important;
        }
        
        /* === TARJETAS DE MÉTRICAS (Transparencia con borde sutil) === */
        [data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.05); /* Funciona en dark y light */
            padding: 10px 15px;
            border-radius: 8px;
            border: 1px solid rgba(128, 128, 128, 0.1);
            text-align: center;
        }
        
        /* Ajuste de fuentes para layout compacto */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            opacity: 0.8;
        }
        
        /* === HEADERS CON BORDE INFERIOR === */
        h1, h2, h3 {
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        }
        
        h3 {
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 5px;
            margin-bottom: 15px !important;
            font-size: 1.2rem !important;
            opacity: 0.9;
        }
        
        /* === ALINEACIÓN DE GRÁFICOS === */
        .js-plotly-plot {
            height: 500px !important; /* Altura generosa para evitar cortes */
        }
        
        /* === SIDEBAR === */
        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.1);
        }
        
        /* === IMPRESIÓN (Forzar Blanco/Negro) === */
        @media print {
            .stApp, .block-container, body {
                background: white !important;
            }
            [data-testid="stSidebar"], header, footer, button, .stDownloadButton {
                display: none !important;
            }
            * {
                color: black !important;
                box-shadow: none !important;
            }
            [data-testid="stMetric"] {
                border: 1px solid #000;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def renderizar_header():
    """Encabezado que se ve bien en ambos temas."""
    st.markdown("""
    <div style="padding: 1rem 0 2rem 0; text-align: left; border-bottom: 1px solid rgba(128,128,128,0.2); margin-bottom: 1rem;">
        <h1 style="margin: 0; font-size: 2rem; letter-spacing: 1px;">
            🛡️ CONTROL DE PLATAFORMA XTRIM
        </h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.7; font-size: 1rem; letter-spacing: 2px; text-transform: uppercase;">
            RADIOGRAFÍA EJECUTIVA DE INFRAESTRUCTURA
        </p>
    </div>
    """, unsafe_allow_html=True)


def renderizar_kpis_ejecutivos(m: InventoryMetrics, resumen: dict):
    """KPIs principales con diseño responsivo."""
    cols = st.columns(6)
    
    with cols[0]:
        st.metric("SERVIDORES", resumen['total'])
    with cols[1]:
        st.metric("VIRTUALIZACIÓN", f"{resumen['pct_virtual']:.0f}%", 
                 f"{resumen['virtuales']} VMs")
    with cols[2]:
        st.metric("FÍSICOS", resumen['fisicos'], 
                 f"{resumen['pct_fisico']:.0f}% Mix")
    with cols[3]:
        st.metric("SITES", m.ubicaciones_unicas)
    with cols[4]:
        st.metric("BACKUP SI", f"{resumen['cobertura_backup']:.0f}%")
    with cols[5]:
        st.metric("CALIDAD DATA", f"{resumen['calidad']:.0f}%")


def render(metricas: InventoryMetrics, metricas_anteriores: Optional[InventoryMetrics] = None):
    """Renderizado principal."""
    aplicar_estilos()
    
    # 0. Calculamos resumen inicial para defaults del sidebar
    resumen_global = metricas.obtener_resumen()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ OPCIONES")
        modo_presentacion = st.toggle("📺 Modo Presentación")
        if modo_presentacion:
            st.markdown("""<style>[data-testid="stSidebar"] { display: none; }</style>""", unsafe_allow_html=True)
            
        st.markdown("### 🔎 Búsqueda Rápida")
        df = metricas.datos_crudos
        busqueda = st.text_input("Buscar", placeholder="Hostname, IP, Segmento...")
        
        st.markdown("### 🔍 Filtros")
        with st.expander("Ubicación & Red", expanded=True):
            ubi_sel = st.multiselect("Ubicación", sorted(df['location'].unique()), default=sorted(df['location'].unique()))
            if 'network_segment' in df.columns:
                 seg_sel = st.multiselect("Segmento Red", sorted(df['network_segment'].unique()))
            else:
                 seg_sel = []
            
        with st.expander("Tipo & OS"):
            tipo_sel = st.multiselect("Tipo", sorted(df['server_type'].unique()), default=sorted(df['server_type'].unique()))
            os_sel = st.multiselect("OS", sorted(df['os'].unique())) 

        with st.expander("Estados"):
            if 'has_backup' in df.columns:
                bk_sel = st.multiselect("Respaldo", sorted(df['has_backup'].unique()))
            else:
                bk_sel = []

        st.markdown("---")
        st.markdown("### 💰 FinOps (Estimación)")
        costo_cpu = st.number_input("Costo unitario vCPU ($)", min_value=0.0, value=15.0, step=1.0)
        costo_ram = st.number_input("Costo unitario GB RAM ($)", min_value=0.0, value=8.0, step=1.0)
        
        # Override de Capacidad Total
        use_custom_capacity = st.checkbox("Sobreescribir Capacidad Total", value=False)
        custom_cpu = None
        custom_ram = None
        
        if use_custom_capacity:
            default_cpu = resumen_global['total_cpu']
            default_ram = int(resumen_global['total_ram_gb'])
            custom_cpu = st.number_input("Total vCPU Cores", min_value=0, value=default_cpu)
            custom_ram = st.number_input("Total RAM (GB)", min_value=0, value=default_ram)
            st.caption("Calculando costos sobre estos valores manuales.")
        
        st.markdown("---")
        st.markdown("### 📄 Reportes")
        if st.sidebar.button("Generar PDF Ejecutivo"):
             try:
                # Generar bytes del PDF
                pdf_bytes = reporter.generar_reporte_pdf(
                    metricas.obtener_resumen(), 
                    metricas.top_aplicaciones
                )
                
                st.sidebar.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name="reporte_ejecutivo.pdf",
                    mime="application/pdf"
                )
                st.sidebar.success("Generado!")
             except Exception as e:
                st.sidebar.error(f"Error: {e}")

    # Lógica de filtrado
    df_f = df.copy()
    if busqueda:
        b = busqueda.lower()
        df_f = df_f[df_f.astype(str).apply(lambda x: x.str.lower().str.contains(b, na=False)).any(axis=1)]
    if ubi_sel:
        df_f = df_f[df_f['location'].isin(ubi_sel)]
    if tipo_sel:
        df_f = df_f[df_f['server_type'].isin(tipo_sel)]
    if os_sel:
        df_f = df_f[df_f['os'].isin(os_sel)]
    if seg_sel:
        df_f = df_f[df_f['network_segment'].isin(seg_sel)]
    if bk_sel and 'has_backup' in df_f.columns:
        df_f = df_f[df_f['has_backup'].isin(bk_sel)]
        
    m = InventoryMetrics(df_f)
    resumen = m.obtener_resumen()

    # === DASHBOARD ===
    renderizar_header()
    
    # 🕒 TIME MACHINE: COMPARATIVA HISTÓRICA
    if metricas_anteriores:
        st.markdown("### 🕒 TIME MACHINE (Comparativa)")
        comp = InventoryComparator(metricas, metricas_anteriores)
        cambios = comp.calculate_changes()
        
        # Delta Metrics Row
        dc1, dc2, dc3, dc4 = st.columns(4)
        with dc1:
            st.metric("Variación Total", 
                     f"{cambios['summary']['net_change']:+d}", 
                     delta=int(cambios['summary']['net_change']))
        with dc2:
            st.metric("Nuevas Altas", f"+{cambios['summary']['added_count']}", delta_color="normal")
        with dc3:
            st.metric("Bajas/Decomisos", f"-{cambios['summary']['removed_count']}", delta_color="inverse")
        with dc4:
            st.metric("Backup Delta", f"{cambios['kpi_deltas']['backup_coverage']:+.0f}%")
            
        # Delta Details (Expandable)
        with st.expander("📝 Ver Detalles de Altas y Bajas"):
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.write("**🔽 Bajas (No detectados en carga actual):**")
                if cambios['details']['removed_hosts']:
                    st.error(", ".join(cambios['details']['removed_hosts'][:50]))
                else:
                    st.caption("Sin bajas detectadas.")
            with d_col2:
                st.write("**🔼 Altas (Nuevos en esta carga):**")
                if cambios['details']['added_hosts']:
                    st.success(", ".join(cambios['details']['added_hosts'][:50]))
                else:
                    st.caption("Sin nuevas altas.")
        st.markdown("---")

    renderizar_kpis_ejecutivos(m, resumen)
    
    st.markdown("---")
    
    # ROW 1: CAPACIDAD (Vital para Gerencia)
    st.markdown("### 🔋 CAPACIDAD & RECURSOS")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric("MEMORIA RAM TOTAL", f"{resumen['total_ram_gb']:,.0f} GB")
    with c2:
        st.metric("CPU CORES TOTAL", f"{resumen['total_cpu']:,.0f}")
    with c3:
         if 'ram_gb' in df_f.columns:
            res_loc = df_f.groupby('location')['ram_gb'].sum().sort_values(ascending=False).head(5)
            # Pequeño gráfico nativo para resumen rápido
            st.bar_chart(res_loc, color="#2E86C1", height=150)

    st.markdown("---")
    
    # ROW 2: INFRAESTRUCTURA (2 COLUMNAS PARA MEJOR VISIBILIDAD)
    st.markdown("### 🏗️ ARQUITECTURA DE SERVIDORES")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = charts.crear_grafico_pastel(m.distribucion_tipo_servidor, "Distribución Físico vs Virtual")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        fig = charts.crear_grafico_pastel(m.distribucion_so, "Distribución Sistemas Operativos")
        st.plotly_chart(fig, use_container_width=True)
       
    # ☢️ RISK RADAR (NUEVO)
    st.markdown("### ☢️ RADAR DE OBSOLESCENCIA (Live EOL)")
    
    # Análisis bajo demanda para no bloquear carga inicial si API falla
    radar = RiskRadar()
    df_risk = df_f.copy()
    
    # Aplicar evaluación a cada fila única de SO para eficiencia
    unique_os = df_risk['os'].dropna().unique()
    risk_map = {os: radar.evaluate_os(os) for os in unique_os}
    
    # KPIs de Riesgo
    eol_count = sum(1 for os in df_risk['os'] if risk_map.get(os, {}).get('status') == 'EOL')
    risk_count = sum(1 for os in df_risk['os'] if risk_map.get(os, {}).get('status') == 'RISK')
    
    r1, r2, r3 = st.columns(3)
    with r1:
        st.metric("Sistemas EOL (Crítico)", f"{eol_count}", delta="-Riesgo Alto", delta_color="inverse")
    with r2:
        st.metric("Próximo a Vencer (<1 año)", f"{risk_count}", delta="Atención", delta_color="off")
    with r3:
        st.info(f"Analizando {len(unique_os)} variantes de SO (cacheado).")
        
    if eol_count > 0:
        st.warning(f"⚠️ Se detectaron {eol_count} servidores con sistemas operativos fuera de soporte.")
        # Mostrar tabla de afectados usando la columna detallada para el mapa
        affected = df_risk[df_risk['os'].map(lambda x: risk_map.get(x, {}).get('status') == 'EOL')]
        st.dataframe(affected[['hostname', 'ip', 'os', 'server_type']], height=150)
        
    st.markdown("---")
        
    # ROW 3: DETALLE GEOGRÁFICO Y AMBIENTES
    col3, col4 = st.columns(2)
    
    with col3:
        fig = charts.crear_sunburst(m.datos_crudos, ['location', 'server_type'], "Jerarquía: Ubicación → Tipo")
        st.plotly_chart(fig, use_container_width=True)
        
    with col4:
         if 'environment' in m.datos_crudos.columns:
            fig = charts.crear_grafico_barras(m.distribucion_ambiente, "Distribución por Ambiente", orientacion='h')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
    # ROW 4: OPERACIÓN Y RESPALDO
    # ROW 4: OPERACIÓN Y RESPALDO (SECCIÓN MEJORADA)
    st.markdown("### 🛡️ CONTROL OPERATIVO & RESPALDOS")
    
    # Usamos 2 columnas pero la segunda tendrá el gráfico complejo
    col5, col6 = st.columns([1, 1.5]) 
    
    with col5:
        if 'has_backup' in m.datos_crudos.columns:
            datos_backup = m.datos_crudos['has_backup'].value_counts().to_dict()
            fig = charts.crear_grafico_pastel(datos_backup, "Cobertura General de Respaldo")
            st.plotly_chart(fig, use_container_width=True)
            
    with col6:
        # Gráfico Nuevo: Backup por Ambiente (Stacked Bar)
        df_backup = m.backup_por_ambiente
        if not df_backup.empty:
            fig = charts.crear_grafico_barras_apiladas(
                df_backup, 
                x_col='environment', 
                y_col='count', 
                color_col='has_backup', 
                titulo="Estado de Respaldo por Ambiente"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Fallback a Top Apps si no hay datos complejos
            fig = charts.crear_grafico_barras(m.top_aplicaciones, "Top Aplicaciones", orientacion='h')
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    
    # ROW 5 (Extra): Top Aplicaciones (Ahora en fila completa para detalle)
    st.markdown("### 📦 TOP APLICACIONES / SERVICIOS")
    st.info("Distribución de las aplicaciones más frecuentes instaladas en los servidores.")
    fig = charts.crear_grafico_barras(m.top_aplicaciones, "Top 10 Aplicaciones Detectadas", orientacion='h', color='#3498DB')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ROW 5: REDES (MOVADO AL FINAL)
    st.markdown("### 🔌 SEGMENTACIÓN DE REDES")
    st.info("Visualización basada en clasificación de segmentos IP (Guayaquil .59, Quito .21, etc.)")
    
    if 'network_segment' in df_f.columns:
        datos_red = m.distribucion_segmento_red
        # Gráfico Ancho completo para redes
        fig = charts.crear_grafico_barras(datos_red, "Distribución Total por Segmento de Red (VLANs)", orientacion='h', color='#8E44AD')
        st.plotly_chart(fig, use_container_width=True)

    # ROW 6: FINOPS Y GOBIERNO (NUEVO)
    st.markdown("---")
    st.markdown("### 💰 IMPACTO FINANCIERO (ESTIMADO)")
    
    finops = m.calcular_finops(costo_cpu, costo_ram, custom_cpu, custom_ram)
    fc1, fc2, fc3 = st.columns(3)
    
    with fc1:
        st.metric("COSTO MENSUAL (TCO)", f"${finops['total_mensual']:,.2f}")
    with fc2:
        st.metric("COSTO ANUAL PROYECTADO", f"${finops['total_anual']:,.2f}")
    with fc3:
         costo_cpu_total = finops['desglose']['cpu_costo']
         costo_ram_total = finops['desglose']['ram_costo']
         # Pequeño breakdown
         df_costos = pd.DataFrame({
             'Recurso': ['CPU', 'RAM'],
             'Costo': [costo_cpu_total, costo_ram_total]
         }).set_index('Recurso')
         st.bar_chart(df_costos, color='#27AE60', height=120)

    # === NUEVAS SECCIONES PREMIUM (Negocio e Infra) ===
    
    # SECCIÓN DE NEGOCIO (Responsables y Apps)
    if 'RESPONSABLE' in df_f.columns and 'APLICACION' in df_f.columns:
        st.markdown("---")
        st.markdown("### 🏢 GESTIÓN DE NEGOCIO (Dueños de Servicio)")
        
        col_biz1, col_biz2 = st.columns([2, 1])
        with col_biz1:
            # Treemap Responsable -> Aplicación
            # Limpieza rápida para el gráfico
            df_biz = df_f.copy()
            df_biz['RESPONSABLE'] = df_biz['RESPONSABLE'].fillna('SIN ASIGNAR').astype(str)
            df_biz['APLICACION'] = df_biz['APLICACION'].fillna('GENERICO').astype(str)
            
            fig = charts.crear_treemap(
                df_biz, 
                path=['RESPONSABLE', 'APLICACION'], 
                titulo="Mapa de Responsabilidad: ¿Quién cuida qué?"
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_biz2:
            st.info("Top 5 Responsables por Carga (CPU)")
            if 'cpu_cores' in df_biz.columns:
                top_resp = df_biz.groupby('RESPONSABLE')['cpu_cores'].sum().sort_values(ascending=False).head(5)
                st.bar_chart(top_resp, color="#E67E22")
            else:
                st.caption("No hay datos de CPU para calcular carga.")

    # SECCIÓN DE INFRAESTRUCTURA FÍSICA (Hardware)
    # Detectar si hay datos físicos reales (Enclosure, Serial, Modelo)
    cols_fisicos = [c for c in df_f.columns if c in ['ENCLOSURE', 'MODELO', 'SERIAL', 'IP_ADMIN']]
    hay_fisicos = len(cols_fisicos) > 0 and df_f['server_type'].str.contains('FISICO').any()
    
    if hay_fisicos:
        st.markdown("---")
        st.markdown("### 🏗️ INFRAESTRUCTURA FÍSICA & HARDWARE")
        
        ic1, ic2 = st.columns(2)
        with ic1:
            st.metric("Total Hosts Físicos", df_f[df_f['server_type'] == 'FISICO'].shape[0])
            if 'MODELO' in df_f.columns:
                top_models = df_f['MODELO'].value_counts().head(5)
                st.write("**Modelos Predominantes:**")
                st.dataframe(top_models, use_container_width=True)
                
        with ic2:
            if 'ENCLOSURE' in df_f.columns:
                 # Gráfico de Enclosures (Donde están alojados)
                 enc_counts = df_f['ENCLOSURE'].value_counts()
                 fig = charts.crear_grafico_pastel(enc_counts.to_dict(), "Distribución por Enclosure / Chasis")
                 st.plotly_chart(fig, use_container_width=True)
            else:
                 st.info("No se detectó información de Enclosures.")

    # ROW 7: CALIDAD DE DATOS
    st.markdown("---")
    st.markdown("### 🔍 CALIDAD DE DATOS & GOBIERNO")
    
    calidad_df = m.auditar_calidad_datos()
    
    qc1, qc2 = st.columns([1, 2])
    
    with qc1:
        st.metric("SCORE DE CALIDAD", f"{resumen['calidad']:.0f}/100")
        if not calidad_df.empty:
            st.error(f"Se encontraron {len(calidad_df)} registros con problemas.")
            
            # Boton descargar excel errores
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                calidad_df.to_excel(writer, sheet_name='Errores', index=False)
                
            st.download_button(
                label="📥 Descargar Reporte de Errores (Excel)",
                data=buffer.getvalue(),
                file_name="reporte_calidad_datos.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.success("¡Excelente! No se encontraron problemas obvios en los datos.")
            
    with qc2:
        if not calidad_df.empty:
            st.dataframe(calidad_df, height=200, use_container_width=True)
        else:
             st.info("La calidad de los datos cumple con los estándares definidos (IP válida, Hostname, SO identificado).")

    # ROW 8: TABLA DETALLADA
    st.markdown("---")
    st.markdown("### 📋 INVENTARIO DETALLADO")
    
    columnas_visibles = ['hostname', 'ip', 'network_segment', 'server_type', 'os', 'ram_gb', 'cpu_cores', 'has_backup', 'location']
    columnas_visibles = [c for c in columnas_visibles if c in df_f.columns]
    
    st.dataframe(
        df_f[columnas_visibles],
        use_container_width=True,
        hide_index=True,
        column_config={
            "hostname": "Servidor",
            "ip": "Dirección IP",
            "network_segment": "Segmento",
            "server_type": "Tipo",
            "os": "SO",
            "ram_gb": st.column_config.NumberColumn("RAM (GB)"),
            "cpu_cores": st.column_config.NumberColumn("Cores"),
            "has_backup": "Backup",
            "location": "Ubicación"
        }
    )
