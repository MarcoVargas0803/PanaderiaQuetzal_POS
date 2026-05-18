import flet as ft
from components.Toasts import NotificationHelper

class InicioView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    #Definición de _handlers para verificaciones internas.
    def _notificar(self,page, mensaje: str, es_error: bool):
        """Atajo interno para disparar Toasts de forma asíncrona."""
        page.run_task(
            NotificationHelper.mostrar_toast, 
            page, 
            mensaje, 
            es_error # es_error
        )

    def _handle_iniciar_sesion(self,e):
        
        self.navegar("/login")
        # 1. Ejecutamos la notificación (asíncrona)
        # Pasamos la función, luego los argumentos posicionales
        e.page.run_task(
            NotificationHelper.mostrar_toast, 
            e.page, 
            "¡Iniciando sesion!", 
            False # es_error
        )
        


    def build(self):
        return ft.View(
            route="/",
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=ft.Text("Panadería Quetzal POS V.1.0.", color="white", weight=ft.FontWeight.BOLD), bgcolor=self.COLOR_MARINO, padding=10, border_radius=5),
                        ft.Row([
                            ft.Button("Iniciar Sesión", on_click = lambda _:self.navegar("/login"), style=ft.ButtonStyle(color=self.COLOR_MARINO)),
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