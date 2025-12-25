import pandas as pd
from typing import Optional, Union, BinaryIO
from io import BytesIO
from src.config import COLUMN_MAPPING

def find_header_row(df: pd.DataFrame, keywords: list[str], max_rows: int = 20) -> Optional[int]:
    """
    Scans the first 'max_rows' of the DataFrame to find a row containing
    a significant number of expected keywords.
    """
    keywords_lower = [k.lower() for k in keywords]
    
    for i in range(min(max_rows, len(df))):
        row_values = df.iloc[i].astype(str).str.lower().tolist()
        match_count = sum(1 for k in keywords_lower if any(k in val for val in row_values))
        
        if match_count >= 2:
            return i
            
    return None

def load_data(file_source: Union[str, BinaryIO]) -> pd.DataFrame:
    """
    Loads dynamically searching for the header row.
    Accepts file path (str) or file-like object (BytesIO).
    """
    try:
        xl = pd.ExcelFile(file_source)
        all_dfs = []
        
        target_sheets = [s for s in xl.sheet_names if "2025" in s]
        if not target_sheets:
            target_sheets = xl.sheet_names

        print(f"Loading sheets: {target_sheets}")

        for sheet in target_sheets:
            raw_preview = pd.read_excel(file_source, sheet_name=sheet, header=None, nrows=30)
            required_headers = list(COLUMN_MAPPING.keys())
            header_idx = find_header_row(raw_preview, required_headers)
            
            if header_idx is None:
                print(f"Warning: Could not find header in sheet {sheet}. Skipping.")
                continue
                
            df = pd.read_excel(file_source, sheet_name=sheet, header=header_idx)
            df['_source_sheet'] = sheet
            all_dfs.append(df)
            
        if not all_dfs:
            raise ValueError("No valid data found in any sheet.")
            
        final_df = pd.concat(all_dfs, ignore_index=True)
        return final_df
        
    except Exception as e:
        raise RuntimeError(f"Error loading Excel file: {e}")
