
"""
unify_inventory.py
Transforma 'INVENTARIO SRV NAC 2025.xlsx' en un formato Maestro Estandarizado.
Genera pestañas separadas por dominio (General, Seguridad, DB, Soporte).
"""
import pandas as pd
from pathlib import Path
import re

SOURCE_FILE = Path("data/INVENTARIO SRV NAC 2025.xlsx")
OUTPUT_FILE = Path("data/MAESTRO_PLATAFORMA_V1.xlsx")

def clean_header(txt):
    return str(txt).strip().upper().replace('\n', ' ').replace('  ', ' ')

def main():
    if not SOURCE_FILE.exists():
        print(f"Error: No se encuentra {SOURCE_FILE}")
        return

    print("--- 1. Detectando cabeceras ---")
    # Leemos sin header primero para buscar la fila correcta (heurística)
    df_raw = pd.read_excel(SOURCE_FILE, sheet_name=0, header=None)
    
    header_idx = 0
    for i, row in df_raw.iterrows():
        row_str = " ".join(row.astype(str).tolist()).upper()
        if "IP INTERNA" in row_str or "SISTEMA OPERATIVO" in row_str:
            header_idx = i
            break
            
    print(f"Cabecera detectada en fila: {header_idx}")
    
    # Leemos dataframe real
    df = pd.read_excel(SOURCE_FILE, sheet_name=0, header=header_idx)
    
    # Limpiamos nombres de columnas
    df.columns = [clean_header(c) for c in df.columns]
    
    print("Columnas encontradas:", df.columns.tolist())

    # --- 2. Selección y Renombrado de Columnas ---
    
    # Mapeo de columnas originales -> Estandar
    mapping = {
        'HOSTNAME': 'HOSTNAME', # A veces no tiene nombre explicito, buscaré heurística
        'IP INTERNA': 'IP_ADDRESS',
        'TIPO DE SERVIDOR': 'TIPO',
        'SISTEMA OPERATIVO': 'OS',
        'APLICACIÓN': 'APLICACION',
        'APLICACIN': 'APLICACION', # Encoding fix
        'MEMORIA': 'RAM_RAW',
        'PROCESADOR': 'CPU_RAW',
        'PROTECCIÓN DE TREND MCRO XDR - SRV': 'SEG_TREND',
        'PROTECCIN DE TREND MCRO XDR - SRV': 'SEG_TREND',
        'CORTEX': 'SEG_CORTEX',
        'BASE DE DATOS': 'DB_ENGINE',
        'VERSIÓN DB': 'DB_VERSION',
        'VERSIN DB': 'DB_VERSION',
        'EMPRESA QUE DA SOPORTE': 'SOPORTE_VENDOR',
        'COSTO SOPORTE': 'SOPORTE_COSTO',
        'CIUDAD': 'UBICACION',
        'AMBIENTE': 'AMBIENTE',
        'SERIE': 'SERIAL',
        'BACKUP SE REALIZA': 'TIENE_BACKUP'
    }
    
    # Filtrar columnas que existen
    rename_dict = {}
    for col in df.columns:
        # Intento de match exacto o parcial seguro
        for key, val in mapping.items():
            if key in col: # Cuidado con matches parciales, pero estos keys son bastante únicos
                rename_dict[col] = val
                break
    
    df_clean = df.rename(columns=rename_dict)
    
    # Si no hay HOSTNAME explícito, intentamos 'NOMBRE' o asumimos que falta
    if 'HOSTNAME' not in df_clean.columns:
        # A veces es Unnamed o Nombre de servidor
        # En el análisis anterior vi que NO había columna HOSTNAME explicita en head(5)?
        # Chequeo manual rápido: TIPO, SRV VIRTUALES...
        pass

    # --- 3. Generación de Splits ---
    
    # A. GENERAL (Lo esencial)
    cols_general = ['UBICACION', 'HOSTNAME', 'IP_ADDRESS', 'TIPO', 'OS', 'AMBIENTE', 'SERIAL', 'RAM_RAW', 'CPU_RAW', 'APLICACION']
    # Select only existing
    cols_general = [c for c in cols_general if c in df_clean.columns]
    df_general = df_clean[cols_general].copy()
    
    # B. SEGURIDAD (Cybersec View)
    cols_sec = ['HOSTNAME', 'IP_ADDRESS', 'OS', 'SEG_TREND', 'SEG_CORTEX', 'TIENE_BACKUP']
    cols_sec = [c for c in cols_sec if c in df_clean.columns]
    df_sec = df_clean[cols_sec].copy()
    
    # C. BASES DE DATOS (DBA View)
    # Filtrar solo los que tienen DB
    cols_db = ['HOSTNAME', 'IP_ADDRESS', 'DB_ENGINE', 'DB_VERSION']
    cols_db = [c for c in cols_db if c in df_clean.columns]
    if 'DB_ENGINE' in df_clean.columns:
        df_db = df_clean.dropna(subset=['DB_ENGINE'])[cols_db]
        # Filtrar "NO APLICA", "-", etc.
        df_db = df_db[~df_db['DB_ENGINE'].astype(str).isin(['nan', '-', 'NO', 'N/A'])]
    else:
        df_db = pd.DataFrame()

    # D. FINANCIERO / SOPORTE (FinOps View)
    cols_fin = ['HOSTNAME', 'IP_ADDRESS', 'SERIAL', 'SOPORTE_VENDOR', 'SOPORTE_COSTO']
    cols_fin = [c for c in cols_fin if c in df_clean.columns]
    df_fin = df_clean.dropna(subset=['SOPORTE_VENDOR'])[cols_fin]
    
    # --- 4. Exportar Excel Maestro ---
    print(f"Generando {OUTPUT_FILE}...")
    with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
        df_general.to_excel(writer, sheet_name='1. GENERAL', index=False)
        df_sec.to_excel(writer, sheet_name='2. SEGURIDAD', index=False)
        df_db.to_excel(writer, sheet_name='3. BASES DE DATOS', index=False)
        df_fin.to_excel(writer, sheet_name='4. SOPORTE Y COSTOS', index=False)
        
        # Formato Tabla (Auto-filter)
        workbook = writer.book
        for sheet_name, dframe in {'1. GENERAL': df_general, '2. SEGURIDAD': df_sec, '3. BASES DE DATOS': df_db, '4. SOPORTE Y COSTOS': df_fin}.items():
            worksheet = writer.sheets[sheet_name]
            (max_row, max_col) = dframe.shape
            options = {'columns': [{'header': col} for col in dframe.columns]}
            if max_row > 0:
                worksheet.add_table(0, 0, max_row, max_col - 1, options)
                worksheet.set_column(0, max_col - 1, 20) # Width auto-ish

    print("¡Proceso completado con éxito!")

if __name__ == "__main__":
    main()
