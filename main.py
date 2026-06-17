from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import random
import os

app = FastAPI(title="API de Optimización de Horarios Profesional")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        req_lab = str(fila.get("requiere_laboratorio")).strip().upper()
        tipo_a = str(fila.get("tipo_aula")).strip().upper()
        
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


@app.post("/evaluar")
async def evaluar_horario(file: UploadFile = File(...)):
    try:
        df_horario = pd.read_excel(file.file, sheet_name="Horario_Inicial")
        total, detalles, p_aula, p_doc, p_infra, p_cap = calcular_penalizaciones(df_horario)
        return {
            "status": "success",
            "penalizacion_total": total,
            "desglose": {"choques_aula": p_aula, "cruces_docente": p_doc, "errores_laboratorio": p_infra, "errores_capacidad": p_cap},
            "conflictos_detectados": detalles
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- OPTIMIZAR Y DESCARGAR EXCEL DIRECTAMENTE ---
@app.post("/optimizar")
async def optimizar_horario(file: UploadFile = File(...)):
    try:
        df_solucion = pd.read_excel(file.file, sheet_name="Horario_Inicial")
        
        catalogo_aulas = {}
        for idx, row in df_solucion.dropna(subset=["aula"]).iterrows():
            catalogo_aulas[row["aula"]] = (row["tipo_aula"], row["capacidad_aula"])
            
        aulas_nombres = list(catalogo_aulas.keys())
        bloques_disponibles = df_solucion["id_bloque"].dropna().unique().tolist()
        dias_disponibles = df_solucion["dia"].dropna().unique().tolist()

        penalizacion_actual, _, _, _, _, _ = calcular_penalizaciones(df_solucion)
        
        max_iteraciones = 1000
        iteracion = 0
        
        while penalizacion_actual > 0 and iteracion < max_iteraciones:
            df_candidato = df_solucion.copy()
            fila_al_azar = random.choice(df_candidato.index)
            
            if random.random() < 0.5:
                aula_elegida = random.choice(aulas_nombres)
                tipo_u, cap_u = catalogo_aulas[aula_elegida]
                df_candidato.at[fila_al_azar, "aula"] = aula_elegida
                df_candidato.at[fila_al_azar, "tipo_aula"] = tipo_u
                df_candidato.at[fila_al_azar, "capacidad_aula"] = cap_u
            else:
                df_candidato.at[fila_al_azar, "id_bloque"] = random.choice(bloques_disponibles)
                df_candidato.at[fila_al_azar, "dia"] = random.choice(dias_disponibles)

            nueva_penalizacion, _, _, _, _, _ = calcular_penalizaciones(df_candidato)
            
            if nueva_penalizacion < penalizacion_actual:
                df_solucion = df_candidato
                penalizacion_actual = nueva_penalizacion
            
            iteracion += 1

        # Actualizar la columna de observaciones en las filas optimizadas
        df_solucion["observacion"] = "Correcta"

        # RUTA DONDE SE GUARDARÁ EL ARCHIVO TEMPORAL EN TU PC
        ruta_salida = "Horario_Optimizado.xlsx"
        
        # Guardamos el DataFrame limpio de nuevo a un archivo Excel real
        with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
            df_solucion.to_excel(writer, sheet_name="Horario_Optimizado", index=False)

        # Retornamos el archivo físico para que el navegador lo descargue automáticamente
        return FileResponse(
            path=ruta_salida, 
            filename="Horario_Optimizado.xlsx", 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        return {"status": "error", "message": f"Error en la optimización: {str(e)}"}
