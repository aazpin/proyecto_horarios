import flet as ft
from state import AppState

# Import views
from views.home_view import HomeView
from views.dashboard_view import DashboardView
from views.data_view import DataView
from views.optimizer_view import OptimizerView
from views.schedule_view import ScheduleView
from views.teachers_view import TeachersView

def main(page: ft.Page):
    page.title = "Sistema de Gestión de Horarios Académicos"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.width = 1200
    page.window.height = 800
    page.bgcolor = ft.Colors.BLUE_GREY_50
    
    # Initialize State
    app_state = AppState()
    app_state.page = page

    # Initialize Views
    views = {
        0: HomeView(app_state),
        1: DashboardView(app_state),
        2: DataView(app_state),
        3: TeachersView(app_state),
        4: OptimizerView(app_state),
        5: ScheduleView(app_state)
    }

    content_area = ft.Container(
        content=views[0].build(),
        expand=True,
        padding=20,
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        margin=10
    )

    def on_nav_change(e):
        selected_index = e.control.selected_index
        # Verify data is loaded before allowing access to other views
        if selected_index != 0 and not app_state.is_loaded():
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, carga primero el archivo Excel en la vista de Inicio."), bgcolor=ft.Colors.ERROR)
            page.snack_bar.open = True
            e.control.selected_index = 0
            page.update()
            return
            
        content_area.content = views[selected_index].build()
        page.update()

    rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Inicio"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Resumen"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TABLE_CHART_OUTLINED, selected_icon=ft.Icons.TABLE_CHART, label="Datos"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PERSON_OUTLINED, selected_icon=ft.Icons.PERSON, label="Docentes"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PLAY_CIRCLE_OUTLINE, selected_icon=ft.Icons.PLAY_CIRCLE_FILL, label="Optimizar"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED, selected_icon=ft.Icons.CALENDAR_MONTH, label="Horarios"
            ),
        ],
        on_change=on_nav_change,
        bgcolor=ft.Colors.BLUE_GREY_50
    )

    page.add(
        ft.Row(
            [
                rail,
                ft.VerticalDivider(width=1, color=ft.Colors.TRANSPARENT),
                content_area,
            ],
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.run(main)
