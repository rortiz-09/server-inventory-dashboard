"""
comparator.py - Lógica de Comparación Histórica (Time Machine)
Calcula deltas entre dos snapshots de inventario.
"""
import pandas as pd
from typing import Dict, Any, List
from src.core.metrics import InventoryMetrics

class InventoryComparator:
    def __init__(self, current: InventoryMetrics, previous: InventoryMetrics):
        self.current = current
        self.previous = previous
        
    def _extract_keys(self, df: pd.DataFrame) -> set:
        """Extrae identificadores únicos (Hostname o IP)."""
        if 'hostname' in df.columns and not df['hostname'].isna().all():
            return set(df['hostname'].dropna().unique())
        if 'ip' in df.columns:
            return set(df['ip'].dropna().unique())
        return set()

    def calculate_changes(self) -> Dict[str, Any]:
        """
        Genera reporte de Altas, Bajas y Cambios.
        """
        # Obtener sets de identificadores
        curr_keys = self._extract_keys(self.current.df)
        prev_keys = self._extract_keys(self.previous.df)
        
        # Calcular deltas de existencia
        added = curr_keys - prev_keys
        removed = prev_keys - curr_keys
        retained = curr_keys & prev_keys
        
        # Calcular MODIFICACIONES en retenidos
        modified = []
        for key in retained:
            # Buscar fila en ambos DFs (asumiendo unicidad por key, o tomando el primero)
            # Usamos hostname como key principal
            row_curr = self.current.df[self.current.df['hostname'] == key].iloc[0]
            row_prev = self.previous.df[self.previous.df['hostname'] == key].iloc[0]
            
            changes = []
            
            # 1. Cambio de OS
            if str(row_curr.get('os')) != str(row_prev.get('os')):
                changes.append(f"OS: {row_prev.get('os')} -> {row_curr.get('os')}")
                
            # 2. Cambio de IP
            if str(row_curr.get('ip')) != str(row_prev.get('ip')):
                changes.append(f"IP: {row_prev.get('ip')} -> {row_curr.get('ip')}")
                
            # 3. Cambio de RAM
            if row_curr.get('ram_gb') != row_prev.get('ram_gb'):
                changes.append(f"RAM: {row_prev.get('ram_gb')}GB -> {row_curr.get('ram_gb')}GB")
                
            # 4. Cambio de Estado (Backup)
            if row_curr.get('has_backup') != row_prev.get('has_backup'):
                 changes.append(f"Backup: {row_prev.get('has_backup')} -> {row_curr.get('has_backup')}")

            if changes:
                modified.append({
                    'hostname': key,
                    'changes': "; ".join(changes)
                })

        # Calcular variaciones de KPIs
        curr_kpis = self.current.obtener_resumen()
        prev_kpis = self.previous.obtener_resumen()
        
        delta_total = curr_kpis['total'] - prev_kpis['total']
        delta_virtual = curr_kpis['pct_virtual'] - prev_kpis['pct_virtual']
        
        return {
            'summary': {
                'added_count': len(added),
                'removed_count': len(removed),
                'modified_count': len(modified),
                'net_change': delta_total,
                'retained_count': len(retained)
            },
            'details': {
                'added_hosts': sorted(list(added)),
                'removed_hosts': sorted(list(removed)),
                'modified_hosts': modified 
            },
            'kpi_deltas': {
                'total_servers': delta_total,
                'virtualization_pct': delta_virtual,
                'backup_coverage': curr_kpis['cobertura_backup'] - prev_kpis['cobertura_backup']
            }
        }
