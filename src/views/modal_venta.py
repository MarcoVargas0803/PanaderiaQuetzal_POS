import flet as ft
from Backend.dao_panaderia import registrar_venta_directa
from session_state import get_session
from components.Toasts import NotificationHelper
import time
import threading

class ModalVenta:
    def __init__(self, page, on_success_callback):
        self.page = page
        self.on_success_callback = on_success_callback
        self.COLOR_MARINO = "#2C3545"
        self.metodo_pago = "Efectivo"
        self.carrito_actual = {}
        self.total_actual = 0.0
        self.dialog = None
        self._build_dialog()

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)

    def cambiar_pago(self, e):
        self.metodo_pago = e.control.data
        self._actualizar_botones_pago()
        self.dialog.update()

    def _actualizar_botones_pago(self):
        for btn in self.botones_pago.controls:
            if btn.data == self.metodo_pago:
                if self.metodo_pago == "Efectivo":
                    btn.style = ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color="white")
                elif self.metodo_pago == "Tarjeta":
                    btn.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color="white")
                else:
                    btn.style = ft.ButtonStyle(bgcolor=ft.Colors.PURPLE, color="white")
            else:
                btn.style = ft.ButtonStyle(bgcolor=ft.Colors.GREY, color="white")
        
    def confirmar(self, e):
        session = get_session()
        
        if not self.carrito_actual:
            self._notificar("El carrito está vacío", es_error=True)
            return

        self.btn_confirmar.disabled = True
        self.btn_confirmar.text = "Procesando..."
        self.dialog.update()

        threading.Thread(target=self._procesar_venta_db, args=(session,), daemon=True).start()

    def _procesar_venta_db(self, session):
        try:
            detalles = [{"productos_id": v["producto_id"], "cantidad": v["cantidad"]} for v in self.carrito_actual.values()]

            registrar_venta_directa(
                int(session.current_user_id),
                int(session.current_caja_id),
                self.total_actual,
                detalles,
                self.metodo_pago
            )

            self.page.run_task(self._venta_exitosa_async)
        except Exception as ex:
            self.page.run_task(self._venta_error_async, str(ex))

    async def _venta_exitosa_async(self):
        self._notificar("VENTA REGISTRADA CON ÉXITO", es_error=False)
        self.cerrar(None)
        if self.on_success_callback:
            self.on_success_callback()

    async def _venta_error_async(self, error_msg):
        self.btn_confirmar.disabled = False
        self.btn_confirmar.text = "CONFIRMAR VENTA"
        self._notificar(f"Error al registrar venta: {error_msg}", es_error=True)
        self.dialog.update()

    def cerrar(self, e):
        self.dialog.open = False
        self.page.update()

    def _build_dialog(self):
        self.btn_efectivo = ft.ElevatedButton("EFECTIVO", icon=ft.Icons.MONEY, data="Efectivo", on_click=self.cambiar_pago, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color="white"))
        self.btn_tarjeta = ft.ElevatedButton("TARJETA", icon=ft.Icons.CREDIT_CARD, data="Tarjeta", on_click=self.cambiar_pago, style=ft.ButtonStyle(bgcolor=ft.Colors.GREY, color="white"))
        self.btn_transferencia = ft.ElevatedButton("TRANSFER", icon=ft.Icons.PHONE_ANDROID, data="Transferencia", on_click=self.cambiar_pago, style=ft.ButtonStyle(bgcolor=ft.Colors.GREY, color="white"))
        
        self.botones_pago = ft.Row([self.btn_efectivo, self.btn_tarjeta, self.btn_transferencia], spacing=10, alignment=ft.MainAxisAlignment.CENTER)

        selector_pago = ft.Container(
            content=ft.Column([
                ft.Text("MÉTODO DE PAGO:", weight="bold", size=14, color=self.COLOR_MARINO),
                self.botones_pago
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=10
        )

        self.btn_confirmar = ft.ElevatedButton("CONFIRMAR VENTA", on_click=self.confirmar, bgcolor="#F6921E", color="white", height=50, width=400)
        
        self.texto_total = ft.Text(f"Total de la orden: $0.00", size=20, weight="bold", color="#27AE60")

        contenido = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.SHOPPING_CART_CHECKOUT, size=50, color="#F6921E"),
                ft.Text("RESUMEN DE VENTA", size=24, weight="bold", color=self.COLOR_MARINO),
                self.texto_total,
                ft.Divider(),
                selector_pago,
                ft.Divider(),
                self.btn_confirmar,
                ft.TextButton("CANCELAR", on_click=self.cerrar)
            ], spacing=15, horizontal_alignment="center", tight=True),
            padding=30, width=480
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            content=contenido,
            content_padding=0,
            shape=ft.RoundedRectangleBorder(radius=15)
        )

    def show(self, carrito, total):
        self.carrito_actual = carrito
        self.total_actual = total
        
        if not self.carrito_actual:
            self._notificar("Agregue productos al carrito antes de cobrar.", es_error=True)
            return

        self.texto_total.value = f"Total de la orden: ${self.total_actual:.2f}"
        
        # Resetear estado
        self.metodo_pago = "Efectivo"
        self._actualizar_botones_pago()
        self.btn_confirmar.disabled = False
        self.btn_confirmar.text = "CONFIRMAR VENTA"

        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()
