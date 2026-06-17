import flet as ft
from state import AppState

class HomeView:
    def __init__(self, app_state: AppState):
        self.app_state = app_state
        self.file_picker = ft.FilePicker()
        
        self.status_text = ft.Text("", size=16, italic=True)
        self.btn_load = ft.Button(
            "Seleccionar Archivo Excel",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self.on_file_pick_clicked
        )

    async def on_file_pick_clicked(self, e):
        if self.file_picker not in self.app_state.page.overlay:
            self.app_state.page.overlay.append(self.file_picker)
        self.app_state.page.update()
        
        # We must await the file picker dialog
        files = await self.file_picker.pick_files(
            allowed_extensions=["xlsx", "xls"],
            allow_multiple=False
        )
        
        if files and len(files) > 0:
            file_path = files[0].path
            self.status_text.value = f"Cargando archivo: {files[0].name}..."
            self.status_text.color = ft.Colors.BLUE
            self.app_state.page.update()

            success, msg = self.app_state.load_excel(file_path)
            
            if success:
                self.status_text.value = f"¡Éxito! {msg}"
                self.status_text.color = ft.Colors.GREEN
            else:
                self.status_text.value = f"Error: {msg}"
                self.status_text.color = ft.Colors.RED
            self.app_state.page.update()

    def build(self):
        # We need to add the file_picker to the overlay for it to work
        if self.file_picker not in self.app_state.page.overlay:
            self.app_state.page.overlay.append(self.file_picker)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.SCHOOL, size=100, color=ft.Colors.BLUE_700),
                    ft.Text("Bienvenido al Sistema de Gestión de Horarios", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("Para comenzar, por favor seleccione el archivo Excel con los datos maestros y el horario inicial.", size=16, color=ft.Colors.GREY_700),
                    ft.Container(height=40),
                    self.btn_load,
                    ft.Container(height=20),
                    self.status_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.Alignment.CENTER,
            expand=True
        )
