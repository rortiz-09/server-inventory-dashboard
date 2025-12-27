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
        products = ['windows-server', 'ubuntu', 'redhat']
        data = {}
        
        try:
            for product in products:
                resp = requests.get(f"{API_URL}/{product}.json")
                if resp.status_code == 200:
                    cycles = resp.json()
                    # Mapear ciclo -> fecha EOL
                    data[product] = {
                        c['cycle']: c['eol'] for c in cycles
                    }
            
            # Guardar en Cache
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
        os_lower = str(os_name).lower()
        product = None
        version = None

        # Heurística simple de detección
        if 'windows' in os_lower:
            product = 'windows-server'
            # Extraer año (2008, 2012, 2016, 2019, 2022)
            for v in ['2022', '2019', '2016', '2012', '2008', '2003']:
                if v in os_lower:
                    version = v
                    break
        elif 'ubuntu' in os_lower:
            product = 'ubuntu'
            # Extraer XX.04
            import re
            match = re.search(r'(\d{2}\.04)', os_lower)
            if match:
                version = match.group(1)
        elif 'red hat' in os_lower or 'rhel' in os_lower:
            product = 'redhat'
            # RHEL 7, 8, 9
            import re
            match = re.search(r'release (\d+)', os_lower)
            if match:
                version = match.group(1)

        # Evaluar fecha
        if product and version and product in self.lifecycle_data:
            eol_str = self.lifecycle_data[product].get(version)
            if eol_str:
                if isinstance(eol_str, bool): # Support puede ser boleano false
                     return {'status': 'EOL', 'eol_date': 'Expired'}
                
                try:
                    eol_date = date.fromisoformat(eol_str)
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
