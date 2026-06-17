import pandas as pd
import os

def guardar_horario_optimizado(df_solucion: pd.DataFrame, ruta_original: str) -> tuple[bool, str]:
    """Guarda el DataFrame de solución optimizada en un archivo Excel."""
    try:
        df_solucion["observacion"] = "Correcta"
        
        directorio_original = os.path.dirname(ruta_original)
        ruta_salida = os.path.join(directorio_original, "Horario_Optimizado.xlsx")
        
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            df_solucion.to_excel(writer, sheet_name="Horario_Optimizado", index=False)
            
        return True, ruta_salida
    except Exception as e:
        return False, str(e)
