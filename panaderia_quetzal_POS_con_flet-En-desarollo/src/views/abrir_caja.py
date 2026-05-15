import flet as ft
from Backend.dao_panaderia import abrir_caja, obtener_caja_activa
from session_state import get_session

class AbrirCajaView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    def confirmar_apertura(self, e):
        session = get_session()
        try:
            val_str = str(self.txt_fondo.value or "0").replace(",", ".")
            fondo = float(val_str)
            abrir_caja(session.current_user_id, fondo)
            activa = obtener_caja_activa(session.current_user_id)
            if activa:
                session.current_caja_id = activa
            self.navegar("/ventana_principal")
        except Exception as ex:
            print(f"Error al abrir caja: {ex}")
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED)
            e.page.snack_bar.open = True
            e.page.update()

    def build(self):
        session = get_session()
        self.txt_fondo = ft.TextField(
            label="Fondo Inicial Efectivo ($)", 
            value="0.0", 
            width=300, 
            text_align="center",
            border_color=self.COLOR_MARINO
        )

        return ft.View(
            route="/abrir_caja",
            bgcolor="white",
            vertical_alignment="center",
            horizontal_alignment="center",
            controls=[
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.LOCK_PERSON, size=80, color=self.COLOR_MARINO),
                        ft.Text("Apertura de Turno Requerida", size=30, weight="bold", color=self.COLOR_MARINO),
                        ft.Text(f"Cajero/a: {session.current_user}", size=18, color="#9BA4B5"),
                        ft.Container(height=20),
                        self.txt_fondo,
                        ft.Container(height=20),
                        ft.ElevatedButton(
                            "INICIAR TURNO Y ABRIR CAJA",
                            on_click=self.confirmar_apertura,
                            width=350, height=50,
                            style=ft.ButtonStyle(
                                bgcolor=self.COLOR_MARINO,
                                color="white",
                                shape=ft.RoundedRectangleBorder(radius=5)
                            )
                        ),
                        ft.TextButton("Cerrar Sesión / Salir", on_click=lambda _: self.navegar("/"))
                    ], alignment="center", horizontal_alignment="center"),
                    padding=40,
                    bgcolor="#F8F9FA",
                    border_radius=20,
                    border=ft.Border.all(1, "#E0E5EC")
                )
            ]
        )
