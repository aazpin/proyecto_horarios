import flet as ft
from state import AppState
import pandas as pd

class TeachersView:
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        
        # References for dynamic UI updates
        self.dd_teachers = ft.Dropdown(
            label="Selecciona un Docente",
            width=300,
            on_select=self.on_teacher_select
        )
        self.teacher_info_col = ft.Column(expand=True, spacing=20)
        
    def _get_teacher_details(self, docente_name: str) -> dict:
        df_docentes = self.app_state.get_df("Docentes")
        if df_docentes is None or df_docentes.empty:
            return {}
            
        docente_row = df_docentes[df_docentes["docente"] == docente_name]
        if docente_row.empty:
            return {}
            
        return docente_row.iloc[0].to_dict()

    def _get_teacher_schedule(self, docente_name: str) -> pd.DataFrame:
        df_opt = self.app_state.get_df("Horario_Optimizado")
        df_ini = self.app_state.get_df("Horario_Inicial")
        
        df_horario = df_opt if df_opt is not None else df_ini
        
        if df_horario is None or df_horario.empty:
            return pd.DataFrame()
            
        return df_horario[df_horario["docente"] == docente_name]

    def _build_profile_card(self, details: dict):
        if not details:
            return ft.Text("Detalles no encontrados.")
            
        return ft.Card(
            elevation=4,
            content=ft.Container(
                padding=20,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.PERSON_PIN, size=50, color=ft.Colors.BLUE_700),
                        ft.Column([
                            ft.Text(f"{details.get('docente', 'N/A')}", size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Especialidad: {details.get('especialidad', 'N/A')} | Max Horas: {details.get('max_horas_semana', 'N/A')}", color=ft.Colors.GREY_700),
                            ft.Text(f"Preferencia de Jornada: {details.get('preferencia_jornada', 'N/A')} | Observación: {details.get('observacion', 'Ninguna')}", italic=True, color=ft.Colors.GREY_500),
                        ])
                    ]
                )
            )
        )

    def _build_schedule_table(self, df_schedule: pd.DataFrame):
        if df_schedule.empty:
            return ft.Container(
                padding=20,
                content=ft.Text("Este docente no tiene clases asignadas en el horario actual.", color=ft.Colors.GREY_500, italic=True)
            )
            
        columns_to_show = ["asignatura", "dia", "hora_inicio", "hora_fin", "aula", "num_estudiantes"]
        
        columns = [ft.DataColumn(ft.Text(str(col).capitalize().replace('_', ' '), weight=ft.FontWeight.BOLD)) for col in columns_to_show]
        rows = []
        
        for _, row in df_schedule.iterrows():
            cells = []
            for col_name in columns_to_show:
                val = row.get(col_name, "")
                cells.append(ft.DataCell(ft.Text(str(val))))
            rows.append(ft.DataRow(cells=cells))
            
        return ft.Container(
            padding=10,
            content=ft.Column([
                ft.Text("Clases Asignadas", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                ft.ListView([
                    ft.DataTable(
                        columns=columns,
                        rows=rows,
                        border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_300), right=ft.BorderSide(1, ft.Colors.GREY_300), bottom=ft.BorderSide(1, ft.Colors.GREY_300), left=ft.BorderSide(1, ft.Colors.GREY_300)),
                        border_radius=8,
                        heading_row_color=ft.Colors.BLUE_50,
                    )
                ], height=350)
            ])
        )

    def on_teacher_select(self, e):
        selected_docente = self.dd_teachers.value
        
        self.teacher_info_col.controls.clear()
        
        if not selected_docente:
            self.teacher_info_col.controls.append(ft.Text("Seleccione un docente de la lista para ver su información."))
        else:
            details = self._get_teacher_details(selected_docente)
            schedule_df = self._get_teacher_schedule(selected_docente)
            
            profile_card = self._build_profile_card(details)
            schedule_table = self._build_schedule_table(schedule_df)
            
            self.teacher_info_col.controls.extend([
                profile_card,
                schedule_table
            ])
            
        self.app_state.page.update()

    def build(self):
        if not self.app_state.is_loaded():
            return ft.Container(
                content=ft.Text("Por favor, cargue un archivo Excel en la pantalla de Inicio primero.", size=20, color=ft.Colors.RED),
                alignment=ft.Alignment.CENTER
            )
            
        df_docentes = self.app_state.get_df("Docentes")
        
        if df_docentes is not None and not df_docentes.empty:
            docentes_list = df_docentes["docente"].dropna().unique().tolist()
            self.dd_teachers.options = [ft.dropdown.Option(docente) for docente in sorted(docentes_list)]
        else:
            self.dd_teachers.options = []

        # Estado inicial del panel derecho
        self.teacher_info_col.controls = [
            ft.Container(
                padding=50,
                alignment=ft.Alignment.CENTER,
                content=ft.Text("Seleccione un docente de la lista lateral para visualizar sus datos.", color=ft.Colors.GREY_500, italic=True)
            )
        ]

        left_panel = ft.Container(
            width=350,
            padding=20,
            border=ft.Border(right=ft.BorderSide(1, ft.Colors.GREY_300)),
            content=ft.Column(
                [
                    ft.Text("Buscador de Docentes", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(color=ft.Colors.TRANSPARENT),
                    self.dd_teachers,
                    ft.Divider(color=ft.Colors.TRANSPARENT),
                    ft.Text("Utiliza este panel para navegar rápidamente entre los perfiles de los docentes.", size=12, color=ft.Colors.GREY_500)
                ]
            )
        )

        right_panel = ft.Container(
            expand=True,
            padding=20,
            content=self.teacher_info_col
        )

        return ft.Container(
            content=ft.Row(
                [
                    left_panel,
                    right_panel
                ],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),
            expand=True
        )
