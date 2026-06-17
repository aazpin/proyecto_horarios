import pandas as pd
import random

def calcular_penalizaciones(df):
    penalizacion_aula = 0
    penalizacion_docente = 0
    penalizacion_infraestructura = 0
    penalizacion_capacidad = 0
    detalles = []

    df_eval = df.dropna(subset=["dia", "id_bloque", "aula", "docente"])

    duplicados_aula = df_eval[df_eval.duplicated(subset=["dia", "id_bloque", "aula"], keep=False)]
    if not duplicados_aula.empty:
        for (d, b, a), grupo in duplicados_aula.groupby(["dia", "id_bloque", "aula"]):
            penalizacion_aula += 100 * (len(grupo) - 1)
            detalles.append(f"Choque Aula {a} ({d} - Bloque {b})")

    duplicados_docente = df_eval[df_eval.duplicated(subset=["dia", "id_bloque", "docente"], keep=False)]
    if not duplicados_docente.empty:
        for (d, b, doc), grupo in duplicados_docente.groupby(["dia", "id_bloque", "docente"]):
            penalizacion_docente += 100 * (len(grupo) - 1)
            detalles.append(f"Cruce Docente {doc} ({d} - Bloque {b})")

    for index, fila in df_eval.iterrows():
        req_lab = str(fila.get("requiere_laboratorio", "")).strip().upper()
        tipo_a = str(fila.get("tipo_aula", "")).strip().upper()
        
        if req_lab in ["SÍ", "SI"]:
            if "LABORATORIO" not in tipo_a:
                penalizacion_infraestructura += 100
                detalles.append(f"Error Infraestructura: {fila['asignatura']} requiere Laboratorio.")

        try:
            num_est = int(fila.get("num_estudiantes", 0))
            cap_aula = int(fila.get("capacidad_aula", 0))
            if num_est > cap_aula:
                penalizacion_capacidad += 100
                detalles.append(f"Error Capacidad: {fila['asignatura']} supera a {fila['aula']}.")
        except:
            pass

    total_penalizacion = penalizacion_aula + penalizacion_docente + penalizacion_infraestructura + penalizacion_capacidad
    return total_penalizacion, detalles, penalizacion_aula, penalizacion_docente, penalizacion_infraestructura, penalizacion_capacidad
