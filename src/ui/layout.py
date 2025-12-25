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

    # ROW 6: TABLA DETALLADA
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
