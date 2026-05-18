import flet as ft
from Backend.dao_panaderia import obtener_corte_caja, cerrar_caja
from session_state import get_session
from components.Toasts import NotificationHelper

class CorteCajaView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)

    def ejecutar_cierre(self, e):
        session = get_session()
        try:
            val_str = str(self.txt_fisico.value or "0").replace(",", ".")
            monto = float(val_str)
            if monto < 0:
                raise ValueError("El monto contado no puede ser negativo")
            cerrar_caja(int(session.current_caja_id), monto)
            session.current_caja_id = None
            self.navegar("/")
        except Exception as ex:
            print(f"Error al cerrar caja: {ex}")
            self._notificar(f"Error BD: {ex}", es_error=True)

    def build(self):
        session = get_session()
        datos = obtener_corte_caja(session.current_caja_id)
        
        self.txt_fisico = ft.TextField(label="Efectivo en Caja ($)", autofocus=True)
        
        # Si no hay datos, mostrar error
        if not datos:
            return ft.View(route="/corte_caja", controls=[ft.Text("No se pudo obtener información de la caja")])

        return ft.View(
            route="/corte_caja",
            controls=[
                ft.AppBar(title=ft.Text("Cierre de Turno"), bgcolor="#2C3545", color="white"),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Resumen de Caja", size=24, weight="bold"),
                        ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.ListTile(title=ft.Text(f"Saldo Inicial: ${datos.get('saldo_inicial', 0):.2f}")),
                                    ft.ListTile(title=ft.Text(f"Total Ventas: ${datos.get('total_cobrado', 0):.2f}")),
                                    ft.ListTile(title=ft.Text(f"Esperado en Efectivo: ${datos.get('saldo_esperado_efectivo', 0):.2f}", weight="bold", color="green")),
                                ]), padding=20
                            )
                        ),
                        ft.Text("Contabilización Física", size=18, weight="bold"),
                        self.txt_fisico,
                        ft.Row([
                            ft.ElevatedButton("Finalizar Turno y Salir", on_click=self.ejecutar_cierre, bgcolor="red", color="white"),
                            ft.TextButton("Volver al POS", on_click=lambda _: self.navegar("/ventana_principal"))
                        ], alignment="center", spacing=20)
                    ], spacing=20, alignment="center"),
                    padding=50
                )
            ]
        )
