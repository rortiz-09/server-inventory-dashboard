"""
cleaner.py - Módulo de Limpieza y Normalización de Datos

Este módulo transforma los datos crudos del Excel en un formato
estandarizado para su visualización en el dashboard.

Autor: Sistema de Gestión de Plataforma
Fecha: Diciembre 2024
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Any
from src.config import COLUMN_MAPPING, OS_MAPPING


def limpiar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Renombra las columnas del DataFrame según el mapeo definido en config.py.
    
    Args:
        df: DataFrame con columnas originales del Excel
        
    Returns:
        DataFrame con columnas renombradas y filtradas
    """
    # Limpiar espacios y saltos de línea en nombres de columna
    df.columns = df.columns.astype(str).str.strip().str.replace('\n', ' ')
    
    nuevas_columnas = {}
    for columna_actual in df.columns:
        columna_upper = columna_actual.upper()
        for nombre_visual, nombre_interno in COLUMN_MAPPING.items():
            # Comparar ignorando saltos de línea
            columna_limpia = columna_upper.replace('\n', ' ')
            if nombre_visual in columna_limpia:
                nuevas_columnas[columna_actual] = nombre_interno
                break
    
    df = df.rename(columns=nuevas_columnas)
    
    # === CORRECCIÓN CRÍTICA: Eliminar columnas duplicadas ===
    # Si múltiples columnas originales se mapean al mismo nombre (ej: has_backup),
    # pandas mantendrá ambas. Esto causa que df['col'] devuelva un DataFrame en lugar de Series.
    # Aquí nos quedamos solo con la primera ocurrencia de cada nombre de columna.
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Mantener solo columnas mapeadas + metadata
    columnas_a_mantener = list(set(nuevas_columnas.values())) + ['_source_sheet']
    columnas_a_mantener = [c for c in columnas_a_mantener if c in df.columns]
    
    return df[columnas_a_mantener]


def normalizar_tipo_servidor(valor: Any) -> str:
    """
    Normaliza el tipo de servidor a categorías estándar.
    
    Args:
        valor: Valor crudo de la columna TIPO DE SERVIDOR
        
    Returns:
        'VIRTUAL', 'FISICO' o 'OTRO'
    """
    if pd.isna(valor):
        return "OTRO"
    
    valor_str = str(valor).upper().strip()
    
    if "VIRTUAL" in valor_str:
        return "VIRTUAL"
    if "FISICO" in valor_str or "FÍSICO" in valor_str:
        return "FISICO"
    
    return "OTRO"


def normalizar_sistema_operativo(valor: Any) -> str:
    """
    Normaliza el sistema operativo a familias conocidas.
    
    Args:
        valor: Valor crudo de la columna SISTEMA OPERATIVO
        
    Returns:
        'Windows', 'Linux', 'ESXi' u 'Otro'
    """
    if pd.isna(valor):
        return "Otro"
    
    valor_str = str(valor).upper().strip()
    
    for clave, normalizado in OS_MAPPING.items():
        if clave in valor_str:
            return normalizado
    
    return "Otro"



def extraer_segmento_ip(valor: Any) -> str:
    """
    Extrae el segmento /24 de una dirección IP.
    
    Args:
        valor: Dirección IP (ej: '192.168.1.100')
        
    Returns:
        Segmento de red (ej: '192.168.1.x') o 'Sin IP'
    """
    if pd.isna(valor):
        return "Sin IP"
    
    valor_str = str(valor).strip()
    partes = valor_str.split('.')
    
    if len(partes) >= 3:
        return f"{partes[0]}.{partes[1]}.{partes[2]}.x"
    
    return "Formato Inválido"


def limpiar_texto(valor: Any, valor_defecto: str = "DESCONOCIDO") -> str:
    """
    Limpia y normaliza campos de texto.
    
    Args:
        valor: Valor crudo del campo
        valor_defecto: Valor a usar si está vacío o es nulo
        
    Returns:
        Texto limpio en mayúsculas o valor por defecto
    """
    if pd.isna(valor):
        return valor_defecto
    
    texto = str(valor).strip().upper()
    
    # Reemplazar valores nulos comunes
    if texto in ["NAN", "NONE", "N/A", "NA", ""]:
        return valor_defecto
    
    return texto


def mapear_ubicacion(valor: str) -> str:
    """
    Traduce códigos de ciudad a nombres completos.
    
    Args:
        valor: Código de ciudad (ej: 'UIO', 'GYE')
        
    Returns:
        Nombre completo de la ciudad
    """
    mapeo_ciudades = {
        'UIO': 'QUITO',
        'GYE': 'GUAYAQUIL',
        'CUE': 'CUENCA',
        'MAN': 'MANTA',
        'AMB': 'AMBATO'
    }
    return mapeo_ciudades.get(valor, valor)


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline principal de limpieza de datos.
    
    Aplica todas las transformaciones necesarias para preparar
    los datos del Excel para su visualización.
    
    Args:
        df: DataFrame crudo del Excel
        
    Returns:
        DataFrame limpio y normalizado
    """
    # Paso 1: Renombrar columnas según mapeo
    df = limpiar_nombres_columnas(df)
    
    # Paso 2: Garantizar que existan todas las columnas esperadas
    columnas_requeridas = {
        'server_type': 'OTRO',
        'os': 'Otro',
        'location': 'DESCONOCIDO',
        'datacenter': 'NO DEFINIDO',
        'criticality': 'No Clasificado',
        'has_backup': False,
        'application': 'DESCONOCIDO',
        'environment': 'DESCONOCIDO',
        'ip': None,
        'hostname': None,
        'public_ip': None
    }
    
    for columna, valor_defecto in columnas_requeridas.items():
        if columna not in df.columns:
            df[columna] = valor_defecto
    
    # Paso 3: Normalizar tipo de servidor
    df['server_type'] = df['server_type'].apply(normalizar_tipo_servidor)
    
    # Paso 4: Normalizar sistema operativo
    df['os'] = df['os'].apply(normalizar_sistema_operativo)
    
    # Paso 5: Limpiar campos de texto
    df['location'] = df['location'].apply(lambda x: limpiar_texto(x, 'DESCONOCIDO'))
    df['datacenter'] = df['datacenter'].apply(lambda x: limpiar_texto(x, 'NO DEFINIDO'))
    df['environment'] = df['environment'].apply(lambda x: limpiar_texto(x, 'DESCONOCIDO'))
    df['application'] = df['application'].apply(lambda x: limpiar_texto(x, 'DESCONOCIDO'))
    df['criticality'] = df['criticality'].apply(lambda x: limpiar_texto(x, 'NO CLASIFICADO'))
    
    # Paso 6: Mapear códigos de ubicación a nombres
    df['location'] = df['location'].apply(mapear_ubicacion)
    
    # Paso 7: Normalizar has_backup (TIENE BACKUP)
    if 'has_backup' in df.columns:
        col = df['has_backup']
        # Si es DataFrame (columnas duplicadas), tomar la primera
        if isinstance(col, pd.DataFrame):
            col = col.iloc[:, 0]
        
        # Lógica Específica: Null o Vacio -> "-"
        df['has_backup'] = col.fillna('-').astype(str).str.upper().str.strip()
        df['has_backup'] = df['has_backup'].replace({'NAN': '-', 'NONE': '-', '': '-'})
        
        # Estandarizar SI/NO
        # Si contiene SI/S/YES/TRUE/1 -> "SI"
        # Si es "-" -> "-"
        # Todo lo demas -> "NO"
        def normalizar_backup(val):
            if val == '-': return '-'
            if val in ['SI', 'S', 'YES', 'TRUE', '1']: return 'SI'
            return 'NO'
            
        df['has_backup'] = df['has_backup'].apply(normalizar_backup)
    
    # Paso 8: Clasificación de Segmentos de Red
    if 'ip' in df.columns:
        def clasificar_red(ip):
            if pd.isna(ip) or str(ip).strip() == '':
                return 'SIN IP'
            ip_str = str(ip).strip()
            
            if '192.168.59.' in ip_str: return 'PROD GUAYAQUIL'
            if '192.168.21.' in ip_str: return 'PROD QUITO'
            if '192.168.76.' in ip_str: return 'TEST'
            if '192.168.77.' in ip_str: return 'DESARROLLO'
            
            # Extraer segmento generico si no coincide
            dots = ip_str.split('.')
            if len(dots) == 4 and all(p.isdigit() for p in dots):
                return f"OTRO ({dots[0]}.{dots[1]}.{dots[2]}.x)"
            return 'OTRO SEGMENTO'

        df['network_segment'] = df['ip'].apply(clasificar_red)
        
        # Extraer segmento /24 para análisis técnico también
        df['ip_segment'] = df['ip'].apply(extraer_segmento_ip)
    
    # Paso 9: Limpiar hostname (convertir None a string legible)
    
    # Conversión explícita de tipos para evitar errores de Arrow
    if 'ip' in df.columns:
        df['ip'] = df['ip'].astype(str)
        
    return df


# Alias para compatibilidad
clean_data = limpiar_datos


