import flet as ft
from Backend.dao_panaderia import registrar_cliente

class RegistrarClienteView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    def guardar(self, e):
        if not self.txt_nombre.value:
            self.page.snack_bar = ft.SnackBar(ft.Text("El nombre es obligatorio"), bgcolor="orange")
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        try:
            registrar_cliente(self.txt_nombre.value.strip(), self.txt_telefono.value.strip())
            self.page.snack_bar = ft.SnackBar(ft.Text("¡Cliente registrado con éxito!"), bgcolor="#27AE60")
            self.page.snack_bar.open = True
            self.navegar("/ventana_principal")
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def build(self):
        self.txt_nombre = ft.TextField(label="Nombre Completo", autofocus=True, prefix_icon=ft.Icons.PERSON)
        self.txt_telefono = ft.TextField(label="Teléfono (10 dígitos)", prefix_icon=ft.Icons.PHONE)

        return ft.View(
            route="/registrar_cliente",
            bgcolor="#F0F2F5",
            padding=0,
            controls=[
                ft.AppBar(title=ft.Text("Nuevo Cliente"), bgcolor=self.COLOR_MARINO, color="white"),
                ft.Row([
                    ft.Container(
                        content=ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.PERSON_ADD, size=50, color=self.COLOR_MARINO),
                                    ft.Text("REGISTRO DE CLIENTE", size=22, weight="bold", color=self.COLOR_MARINO),
                                    ft.Text("Ingrese los datos para habilitar apartados", color="grey"),
                                    ft.Divider(),
                                    self.txt_nombre,
                                    self.txt_telefono,
                                    ft.Divider(),
                                    ft.Row([
                                        ft.ElevatedButton("GUARDAR", on_click=self.guardar, bgcolor="#27AE60", color="white", height=45, expand=1),
                                        ft.TextButton("CANCELAR", on_click=lambda _: self.navegar("/ventana_principal"), height=45)
                                    ], spacing=10)
                                ], spacing=20, horizontal_alignment="center"),
                                padding=30
                            ),
                            elevation=10
                        ),
                        width=450,
                        padding=ft.padding.only(top=50)
                    )
                ], alignment="center", expand=True)
            ]
        )
