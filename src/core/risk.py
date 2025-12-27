"""
risk.py - Gestión de Obsolescencia y Riesgo (EOL)
Conecta con endoflife.date API para obtener ciclos de vida oficiales.
"""
import requests
import json
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional

CACHE_FILE = Path("data/eol_cache.json")
API_URL = "https://endoflife.date/api"

class RiskRadar:
    def __init__(self):
        self.lifecycle_data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Carga datos de ciclo de vida (desde caché o API)."""
        # 1. Intentar cargar cache si es reciente (< 24h)
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, 'r') as f:
                    cache = json.load(f)
                    cache_date = datetime.fromisoformat(cache['timestamp']).date()
                    if cache_date == date.today():
                        return cache['data']
            except Exception:
                pass # Cache corrupto o viejo, ignorar

        # 2. Fetch API (Solo productos clave para no saturar)
        products = ['windows-server', 'ubuntu', 'redhat', 'centos', 'debian', 'oracle-linux']
        data = {}
        
        try:
            for product in products:
                try:
                    resp = requests.get(f"{API_URL}/{product}.json", timeout=5)
                    if resp.status_code == 200:
                        cycles = resp.json()
                        # Mapear ciclo -> fecha EOL
                        data[product] = {
                            str(c['cycle']): c['eol'] for c in cycles
                        }
                    else:
                        print(f"Error HTTP {resp.status_code} para {product}")
                except Exception as req_err:
                     print(f"Error conectando para {product}: {req_err}")

            # Guardar en Cache si obtuvimos algo
            if data:
                CACHE_FILE.parent.mkdir(exist_ok=True)
                with open(CACHE_FILE, 'w') as f:
                    json.dump({'timestamp': date.today().isoformat(), 'data': data}, f)
                
        except Exception as e:
            print(f"Error fetching EOL data: {e}")
            
        return data

    def evaluate_os(self, os_name: str) -> Dict[str, Any]:
        """
        Evalúa el riesgo de un SO basado en su nombre.
        Retorna: { 'status': 'EOL'|'RISK'|'OK'|'UNKNOWN', 'eol_date': 'YYYY-MM-DD' }
        """
        if not os_name:
            return {'status': 'UNKNOWN', 'eol_date': None}

        # 1. Limpieza base
        os_clean = str(os_name).lower().replace(',', '.') # Fix "22,04", "8,9"
        
        product = None
        version = None
        
        import re

        # --- HEURÍSTICA AVANZADA (Basada en datos reales) ---
        
        # 1. WINDOWS SERVER
        if 'windows' in os_clean and 'server' in os_clean:
            product = 'windows-server'
            # Patterns: "server 2016", "server 2022", "server 2008"
            match = re.search(r'server\s+(\d{4})', os_clean)
            if match:
                version = match.group(1)
        
        # 2. UBUNTU
        elif 'ubuntu' in os_clean:
            product = 'ubuntu'
            # Patterns: "ubuntu 22.04", "ubuntu 22.04 lts", "ubuntu 20.04"
            match = re.search(r'(\d{2}\.\d{2})', os_clean)
            if match:
                version = match.group(1)

        # 3. RED HAT / RHEL
        elif 'red hat' in os_clean or 'rhel' in os_clean:
            product = 'redhat'
            # Patterns: "release 7.9", "release 6.10", "rhel 8.4", "linux 8.6"
            # Prioridad: Buscar version mayor (7, 8, 9)
            match = re.search(r'(?:release|rhel|linux)\s*?(\d{1,2})', os_clean)
            if match:
                version = match.group(1)
        
        # 4. ORACLE LINUX
        elif 'oracle linux' in os_clean:
             product = 'oracle-linux'
             # Patterns: "oracle linux 7.9", "oracle linux 7.6"
             match = re.search(r'linux\s*(\d{1,2})', os_clean)
             if match:
                 version = match.group(1)

        # 5. CENTOS
        elif 'centos' in os_clean:
            product = 'centos'
            # Patterns: "centos 7", "release 7.9", "release 5.9"
            match = re.search(r'(?:centos|release)\s*(\d{1})', os_clean)
            if match:
                version = match.group(1)
                
        # 6. DEBIAN
        elif 'debian' in os_clean:
            product = 'debian'
            # Patterns: "debian 12", "debian gnu/linux 12"
            match = re.search(r'debian\s*(?:gnu/linux\s*)?(\d+)', os_clean)
            if match:
                version = match.group(1)

        # --- EVALUACIÓN ---
        if product and version and product in self.lifecycle_data:
            version = str(version)
            eol_str = self.lifecycle_data[product].get(version)
            
            if eol_str:
                if isinstance(eol_str, bool): 
                     if eol_str is False:
                         return {'status': 'OK', 'eol_date': 'Supported'}
                     return {'status': 'EOL', 'eol_date': 'Expired'}
                
                try:
                    eol_date = date.fromisoformat(str(eol_str))
                    today = date.today()
                    days_to_eol = (eol_date - today).days
                    
                    if days_to_eol < 0:
                        return {'status': 'EOL', 'eol_date': eol_str}
                    elif days_to_eol < 365:
                        return {'status': 'RISK', 'eol_date': eol_str}
                    else:
                        return {'status': 'OK', 'eol_date': eol_str}
                except ValueError:
                    pass

        return {'status': 'UNKNOWN', 'eol_date': None}
