import flet as ft
from state import AppState
import pandas as pd

class ScheduleView:
    def __init__(self, app_state: AppState):
        self.app_state = app_state

    def _create_datatable_from_df(self, df: pd.DataFrame):
        if df is None or df.empty:
            return ft.Text("No hay datos disponibles en el horario optimizado.", italic=True)

        columns = [ft.DataColumn(ft.Text(str(col), weight=ft.FontWeight.BOLD)) for col in df.columns]
        
        rows = []
        for index, row in df.iterrows():
            cells = []
            for col_name, val in zip(df.columns, row):
                color = ft.Colors.BLACK
                if col_name == "observacion" and isinstance(val, str) and "Conflicto" in val:
                    color = ft.Colors.RED
                elif col_name == "observacion" and isinstance(val, str) and "Correcta" in val:
                    color = ft.Colors.GREEN
                    
                cells.append(ft.DataCell(ft.Text(str(val), color=color)))
            rows.append(ft.DataRow(cells=cells))

        return ft.Column([
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

        df_optimizado = self.app_state.get_df("Horario_Optimizado")
        
        if df_optimizado is None:
            df_optimizado = self.app_state.get_df("Horario_Inicial")
            titulo = "Horario Inicial (Aún no optimizado)"
            color_titulo = ft.Colors.ORANGE_700
        else:
            titulo = "Horario Optimizado"
            color_titulo = ft.Colors.GREEN_700

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(titulo, size=32, weight=ft.FontWeight.BOLD, color=color_titulo),
                    ft.Divider(height=20, color=ft.Colors.GREY_300),
                    ft.Container(
                        content=self._create_datatable_from_df(df_optimizado),
                        expand=True
                    )
                ],
                expand=True
            ),
            expand=True
        )
