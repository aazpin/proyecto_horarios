import flet as ft
from state import AppState

class DashboardView:
    def __init__(self, app_state: AppState):
        self.app_state = app_state

    def _create_stat_card(self, title, value, icon, color):
        return ft.Card(
            elevation=5,
            content=ft.Container(
                padding=20,
                width=200,
                height=120,
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Icon(icon, color=color, size=30),
                                ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        ft.Text(str(value), size=36, weight=ft.FontWeight.BOLD, color=color),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )

    def build(self):
        if not self.app_state.is_loaded():
            return ft.Container(
                content=ft.Text("Por favor, cargue un archivo Excel en la pantalla de Inicio primero.", size=20, color=ft.Colors.RED),
                alignment=ft.Alignment.CENTER
            )

        # Get data
        df_docentes = self.app_state.get_df("Docentes")
        df_aulas = self.app_state.get_df("Aulas")
        df_asignaturas = self.app_state.get_df("Asignaturas")
        df_sesiones = self.app_state.get_df("Sesiones_Requeridas")

        # Stats
        total_docentes = len(df_docentes) if df_docentes is not None else 0
        total_aulas = len(df_aulas) if df_aulas is not None else 0
        total_asignaturas = len(df_asignaturas) if df_asignaturas is not None else 0
        total_sesiones = len(df_sesiones) if df_sesiones is not None else 0

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Dashboard Resumen", size=32, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=20, color=ft.Colors.GREY_300),
                    ft.Row(
                        [
                            self._create_stat_card("Docentes", total_docentes, ft.Icons.PEOPLE, ft.Colors.BLUE),
                            self._create_stat_card("Aulas", total_aulas, ft.Icons.MEETING_ROOM, ft.Colors.GREEN),
                            self._create_stat_card("Asignaturas", total_asignaturas, ft.Icons.MENU_BOOK, ft.Colors.ORANGE),
                            self._create_stat_card("Sesiones", total_sesiones, ft.Icons.SCHEDULE, ft.Colors.PURPLE),
                        ],
                        wrap=True,
                        spacing=20
                    ),
                    ft.Container(height=40),
                    ft.Text("Asegúrese de revisar los datos en la pestaña 'Datos' antes de iniciar la optimización.", italic=True, color=ft.Colors.GREY_600)
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.START,
            ),
            expand=True
        )
