import flet as ft
from state import AppState
import pandas as pd

class DataView:
    def __init__(self, app_state: AppState):
        self.app_state = app_state

    def _create_datatable_from_df(self, df: pd.DataFrame):
        if df is None or df.empty:
            return ft.Text("No hay datos disponibles.", italic=True)

        columns = [ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD)) for col in df.columns]
        
        # Limit rows for performance if needed, but Flet handles ~100 rows fine.
        rows = []
        for index, row in df.head(100).iterrows():
            cells = [ft.DataCell(ft.Text(str(val))) for val in row]
            rows.append(ft.DataRow(cells=cells))

        return ft.Column([
            ft.Row([ft.Text(f"Mostrando {len(rows)} filas de {len(df)} totales", italic=True, color=ft.Colors.GREY_500)]),
            ft.ListView([
                ft.DataTable(
                    columns=columns,
                    rows=rows,
                    border=ft.Border(top=ft.BorderSide(1, ft.Colors.GREY_300), right=ft.BorderSide(1, ft.Colors.GREY_300), bottom=ft.BorderSide(1, ft.Colors.GREY_300), left=ft.BorderSide(1, ft.Colors.GREY_300)),
                    border_radius=10,
                    vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                    horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                    heading_row_color=ft.Colors.BLUE_50,
                )
            ], expand=True)
        ], expand=True)

    def build(self):
        if not self.app_state.is_loaded():
            return ft.Container(
                content=ft.Text("Por favor, cargue un archivo Excel en la pantalla de Inicio primero.", size=20, color=ft.Colors.RED),
                alignment=ft.Alignment.CENTER
            )

        tabs = []
        # Sheets we care about viewing
        sheets_to_view = ["Asignaturas", "Docentes", "Aulas", "Bloques", "Disponibilidad_Docente", "Sesiones_Requeridas"]
        
        for sheet_name in sheets_to_view:
            df = self.app_state.get_df(sheet_name)
            if df is not None:
                tab_content = ft.Container(
                    content=self._create_datatable_from_df(df),
                    padding=10,
                    expand=True
                )
                tabs.append(ft.Tab(text=sheet_name, content=tab_content))

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Gestión de Datos", size=32, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, color=ft.Colors.GREY_300),
                    ft.Tabs(
                        selected_index=0,
                        animation_duration=300,
                        tabs=tabs,
                        expand=True,
                    )
                ],
                expand=True
            ),
            expand=True
        )
