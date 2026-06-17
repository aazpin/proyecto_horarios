import flet as ft
import asyncio
import pandas as pd
import random
from state import AppState
from utils.optimizer_logic import calcular_penalizaciones
from utils.excel_manager import guardar_horario_optimizado

class OptimizerView:
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        
        self.btn_start = ft.Button("Iniciar Optimización", icon=ft.Icons.PLAY_ARROW, on_click=self.start_optimization)
        self.progress_bar = ft.ProgressBar(width=400, color="amber", bgcolor="#eeeeee", value=0)
        self.status_text = ft.Text("Listo para iniciar.", size=16)
        self.penalization_text = ft.Text("", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
        
        self.progress_container = ft.Column(
            [self.status_text, self.progress_bar, self.penalization_text],
            visible=False,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    async def start_optimization(self, e):
        if not self.app_state.is_loaded():
            self.status_text.value = "Error: Carga primero el Excel."
            self.app_state.page.update()
            return
            
        self.btn_start.disabled = True
        self.progress_container.visible = True
        self.status_text.value = "Preparando datos..."
        self.progress_bar.value = None  # Indeterminate
        self.app_state.page.update()
        
        success, result, final_score = await asyncio.to_thread(self.run_metaheuristic)
        
        if success:
            self.progress_bar.value = 1.0
            self.status_text.value = f"¡Optimización Completada! Archivo guardado en:\n{result}"
            self.status_text.color = ft.Colors.GREEN
            self.penalization_text.value = f"Penalización Final: {final_score}"
            self.penalization_text.color = ft.Colors.GREEN if final_score == 0 else ft.Colors.ORANGE
            
            # Recargar el Excel para que la vista de "Horarios" se actualice
            self.app_state.load_excel(result)
        else:
            self.status_text.value = f"Error: {result}"
            self.status_text.color = ft.Colors.RED
            self.progress_bar.value = 0
            
        self.btn_start.disabled = False
        self.app_state.page.update()

    def run_metaheuristic(self):
        try:
            df_solucion = self.app_state.get_df("Horario_Inicial").copy()
            if df_solucion is None:
                return False, "Hoja 'Horario_Inicial' no encontrada.", 0
                
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

            # Guardar el archivo
            ruta_original = self.app_state.excel_path
            success, result_path = guardar_horario_optimizado(df_solucion, ruta_original)
            
            return success, result_path, penalizacion_actual
        except Exception as e:
            return False, str(e), -1

    def build(self):
        if not self.app_state.is_loaded():
            return ft.Container(
                content=ft.Text("Por favor, cargue un archivo Excel en la pantalla de Inicio primero.", size=20, color=ft.Colors.RED),
                alignment=ft.Alignment.CENTER
            )
            
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Motor de Optimización", size=32, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, color=ft.Colors.GREY_300),
                    ft.Text("Este proceso utilizará un algoritmo metaheurístico para resolver conflictos de horarios, asignación de aulas y disponibilidad de docentes.", size=16),
                    ft.Container(height=40),
                    self.btn_start,
                    ft.Container(height=30),
                    self.progress_container,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True
        )
