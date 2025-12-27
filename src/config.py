"""
config.py - Configuración Central del Dashboard

Define paths, mapeo de columnas y valores normalizados.

Autor: Sistema de Gestión de Plataforma Xtrim
Fecha: Diciembre 2024
"""

from pathlib import Path

# === RUTAS ===
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Archivo principal: INVENTARIO SRV.xlsx (274 registros oficiales)
EXCEL_FILE = DATA_DIR / "INVENTARIO SRV.xlsx"


# === MAPEO DE COLUMNAS ===
# Mapea nombres del Excel a nombres internos estandarizados
COLUMN_MAPPING = {
    # Identificación
    "IP INTERNA": "ip",
    "IP PUBLICA": "public_ip",
    "HOSTNAME": "hostname",
    
    # Clasificación
    "TIPO DE SERVIDOR": "server_type",
    "SISTEMA OPERATIVO": "os",
    "UBICACION": "location",
    "LOCATION": "location",
    "DATA CENTER": "datacenter",
    
    # Recursos (para futuro)
    "RAM": "ram_gb",
    "RAM (GB)": "ram_gb",
    "MEMORIA RAM": "ram_gb",
    "MEMORIA": "ram_gb", # Added
    "CPU": "cpu_cores",
    "CPU CORES": "cpu_cores",
    "PROCESADOR": "cpu_cores", # Added
    
    # Operación
    "SERVIDOR PRODUCCIÓN / PREPRODUCCIÓN": "environment",
    "AMBIENTE": "environment",
    "PRODUCCION": "environment", # Added
    "APLICACIÓN": "application",
    "APLICACION": "application",
    "BASE DE DATOS": "database_engine", # Added
    "VERSION DB": "database_version", # Added
    
    # Riesgo y Compliance
    "SISTEMAS CRITICOS": "criticality",
    "CRITICIDAD": "criticality",
    "BACKUP": "has_backup",
    "BACKUP SE REALIZA": "has_backup",
    "TIENE BACKUP": "has_backup",
    "PLATAFORMA BACKUP": "backup_platform",
    "PLATAFORMA DE BACKUP": "backup_platform",
    
    # Soporte (para futuro)
    "PROVEEDOR SOPORTE": "support_vendor",
    "EMPRESA SOPORTE": "support_vendor",
}


# === NORMALIZACIÓN DE VALORES ===
OS_MAPPING = {
    "WIN": "Windows",
    "WINDOWS": "Windows",
    "LINUX": "Linux",
    "RHEL": "Linux",
    "UBUNTU": "Linux",
    "CENTOS": "Linux",
    "DEBIAN": "Linux",
    "ORACLE LINUX": "Linux",
    "ESXI": "ESXi",
    "VMWARE": "ESXi",
}
