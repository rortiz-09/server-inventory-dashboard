import pandas as pd
import pytest
from src.core.cleaner import clean_data
from src.core.metrics import InventoryMetrics

@pytest.fixture
def raw_df():
    data = {
        'IP INTERNA': ['192.168.1.1', '192.168.1.2', '192.168.1.3', None],
        'HOSTNAME': ['srv1', 'srv2', 'srv3', None],
        'TIPO DE SERVIDOR': ['Virtual', 'Físico', 'Desconocido', None],
        'SISTEMA OPERATIVO': ['Windows 2019', 'RHEL 8', 'ESXi 7.0', None],
        'SISTEMAS CRITICOS': ['ALTO', None, 'BAJO', None],
        'BACKUP SE REALIZA': ['SI', 'NO', 'TRUE', None]
    }
    return pd.DataFrame(data)

def test_cleaner_columns(raw_df):
    cleaned = clean_data(raw_df)
    expected_cols = ['ip', 'hostname', 'server_type', 'os', 'criticality', 'has_backup']
    for col in expected_cols:
        assert col in cleaned.columns

def test_cleaner_normalization(raw_df):
    cleaned = clean_data(raw_df)
    
    # Server Type
    assert cleaned.iloc[0]['server_type'] == 'VIRTUAL'
    assert cleaned.iloc[1]['server_type'] == 'FISICO'
    
    # OS
    assert cleaned.iloc[0]['os'] == 'Windows'
    assert cleaned.iloc[1]['os'] == 'Linux'
    assert cleaned.iloc[2]['os'] == 'ESXi'
    
    # Backup (Boolean)
    assert cleaned.iloc[0]['has_backup'] == True
    assert cleaned.iloc[1]['has_backup'] == False
    assert cleaned.iloc[2]['has_backup'] == True

def test_metrics_logic(raw_df):
    cleaned = clean_data(raw_df)
    metrics = InventoryMetrics(cleaned)
    
    summary = metrics.get_summary()
    
    # We expect 3 valid rows (the None row should be dropped by cleaner or handled)
    # The cleaner logic: df.dropna(how='all') might keep row 3 if it has *some* data?
    # Wait, the None row in fixture has all Nones? Yes.
    # cleaner.py: df.dropna(how='all')
    
    assert summary['total'] == 3
    assert summary['pct_virtual'] == 33.3  # 1 out of 3
    assert summary['pct_backup_compliant'] == 66.67 # 2 out of 3 ("SI", "TRUE")
    assert summary['critical_servers'] == 1 # "ALTO"
