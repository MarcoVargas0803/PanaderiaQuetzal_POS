import flet as ft
from Backend.dao_panaderia import registrar_cliente

class RegistrarClienteView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    def guardar(self, e):
        nombre = self.txt_nombre.value.strip()
        telefono = self.txt_telefono.value.strip()

        # Validar nombre
        if not nombre:
            self.txt_nombre.error_text = "El nombre es obligatorio"
            self.txt_nombre.update()
            return
        else:
            self.txt_nombre.error_text = None
            self.txt_nombre.update()

        # Validar teléfono: exactamente 10 dígitos numéricos
        if telefono and (not telefono.isdigit() or len(telefono) != 10):
            self.txt_telefono.error_text = "El teléfono debe tener exactamente 10 dígitos numéricos"
            self.txt_telefono.update()
            return
        else:
            self.txt_telefono.error_text = None
            self.txt_telefono.update()

        try:
            registrar_cliente(nombre, telefono if telefono else None)
            self.page.snack_bar = ft.SnackBar(ft.Text("¡Cliente registrado con éxito!"), bgcolor="#27AE60")
            self.page.snack_bar.open = True
            self.navegar("/ventana_principal")
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al registrar: {ex}"), bgcolor="red")
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
