"""
metrics.py - Metricas Ejecutivas del Inventario

Calcula KPIs y estadisticas para reportes gerenciales.

Autor: Sistema de Gestion de Plataforma Xtrim
Fecha: Diciembre 2024
"""

import pandas as pd
from typing import Dict, Any


class MetricasInventario:
    """Calcula metricas ejecutivas del inventario de servidores."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    @property
    def total_servidores(self) -> int:
        return int(len(self.df))
    
    @property
    def datos_crudos(self) -> pd.DataFrame:
        return self.df
    
    total_servers = total_servidores
    raw_data = datos_crudos
    
    # === DISTRIBUCIONES ===
    
    @property
    def distribucion_tipo_servidor(self) -> Dict[str, int]:
        if 'server_type' not in self.df.columns:
            return {}
        return self.df['server_type'].value_counts().to_dict()
    
    physical_vs_virtual = distribucion_tipo_servidor
    
    @property
    def distribucion_so(self) -> Dict[str, int]:
        if 'os' not in self.df.columns:
            return {}
        return self.df['os'].value_counts().to_dict()
    
    os_distribution = distribucion_so
    
    @property
    def distribucion_ubicacion(self) -> Dict[str, int]:
        if 'location' not in self.df.columns:
            return {}
        return self.df['location'].value_counts().to_dict()
    
    location_distribution = distribucion_ubicacion
    
    @property
    def distribucion_datacenter(self) -> Dict[str, int]:
        if 'datacenter' not in self.df.columns:
            return {}
        return self.df['datacenter'].value_counts().to_dict()
    
    datacenter_distribution = distribucion_datacenter
    
    @property
    def distribucion_ambiente(self) -> Dict[str, int]:
        if 'environment' not in self.df.columns:
            return {}
        return self.df['environment'].value_counts().to_dict()
    
    environment_distribution = distribucion_ambiente
    
    @property
    def distribucion_criticidad(self) -> Dict[str, int]:
        if 'criticality' not in self.df.columns:
            return {}
        return self.df['criticality'].value_counts().to_dict()
    
    criticality_breakdown = distribucion_criticidad
    
    @property
    def distribucion_segmento_ip(self) -> Dict[str, int]:
        if 'ip_segment' not in self.df.columns:
            return {}
        return self.df['ip_segment'].value_counts().head(10).to_dict()
    
    ip_segment_distribution = distribucion_segmento_ip

    @property
    def distribucion_segmento_red(self) -> Dict[str, int]:
        if 'network_segment' not in self.df.columns:
            return {}
        return self.df['network_segment'].value_counts().to_dict()

    @property
    def top_aplicaciones(self) -> Dict[str, int]:
        if 'application' not in self.df.columns:
            return {}
        apps = self.df[self.df['application'] != 'DESCONOCIDO']['application']
        if apps.empty:
            return {'Sin Informacion': int(len(self.df))}
        return apps.value_counts().head(10).to_dict()
    
    top_applications = top_aplicaciones
    
    @property
    def backup_por_ambiente(self) -> pd.DataFrame:
        """Retorna DataFrame con conteo de backups por ambiente."""
        if 'environment' not in self.df.columns or 'has_backup' not in self.df.columns:
            return pd.DataFrame()
            
        # Agrupar por ambiente y estado de backup
        df_group = self.df.groupby(['environment', 'has_backup']).size().reset_index(name='count')
        return df_group
    
    # === METRICAS DE BACKUP ===
    
    @property
    def cobertura_backup(self) -> float:
        """Porcentaje de servidores con backup configurado."""
        if 'has_backup' not in self.df.columns:
            return 0.0
        total = len(self.df)
        if total == 0:
            return 0.0
        # Contar valores 'SI' (string)
        con_backup = int((self.df['has_backup'] == 'SI').sum())
        return round(float(con_backup) / float(total) * 100.0, 1)
    
    # === METRICAS DE CALIDAD ===
    
    @property
    def duplicados_potenciales(self) -> int:
        cols = []
        if 'hostname' in self.df.columns:
            cols.append('hostname')
        if 'ip' in self.df.columns:
            cols.append('ip')
        if not cols:
            return 0
        return int(self.df.duplicated(subset=cols, keep=False).sum())
    
    potential_duplicates = duplicados_potenciales
    
    @property
    def score_calidad_datos(self) -> float:
        campos = ['ip', 'hostname', 'os']
        campos_existentes = [c for c in campos if c in self.df.columns]
        if not campos_existentes:
            return 0.0
        
        total_celdas = len(self.df) * len(campos_existentes)
        if total_celdas == 0:
            return 100.0
        
        vacias = 0
        for col in campos_existentes:
            vacias += int(self.df[col].isna().sum())
            vacias += int((self.df[col].astype(str).isin(['None', 'NaN', 'SIN HOSTNAME', 'Sin IP'])).sum())
        
        return round(max(0.0, 1.0 - float(vacias)/float(total_celdas)) * 100.0, 1)
    
    data_quality_score = score_calidad_datos
    
    # === CONTEO ===
    
    @property
    def servidores_virtuales(self) -> int:
        if 'server_type' not in self.df.columns:
            return 0
        return int((self.df['server_type'] == 'VIRTUAL').sum())
    
    @property
    def servidores_fisicos(self) -> int:
        if 'server_type' not in self.df.columns:
            return 0
        return int((self.df['server_type'] == 'FISICO').sum())
    
    @property
    def con_respaldo(self) -> int:
        if 'has_backup' not in self.df.columns:
            return 0
        return int((self.df['has_backup'] == 'SI').sum())
    
    veritas_count = con_respaldo
    
    @property
    def ubicaciones_unicas(self) -> int:
        if 'location' not in self.df.columns:
            return 0
        return int(self.df['location'].nunique())
    
    # === METRICAS DE RECURSOS ===
    
    @property
    def total_ram_gb(self) -> float:
        if 'ram_gb' not in self.df.columns:
            return 0.0
        val = self.df['ram_gb'].sum()
        return float(val) if pd.notna(val) else 0.0
    
    @property
    def total_cpu_cores(self) -> int:
        if 'cpu_cores' not in self.df.columns:
            return 0
        val = self.df['cpu_cores'].sum()
        return int(val) if pd.notna(val) else 0
    
    # === RESUMEN EJECUTIVO ===
    
    def obtener_resumen(self) -> Dict[str, Any]:
        total = self.total_servidores
        virtuales = self.servidores_virtuales
        fisicos = self.servidores_fisicos
        
        return {
            'total': int(total),
            'virtuales': int(virtuales),
            'fisicos': int(fisicos),
            'pct_virtual': round(float(virtuales) / float(total) * 100.0, 1) if total > 0 else 0.0,
            'pct_fisico': round(float(fisicos) / float(total) * 100.0, 1) if total > 0 else 0.0,
            'ubicaciones': int(self.ubicaciones_unicas),
            'calidad': float(self.score_calidad_datos),
            'duplicados': int(self.duplicados_potenciales),
            'cobertura_backup': float(self.cobertura_backup),
            'total_ram_gb': float(self.total_ram_gb),
            'total_cpu': int(self.total_cpu_cores),
        }
    
    get_summary = obtener_resumen


# Alias de clase
InventoryMetrics = MetricasInventario
