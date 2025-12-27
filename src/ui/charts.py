"""
charts.py - Generación de Gráficos con Estilo Premium

Módulo encargado de crear visualizaciones impactantes, legibles y
con una paleta de colores vibrante y profesional.

Autor: Sistema de Gestión de Plataforma Xtrim
Fecha: Diciembre 2024
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any, List

# === PALETAS DE COLORES PREMIUM ===
# Colores vibrantes y de alto contraste
COLORS = {
    'primary': ['#2E86C1', '#1ABC9C', '#F39C12', '#E74C3C', '#8E44AD', '#34495E'],
    'status': {'SI': '#27AE60', 'NO': '#C0392B', '-': '#95A5A6'},
    'gradient': 'Viridis',  # Para mapas de calor o sunbursts
    'background': 'rgba(255,255,255,0)', # Transparente
    'text': '#2C3E50' # Gris oscuro para excelente legibilidad
}

def aplicar_tema(fig):
    """Aplica estilos globales para garantizar legibilidad y estética."""
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=14, color=COLORS['text']),
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        # Margen dinámico y generoso para evitar cortes
        margin=dict(t=50, b=50, l=50, r=50),
        uniformtext_minsize=10, 
        uniformtext_mode='hide',
        xaxis=dict(automargin=True),
        yaxis=dict(automargin=True),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor='rgba(255,255,255,0.5)',
            bordercolor='rgba(0,0,0,0.1)',
            borderwidth=1,
            font=dict(size=12)
        )
    )
    return fig

def crear_sunburst(df: pd.DataFrame, ruta: List[str], titulo: str) -> go.Figure:
    """Crea gráfico Sunburst jerárquico vibrante."""
    if df.empty:
        return go.Figure()

    # Rellenar nulos para visualización
    df_chart = df.copy()
    for col in ruta:
        df_chart[col] = df_chart[col].fillna('SIN DEFINIR')

    fig = px.sunburst(
        df_chart,
        path=ruta,
        color=ruta[1] if len(ruta) > 1 else ruta[0],
        color_discrete_sequence=COLORS['primary'],
        maxdepth=3
    )
    
    fig.update_traces(
        textinfo="label+percent entry",
        insidetextorientation='radial',
        marker=dict(line=dict(color='#FFFFFF', width=1)) 
    )
    
    # Sunburst no usa la leyenda estándar igual, pero ajustamos titulo
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b>", x=0.5, xanchor='center', font=dict(size=16)),
        margin=dict(t=40, b=10, l=10, r=10), # Sunburst necesita menos margen
        showlegend=False # Sunburst muestra jerarquía, no necesita leyenda lateral usualmente
    )
    
    return fig

def crear_treemap(df: pd.DataFrame, path: List[str], titulo: str) -> go.Figure:
    """Crea TreeMap estructurado y claro."""
    if df.empty:
        return go.Figure()
        
    df_chart = df.copy()
    for col in path:
        df_chart[col] = df_chart[col].fillna('?')

    fig = px.treemap(
        df_chart,
        path=path,
        color=path[1] if len(path) > 1 else path[0],
        color_discrete_sequence=COLORS['primary']
    )
    
    fig.update_traces(
        textinfo="label+value+percent root",
        marker=dict(line=dict(color='#FFFFFF', width=1))
    )
    
    fig.update_layout(title=dict(text=f"<b>{titulo}</b>", x=0.5))
    return aplicar_tema(fig)

def crear_grafico_barras_apiladas(df: pd.DataFrame, x_col: str, y_col: str, color_col: str, titulo: str) -> go.Figure:
    """Crea un gráfico de barras apiladas (Stacked Bar Chart)."""
    if df.empty:
        return go.Figure()
        
    fig = px.bar(
        df, 
        x=x_col, 
        y=y_col, 
        color=color_col, 
        title=titulo, 
        text_auto=True,
        color_discrete_map=COLORS['status'] # Usar mapa de colores si aplica
    )
    
    fig.update_traces(
        textfont_size=12, 
        textangle=0, 
        textposition="inside", 
        cliponaxis=False
    )
    
    fig.update_layout(
        barmode='stack',
        xaxis_title=x_col.capitalize(),
        yaxis_title="Cantidad",
        uniformtext_minsize=8, 
        uniformtext_mode='hide'
    )
    return aplicar_tema(fig)


def crear_grafico_pastel(datos: Dict[str, int], titulo: str) -> go.Figure:
    """Crea gráfico de pastel (Donut) moderno con etiquetas claras."""
    if not datos:
        return go.Figure()
        
    labels = list(datos.keys())
    values = list(datos.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        textinfo='label+percent+value', # Muestra TODO: Etiqueta, %, Valor
        textposition='outside',         # Textos afuera para evitar cortes internos
        marker=dict(colors=COLORS['primary'], line=dict(color='#FFFFFF', width=2))
    )])
    
    fig.update_layout(title=dict(text=f"<b>{titulo}</b>", x=0.5))
    return aplicar_tema(fig)

def crear_grafico_barras(datos: Dict[str, int], titulo: str, orientacion='v', color=None) -> go.Figure:
    """Crea gráfico de barras simple con valores visibles."""
    if not datos:
        return go.Figure()
        
    df = pd.DataFrame(list(datos.items()), columns=['Categoria', 'Valor'])
    
    x_col = 'Categoria' if orientacion == 'v' else 'Valor'
    y_col = 'Valor' if orientacion == 'v' else 'Categoria'
    
    fig = px.bar(
        df, 
        x=x_col, 
        y=y_col, 
        orientation=orientacion,
        text='Valor', # Mostrar valor explícitamente
        color_discrete_sequence=[color] if color else COLORS['primary']
    )
    
    fig.update_traces(
        textposition='outside', # Valor afuera de la barra
        textfont_size=12,
        cliponaxis=False        # Evitar que se corte si sale del eje
    )
    
    fig.update_layout(title=dict(text=f"<b>{titulo}</b>", x=0.5))
    return aplicar_tema(fig)

def crear_indicador_gauge(score: float, titulo: str) -> go.Figure:
    """Crea medidor tipo Gauge (velocímetro)."""
    
    color = "#E74C3C" # Rojo
    if score >= 50: color = "#F39C12" # Amarillo
    if score >= 85: color = "#27AE60" # Verde
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        title = {'text': f"<b>{titulo}</b>", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(231, 76, 60, 0.2)'},
                {'range': [50, 85], 'color': 'rgba(243, 156, 18, 0.2)'},
                {'range': [85, 100], 'color': 'rgba(39, 174, 96, 0.2)'}
            ],
        }
    ))
    
    fig.update_layout(height=250, margin=dict(t=40, b=10, l=20, r=20))
    return fig
