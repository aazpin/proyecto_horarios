import flet as ft

def main(page: ft.Page):
    # Configuración estricta de la ventana
    page.title = "App de Optimización de Horarios"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    file_picker = ft.FilePicker()

    # Componentes UI
    archivo_seleccionado = ft.Text("No se ha seleccionado archivo", color="red")
    ruta_archivo = ft.Text(visible=False) # Contenedor oculto para la ruta
    status_text = ft.Text("", size=14, weight="bold")
    btn_optimizar = ft.Button("Ejecutar Optimización", disabled=True, icon=ft.Icons.PLAY_ARROW)

    async def seleccionar_archivo(e):
        e.control.disabled = True
        page.update()
        try:
            files = await file_picker.pick_files()
            if files:
                archivo_seleccionado.value = f"Archivo cargado: {files[0].name}"
                archivo_seleccionado.color = "green"
                # Guardamos la ruta real para usarla en el backend
                ruta_archivo.value = files[0].path
                btn_optimizar.disabled = False
                status_text.value = "" # Limpiar estado previo
        finally:
            e.control.disabled = False
            page.update()

    async def ejecutar_optimizacion(e):
        if not ruta_archivo.value:
            return
        
        btn_optimizar.disabled = True
        status_text.value = "Optimizando horarios... Por favor, espera."
        status_text.color = "blue"
        page.update()

        def run_opt():
            import pandas as pd
            import random
            import os
            from main import calcular_penalizaciones

            archivo_path = ruta_archivo.value
            if not os.path.exists(archivo_path):
                return False, "Error: El archivo seleccionado no existe."

            try:
                # Leer el Excel
                df_solucion = pd.read_excel(archivo_path, sheet_name="Horario_Inicial")
                
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

                # Guardamos en la misma ruta que el original o en el directorio actual
                directorio_original = os.path.dirname(archivo_path)
                ruta_salida = os.path.join(directorio_original, "Horario_Optimizado.xlsx")
                
                with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
                    df_solucion.to_excel(writer, sheet_name="Horario_Optimizado", index=False)

                return True, ruta_salida
            except Exception as ex:
                return False, str(ex)

        import asyncio
        success, resultado = await asyncio.to_thread(run_opt)

        if success:
            status_text.value = f"¡Optimización completada con éxito!\nGuardado en:\n{resultado}"
            status_text.color = "green"
        else:
            status_text.value = f"Error durante la optimización:\n{resultado}"
            status_text.color = "red"

        btn_optimizar.disabled = False
        page.update()

    btn_optimizar.on_click = ejecutar_optimizacion

    def ir_a_dashboard(e):
        page.clean()
        page.add(
            ft.Text("Gestor de Horarios", size=30, weight="bold"),
            ft.Button("Seleccionar Excel", icon=ft.Icons.UPLOAD_FILE, 
                      on_click=seleccionar_archivo),
            archivo_seleccionado,
            btn_optimizar,
            status_text
        )
        page.update()

    # Pantalla principal
    page.add(
        ft.Text("Sistema de Optimización", size=40, weight="bold"),
        ft.Button("Iniciar App", on_click=ir_a_dashboard)
    )

if __name__ == "__main__":
    ft.run(main)