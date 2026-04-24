import flet as ft

class InicioView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    def build(self):
        return ft.View(
            route="/",
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Text("Panadería Quetzal POS V.1.0.", color="white", weight=ft.FontWeight.BOLD), bgcolor=self.COLOR_MARINO, padding=10, border_radius=5),
                        ft.Row([
                            ft.Button("Iniciar Sesión", on_click=lambda _: self.navegar("/login"), style=ft.ButtonStyle(color=self.COLOR_MARINO)),
                            # Botón de Registrarse eliminado
                        ])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=20,
                    border=ft.Border.only(bottom=ft.BorderSide(2, self.COLOR_MARINO))
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Text("PANADERÍA QUETZAL", size=50, weight=ft.FontWeight.BOLD, color="black"),
                        ft.Image(src="../assets/Panaderia_Quetzal_Logo.jpg", width=300, height=300, fit="contain")
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=50),
                    expand=True,
                    alignment=ft.Alignment(0, 0)
                ),
                ft.Container(
                    content=ft.Text("Panadería Quetzal POS V. 1.0", weight=ft.FontWeight.BOLD, color="black"),
                    alignment=ft.Alignment(0, 0),
                    padding=20
                )
            ],
            bgcolor="white"
        )