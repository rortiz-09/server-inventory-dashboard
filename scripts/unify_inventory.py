
"""
unify_inventory.py
Transforma 'INVENTARIO SRV NAC 2025.xlsx' en un formato Maestro Estandarizado.
Genera pestañas separadas por dominio (General, Seguridad, DB, Soporte).
"""
import pandas as pd
from pathlib import Path
import re

SOURCE_FILE = Path("data/INVENTARIO SRV NAC 2025.xlsx")
OUTPUT_FILE = Path("data/MAESTRO_PLATAFORMA_V2.xlsx")

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
    
    # --- 1.5 Pre-procesamiento de Columnas (Coalesce) ---
    # El archivo origen separa SRV FISICOS y SRV VIRTUALES
    # Debemos unificarlos en HOSTNAME
    
    # Normalizar nombres de columnas que pueden variar
    col_fisico = next((c for c in df.columns if 'SRV FISICOS' in c and 'TOTAL' not in c), None)
    col_virtual = next((c for c in df.columns if 'SRV VIRTUALES' in c and '#' not in c), None)
    
    # Crear columna HOSTNAME combinada
    if col_fisico and col_virtual:
        # Prioridad: Si hay físico usa ese, sino virtual.
        # Pero ojo, pueden ser mutuamente excluyentes
        df['HOSTNAME'] = df[col_fisico].fillna(df[col_virtual])
    elif col_fisico:
        df['HOSTNAME'] = df[col_fisico]
    elif col_virtual:
        df['HOSTNAME'] = df[col_virtual]
    else:
        # Fallback si ya existe una columna HOSTNAME
        if 'HOSTNAME' not in df.columns:
            df['HOSTNAME'] = "SRV-DESCONOCIDO"

    # --- 2. Selección y Renombrado de Columnas ---
    
    # Mapeo de columnas originales -> Estandar (User Defined)
    mapping = {
        'HOSTNAME': 'HOSTNAME',
        'IP INTERNA': 'IP_ADDRESS',
        'TIPO DE SERVIDOR': 'TIPO',
        'SISTEMA OPERATIVO': 'OS',
        'APLICACIÓN': 'APLICACION',
        'APLICACIN': 'APLICACION',
        'MEMORIA': 'RAM_GB',
        'PROCESADOR': 'CPU',
        'PERSONA RESPONSABLE DEL USO DEL SRV': 'RESPONSABLE',
        'RESPONSABLE': 'RESPONSABLE',
        'ENCLOSURE': 'ENCLOSURE',
        'IP DEL BLADE': 'IP_ADMIN',

        'SERIE': 'SERIAL',
        'CARACTERISTICAS': 'MODELO',
        'CIUDAD': 'UBICACION',
        'SERVIDOR PRODUCCIN / PREPRODUCCIN': 'AMBIENTE',
        'SERVIDOR PRODUCCION / PREPRODUCCION': 'AMBIENTE',
        'SERVIDOR PRODUCCIÓN / PREPRODUCCIÓN': 'AMBIENTE',
        'AMBIENTE': 'AMBIENTE',
        'SISTEMAS CRITICOS': 'CRITICIDAD'
    }
    
    # Filtrar columnas que existen
    rename_dict = {}
    for col in df.columns:
        for key, val in mapping.items():
            if key == col: 
                rename_dict[col] = val
                break
    
    df_clean = df.rename(columns=rename_dict)
    
    # Limpieza de valores (RAM/CPU vacíos)
    if 'RAM_GB' not in df_clean.columns: df_clean['RAM_GB'] = None
    if 'CPU' not in df_clean.columns: df_clean['CPU'] = None
    
    # --- 3. Generación de Splits ---
    
    # A. SERVIDORES (Hoja Principal)
    # Debe contener todo lo necesario para el dashboard
    cols_main = ['HOSTNAME', 'IP_ADDRESS', 'TIPO', 'OS', 'RAM_GB', 'CPU', 'UBICACION', 'AMBIENTE', 'APLICACION', 'RESPONSABLE', 'CRITICIDAD']
    cols_main = [c for c in cols_main if c in df_clean.columns]
    df_servidores = df_clean[cols_main].copy()
    
    # B. APLICATIVOS (Vista de Negocio / Responsabilidad)
    # Agrupado por Aplicación y Responsable
    cols_app = ['APLICACION', 'RESPONSABLE', 'HOSTNAME', 'IP_ADDRESS', 'OS', 'RAM_GB', 'CPU']
    cols_app = [c for c in cols_app if c in df_clean.columns]
    df_aplicativos = df_clean.dropna(subset=['APLICACION'])[cols_app].sort_values(['APLICACION', 'RESPONSABLE'])

    # C. INFRA_FISICA (Hardware / Simplivity)
    # Filtrar solo físicos o columnas de hardware llenas
    cols_infra = ['HOSTNAME', 'IP_ADDRESS', 'ENCLOSURE', 'IP_ADMIN', 'SERIAL', 'MODELO', 'UBICACION']
    cols_infra = [c for c in cols_infra if c in df_clean.columns]
    
    # Criterio: Es Fisico O tiene Enclosure O tiene Serial
    mask_infra = (
        (df_clean['TIPO'].str.contains('FISICO', na=False, case=False)) | 
        (df_clean.get('ENCLOSURE', pd.Series([None]*len(df_clean))).notna()) |
        (df_clean.get('SERIAL', pd.Series([None]*len(df_clean))).notna())
    )
    df_infra = df_clean[mask_infra][cols_infra]
    
    # --- 4. Exportar Excel Maestro ---
    print(f"Generando {OUTPUT_FILE}...")
    with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
        df_servidores.to_excel(writer, sheet_name='SERVIDORES', index=False)
        df_aplicativos.to_excel(writer, sheet_name='APLICATIVOS', index=False)
        df_infra.to_excel(writer, sheet_name='INFRA_FISICA', index=False)
        
        # Formato Tabla
        for sheet_name, dframe in {'SERVIDORES': df_servidores, 'APLICATIVOS': df_aplicativos, 'INFRA_FISICA': df_infra}.items():
            worksheet = writer.sheets[sheet_name]
            (max_row, max_col) = dframe.shape
            options = {'columns': [{'header': col} for col in dframe.columns]}
            if max_row > 0:
                worksheet.add_table(0, 0, max_row, max_col - 1, options)
                worksheet.set_column(0, max_col - 1, 20)
                
    print("¡Estandarización completada!")

if __name__ == "__main__":
    main()
