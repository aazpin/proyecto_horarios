import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestión de Horarios Académicos", page_icon="🎓", layout="wide")

@st.cache_data
def load_data(filepath: str):
    """Carga los DataFrames desde el archivo Excel."""
    try:
        df_docentes = pd.read_excel(filepath, sheet_name="Docentes")
        xls = pd.ExcelFile(filepath)
        if "Horario_Optimizado" in xls.sheet_names:
            df_horario = pd.read_excel(xls, sheet_name="Horario_Optimizado")
        elif "Horario_Inicial" in xls.sheet_names:
            df_horario = pd.read_excel(xls, sheet_name="Horario_Inicial")
        else:
            df_horario = pd.DataFrame()
            
        return df_docentes, df_horario
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

# =======================
# INICIALIZACIÓN DE ESTADO
# =======================
EXCEL_PATH = "HOARIO AP METAHEURISTICA.xlsx"

if not os.path.exists(EXCEL_PATH):
    st.error(f"No se encontró el archivo '{EXCEL_PATH}'. Asegúrese de que esté en el mismo directorio.")
    st.stop()

# Cargar a variables locales solo para inicializar el estado
df_docentes_init, df_horario_init = load_data(EXCEL_PATH)

if df_docentes_init.empty:
    st.warning("No se encontraron docentes en el archivo.")
    st.stop()

# Implementación de st.session_state.horarios_df
if 'horarios_df' not in st.session_state:
    st.session_state.horarios_df = df_horario_init.copy()
if 'df_docentes' not in st.session_state:
    st.session_state.df_docentes = df_docentes_init.copy()

# Referencias para facilidad de uso
horarios_df = st.session_state.horarios_df
df_docentes = st.session_state.df_docentes

# =======================
# CATÁLOGOS AUTOMÁTICOS
# =======================
lista_asignaturas = sorted(df_horario_init['asignatura'].dropna().unique().tolist())
lista_aulas = sorted(df_horario_init['aula'].dropna().unique().astype(str).tolist())
lista_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
lista_bloques = sorted(df_horario_init['id_bloque'].dropna().unique().astype(str).tolist())

def time_to_str(t):
    if pd.isna(t): return ""
    return str(t)[:5] if len(str(t)) >= 5 else str(t)

horas_inicio_unicas = df_horario_init['hora_inicio'].dropna().apply(time_to_str).unique().tolist()
horas_fin_unicas = df_horario_init['hora_fin'].dropna().apply(time_to_str).unique().tolist()
lista_horas_inicio = sorted([h for h in horas_inicio_unicas if h])
lista_horas_fin = sorted([h for h in horas_fin_unicas if h])

if not lista_asignaturas: lista_asignaturas = ["Sin Asignatura"]
if not lista_aulas: lista_aulas = ["Sin Aula"]
if not lista_bloques: lista_bloques = ["B1", "B2"]
if not lista_horas_inicio: lista_horas_inicio = ["07:00", "09:00"]
if not lista_horas_fin: lista_horas_fin = ["09:00", "11:00"]

# =======================
# FUNCIONES DE VALIDACIÓN
# =======================
def check_conflictos(nuevo_dia, nuevo_bloque, nuevo_aula, docente_actual, ignorar_indice=None):
    df_temp = st.session_state.horarios_df.copy()
    if ignorar_indice is not None and ignorar_indice in df_temp.index:
        df_temp = df_temp.drop(index=ignorar_indice)
        
    # Choque Docente
    choque_docente = df_temp[(df_temp["docente"] == docente_actual) & 
                             (df_temp["dia"] == nuevo_dia) & 
                             (df_temp["id_bloque"] == nuevo_bloque)]
    if not choque_docente.empty:
        return True, f"El docente ya imparte '{choque_docente.iloc[0]['asignatura']}' el {nuevo_dia} ({nuevo_bloque})."
        
    # Choque Aula
    if pd.notna(nuevo_aula) and str(nuevo_aula).strip() != "":
        choque_aula = df_temp[(df_temp["aula"].astype(str) == str(nuevo_aula)) & 
                              (df_temp["dia"] == nuevo_dia) & 
                              (df_temp["id_bloque"] == nuevo_bloque)]
        if not choque_aula.empty:
            return True, f"El aula {nuevo_aula} está ocupada por '{choque_aula.iloc[0]['docente']}' el {nuevo_dia} ({nuevo_bloque})."

    return False, "Sin conflictos"

# =======================
# BARRA LATERAL (SIDEBAR)
# =======================
st.sidebar.title("👨‍🏫 Gestión de Docentes")
docentes_lista = sorted(df_docentes["docente"].dropna().unique().tolist())
selected_docente = st.sidebar.selectbox("Seleccione un docente:", docentes_lista)

st.sidebar.markdown("---")
st.sidebar.info("La disponibilidad se calcula al vuelo basándose en el estado de las clases asignadas en el sistema.")

# =======================
# PANEL PRINCIPAL
# =======================
st.title("Dashboard de Gestión Sincronizada")

docente_info = df_docentes[df_docentes["docente"] == selected_docente].iloc[0]
docente_horario = st.session_state.horarios_df[st.session_state.horarios_df["docente"] == selected_docente]

st.subheader(f"Perfil: {selected_docente}")
col1, col2, col3 = st.columns(3)
col1.metric("Especialidad", str(docente_info.get("especialidad", "N/A")))
col2.metric("Max Horas/Semana", str(docente_info.get("max_horas_semana", "N/A")))
col3.metric("Clases Asignadas", str(len(docente_horario)))

st.markdown("---")

# =======================
# EDITOR DE CLASES
# =======================
st.subheader("✏️ Clases Asignadas (Edición en Vivo)")

if docente_horario.empty:
    st.info("Este docente no tiene clases asignadas actualmente.")
else:
    columnas_base = ["asignatura", "dia", "id_bloque", "hora_inicio", "hora_fin", "aula", "num_estudiantes"]
    columnas_mostrar = [c for c in columnas_base if c in docente_horario.columns]
    
    edited_df = st.data_editor(
        docente_horario[columnas_mostrar],
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_{selected_docente}",
        column_config={
            "asignatura": st.column_config.SelectboxColumn("Asignatura", options=lista_asignaturas, required=True),
            "dia": st.column_config.SelectboxColumn("Día", options=lista_dias, required=True),
            "id_bloque": st.column_config.SelectboxColumn("Bloque", options=lista_bloques, required=True),
            "aula": st.column_config.SelectboxColumn("Aula", options=lista_aulas, required=True),
            "hora_inicio": st.column_config.SelectboxColumn("Hora Inicio", options=lista_horas_inicio, required=True),
            "hora_fin": st.column_config.SelectboxColumn("Hora Fin", options=lista_horas_fin, required=True),
            "num_estudiantes": st.column_config.NumberColumn("Estudiantes", min_value=1, max_value=200, step=1, required=True)
        }
    )

    errores_tabla = []
    original_indices = docente_horario.index.tolist()
    edited_indices = edited_df.index.tolist()
    
    for idx, row in edited_df.iterrows():
        hay_conflicto, msg = check_conflictos(row.get("dia"), row.get("id_bloque"), row.get("aula"), selected_docente, ignorar_indice=idx if idx in original_indices else None)
        if hay_conflicto:
            errores_tabla.append(f"**{row.get('asignatura')}**: {msg}")
            
    if errores_tabla:
        with st.container(border=True):
            st.error("⚠️ **Conflictos detectados en la tabla:** No se puede guardar hasta resolverlos.")
            for e in errores_tabla:
                st.write(f"- {e}")
        guardar_disabled = True
    else:
        guardar_disabled = False

    if st.button("💾 Guardar Cambios en la Tabla", disabled=guardar_disabled, type="primary"):
        # Borrar eliminados
        filas_borradas = set(original_indices) - set(edited_indices)
        if filas_borradas:
            st.session_state.horarios_df = st.session_state.horarios_df.drop(index=list(filas_borradas))
        
        # Modificar/Agregar
        for idx, row in edited_df.iterrows():
            if idx in st.session_state.horarios_df.index:
                for col in columnas_mostrar:
                    st.session_state.horarios_df.at[idx, col] = row[col]
            else:
                nueva_fila = row.to_dict()
                nueva_fila["docente"] = selected_docente
                nuevo_df = pd.DataFrame([nueva_fila])
                st.session_state.horarios_df = pd.concat([st.session_state.horarios_df, nuevo_df], ignore_index=True)
        
        st.success("¡Cambios guardados! (El estado de disponibilidad se ha actualizado)")
        st.rerun()

st.markdown("---")

# =======================
# AGREGAR NUEVA CLASE (VALIDACIÓN BLOQUEANTE EN EVENTO SUBMIT)
# =======================
with st.expander("➕ Agregar Nueva Clase", expanded=True):
    with st.form(key="form_agregar_clase", border=False):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nueva_asignatura = st.selectbox("Asignatura", options=lista_asignaturas)
            nuevo_dia = st.selectbox("Día", options=lista_dias)
            nuevo_bloque = st.selectbox("Bloque", options=lista_bloques)
        with col_f2:
            nuevo_aula = st.selectbox("Aula", options=lista_aulas)
            nueva_h_inicio = st.selectbox("Hora Inicio", options=lista_horas_inicio)
            nueva_h_fin = st.selectbox("Hora Fin", options=lista_horas_fin)
            nuevo_num_estudiantes = st.number_input("Estudiantes", min_value=1, value=30, step=1)
            
        submit_btn = st.form_submit_button("Confirmar y Optimizar", type="primary")
        
        if submit_btn:
            hay_conflicto_nuevo, msg_conflicto_nuevo = check_conflictos(nuevo_dia, nuevo_bloque, nuevo_aula, selected_docente)
            
            if hay_conflicto_nuevo:
                st.toast(f"Error de Asignación", icon="🚨")
                st.error(f"❌ **Conflicto detectado:** {msg_conflicto_nuevo}")
            else:
                nueva_fila_dict = {
                    "asignatura": nueva_asignatura,
                    "docente": selected_docente,
                    "dia": nuevo_dia,
                    "id_bloque": nuevo_bloque,
                    "hora_inicio": nueva_h_inicio,
                    "hora_fin": nueva_h_fin,
                    "aula": nuevo_aula,
                    "num_estudiantes": nuevo_num_estudiantes,
                }
                nuevo_df = pd.DataFrame([nueva_fila_dict])
                st.session_state.horarios_df = pd.concat([st.session_state.horarios_df, nuevo_df], ignore_index=True)
                
                st.success(f"✅ ¡Clase agregada! Actualizando panel de disponibilidad...")
                st.rerun()

st.markdown("---")

# =======================
# VISUALIZACIÓN DE DISPONIBILIDAD (Sincronizada con st.session_state)
# =======================
st.subheader("🗓️ Estado de Disponibilidad del Docente")
st.caption("Calculado dinámicamente según las clases asignadas en el horario global.")

# Crear grilla base asumiendo 'Libre'
disp_grid = pd.DataFrame("Libre", index=lista_bloques, columns=lista_dias)

# Llenar la grilla con 'Ocupado' según el st.session_state.horarios_df
docente_horario_actualizado = st.session_state.horarios_df[st.session_state.horarios_df["docente"] == selected_docente]

for _, row in docente_horario_actualizado.iterrows():
    dia = row.get("dia")
    bloque = row.get("id_bloque")
    if pd.notna(dia) and pd.notna(bloque) and dia in lista_dias and bloque in lista_bloques:
        disp_grid.at[bloque, dia] = "Ocupado"

def color_disponibilidad(val):
    color = 'lightgreen' if val == 'Libre' else 'lightcoral' if val == 'Ocupado' else ''
    return f'background-color: {color}'

st.dataframe(disp_grid.style.map(color_disponibilidad), use_container_width=True)
