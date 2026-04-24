import flet as ft

class RegistroView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    def build(self):
        return ft.View(
            route="/register",
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Text("Registrar Usuario", color="white", weight=ft.FontWeight.BOLD), bgcolor=self.COLOR_MARINO, padding=10, border_radius=5),
                        ft.Button("Retroceder >", on_click=lambda _: self.navegar("/"), style=ft.ButtonStyle(bgcolor=self.COLOR_MARINO, color="white"))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=20,
                    border=ft.Border.only(bottom=ft.BorderSide(2, self.COLOR_MARINO))
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Nombre", weight=ft.FontWeight.BOLD, size=16, color=self.COLOR_MARINO),
                        ft.TextField(hint_text="Ingrese su nombre", border_color=self.COLOR_MARINO, width=400),
                        ft.Text("Contraseña", weight=ft.FontWeight.BOLD, size=16, color=self.COLOR_MARINO),
                        ft.TextField(hint_text="Ingrese su contraseña", border_color=self.COLOR_MARINO, width=400, password=True, can_reveal_password=True),
                        ft.Text("Mínimo al menos 8 caracteres, una mayúscula y un carácter especial (#,@, %...).", size=11, color="black"),
                        ft.Text("Rol", weight=ft.FontWeight.BOLD, size=16, color=self.COLOR_MARINO),
                        ft.Dropdown(
                            hint_text="Seleccionar rol...",
                            border_color=self.COLOR_MARINO,
                            width=400,
                            options=[
                                ft.dropdown.Option("Administrador"),
                                ft.dropdown.Option("Cajero"),
                                ft.dropdown.Option("Panadero"),
                            ]
                        ),
                        ft.Container(height=20),
                        ft.Button("Registrar Usuario", width=200, height=45, style=ft.ButtonStyle(bgcolor=self.COLOR_MARINO, color="white"))
                    ], 
                    alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    

                )
            ],
            bgcolor="white"
        )