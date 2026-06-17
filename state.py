import pandas as pd
from typing import Dict, Optional
import flet as ft

class AppState:
    def __init__(self):
        self.excel_path: Optional[str] = None
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.page: Optional[ft.Page] = None

    def load_excel(self, path: str):
        """Carga todas las hojas del Excel en memoria."""
        try:
            xl = pd.ExcelFile(path)
            for sheet in xl.sheet_names:
                self.dataframes[sheet] = pd.read_excel(xl, sheet_name=sheet)
            self.excel_path = path
            return True, "Datos cargados correctamente."
        except Exception as e:
            return False, f"Error al cargar Excel: {e}"

    def get_df(self, sheet_name: str) -> Optional[pd.DataFrame]:
        """Obtiene un DataFrame específico."""
        return self.dataframes.get(sheet_name)

    def is_loaded(self) -> bool:
        return len(self.dataframes) > 0
