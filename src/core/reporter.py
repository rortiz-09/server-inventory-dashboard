"""
reporter.py - Generador de Reportes PDF
Genera un reporte ejecutivo en PDF usando fpdf2.
"""
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import tempfile
from typing import Dict, Any

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
    def header(self):
        # Logo placeholder (Texto)
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'REPORTE EJECUTIVO DE INFRAESTRUCTURA', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 10, f'Generado por: Ronny Ortiz el {fecha}', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, f'  {label}', 0, 1, 'L', True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()

    def kpi_grid(self, kpis: Dict[str, Any]):
        self.set_font('Arial', 'B', 10)
        
        # Fila 1
        self.cell(60, 10, f"Total Servidores: {kpis.get('total', 0)}", 1)
        self.cell(60, 10, f"Virtualización: {kpis.get('pct_virtual', 0)}%", 1)
        self.cell(60, 10, f"Compliance Backup: {kpis.get('cobertura_backup', 0)}%", 1)
        self.ln()
        
        # Fila 2
        self.cell(60, 10, f"Total RAM: {kpis.get('total_ram_gb', 0):,.0f} GB", 1)
        self.cell(60, 10, f"Total CPU: {kpis.get('total_cpu', 0):,.0f} Cores", 1)
        self.cell(60, 10, f"Calidad Datos: {kpis.get('calidad', 0)}%", 1)
        self.ln(10)

def generar_reporte_pdf(kpis: Dict[str, Any], top_apps: Dict[str, int]) -> bytes:
    """Crea el PDF y devuelve los bytes."""
    pdf = PDFReport()
    
    # 1. Resumen Ejecutivo
    pdf.chapter_title('1. Resumen Ejecutivo')
    pdf.chapter_body('Este reporte presenta el estado actual de la infraestructura de servidores, incluyendo métricas clave de capacidad, virtualización y cumplimiento operativo.')
    pdf.kpi_grid(kpis)
    
    # 2. Top Aplicaciones
    pdf.chapter_title('2. Top 10 Aplicaciones / Servicios')
    pdf.set_font('Arial', '', 9)
    # Header tabla
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(140, 7, 'Aplicación', 1, 0, 'L', True)
    pdf.cell(40, 7, 'Cantidad', 1, 1, 'C', True)
    
    for app, count in list(top_apps.items())[:10]:
        pdf.cell(140, 6, str(app)[:60], 1)
        pdf.cell(40, 6, str(count), 1, 1, 'C')
    
    pdf.ln(5)
    
    # 3. FinOps / Recomendación
    pdf.chapter_title('3. Observaciones')
    obs = (
        f"- Se requiere revisión de {kpis.get('duplicados', 0)} posibles registros duplicados.\n"
        f"- La cobertura de backup está al {kpis.get('cobertura_backup', 0)}%.\n"
        "- Se recomienda auditar los registros con información de Sistema Operativo faltante."
    )
    pdf.chapter_body(obs)
    
    # Salida a bytes directa (Streamlit requiere bytes, no bytearray)
    return bytes(pdf.output())
