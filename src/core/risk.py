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
        products = ['windows-server', 'ubuntu', 'redhat', 'centos', 'debian']
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

        os_lower = str(os_name).lower()
        product = None
        version = None

        # --- HEURÍSTICA MEJORADA ---
        
        # 1. WINDOWS SERVER
        if 'windows' in os_lower:
            product = 'windows-server'
            # Extraer año (2008, 2012, 2016, 2019, 2022)
            # Orden inverso para evitar matches parciales si los hubiera
            for v in ['2025', '2022', '2019', '2016', '2012', '2008', '2003', '2000']:
                if v in os_lower:
                    version = v
                    # Caso especial: R2 (endoflife.date a veces distingue, a veces no. Para win serv, ciclo es "2012", no "2012 R2")
                    break
        
        # 2. UBUNTU
        elif 'ubuntu' in os_lower:
            product = 'ubuntu'
            import re
            # Busca XX.04 o XX.10
            match = re.search(r'(\d{2}\.\d{2})', os_lower)
            if match:
                version = match.group(1)
        
        # 3. RHEL / RED HAT
        elif 'red hat' in os_lower or 'rhel' in os_lower:
            product = 'redhat'
            import re
            # Busca numero entero principal: "Release 7", "RHEL 8.4" -> ciclo es "7", "8"
            match = re.search(r'(?:release|rhel)\s*(\d+)', os_lower)
            if not match: 
                 # Intento fallback simple: buscar digito suelto si dice "enterprise linux"
                 match = re.search(r'linux\s*(\d+)', os_lower)
            
            if match:
                version = match.group(1)
        
        # 4. CENTOS
        elif 'centos' in os_lower:
            product = 'centos'
            import re
            # CentOS 7, CentOS 8
            match = re.search(r'centos\s*(?:linux\s*)?(\d+)', os_lower)
            if match:
                version = match.group(1)
                
        # 5. DEBIAN
        elif 'debian' in os_lower:
            product = 'debian'
            import re
            # Debian 10, 11
            match = re.search(r'debian\s*(?:linux\s*)?(\d+)', os_lower)
            if match:
                version = match.group(1)

        # --- EVALUACIÓN ---
        if product and version and product in self.lifecycle_data:
            # Normalizar version a string
            version = str(version)
            
            # Caso especial RHEL/CentOS: API usa "7", "8" etc.
            
            eol_str = self.lifecycle_data[product].get(version)
            
            if eol_str:
                if isinstance(eol_str, bool): # False = no eol yet? or boolean support flag
                     # En endoflife.date, 'eol' puede ser booleano false si aun está vivo sin fecha? No, suele ser fecha o bool.
                     # Si es False, significa que no ha muerto.
                     if eol_str is False:
                         return {'status': 'OK', 'eol_date': 'Supported'}
                     return {'status': 'EOL', 'eol_date': 'Expired'}
                
                try:
                    # eol_str date format YYYY-MM-DD
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
                     # Si no es fecha ISO, asumimos texto informativo
                     pass

        return {'status': 'UNKNOWN', 'eol_date': None}
