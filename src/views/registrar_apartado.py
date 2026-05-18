import flet as ft
from Backend.dao_panaderia import registrar_apartado_detallado, obtener_clientes
from session_state import get_session
from components.Toasts import NotificationHelper
import time
from datetime import date, datetime, timedelta

class RegistrarApartadoView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.metodo_pago = "Efectivo" # Valor por defecto

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)

    def cambiar_pago(self, e):
        self.metodo_pago = e.control.data
        self.page.update()

    def confirmar(self, e):
        session = get_session()

        # Validar cliente seleccionado
        if not self.dd_cliente.value:
            self._notificar("Seleccione un cliente para continuar", es_error=True)
            return

        # Validar anticipo
        try:
            anticipo = round(float(str(self.txt_anticipo.value or "0").replace(",", ".")), 2)
        except ValueError:
            self.txt_anticipo.error_text = "Ingrese un monto válido"
            self.txt_anticipo.update()
            return

        minimo = round(session.temp_total * 0.20, 2)
        if anticipo <= 0:
            self.txt_anticipo.error_text = "El anticipo debe ser mayor a cero"
            self.txt_anticipo.update()
            return
        elif anticipo < minimo:
            self.txt_anticipo.error_text = f"El anticipo mínimo es ${minimo:.2f} (20% del total)"
            self.txt_anticipo.update()
            return
        elif anticipo > session.temp_total:
            self.txt_anticipo.error_text = "El anticipo no puede superar el total del pedido"
            self.txt_anticipo.update()
            return
        else:
            self.txt_anticipo.error_text = None
            self.txt_anticipo.update()

        # Validar fecha
        fecha_str = self.txt_fecha.value.strip()
        try:
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            self.txt_fecha.error_text = "Formato inválido. Use: AAAA-MM-DD"
            self.txt_fecha.update()
            return

        if fecha_obj <= date.today():
            self.txt_fecha.error_text = "La fecha de entrega debe ser una fecha futura"
            self.txt_fecha.update()
            return
        else:
            self.txt_fecha.error_text = None
            self.txt_fecha.update()

        try:
            e.control.disabled = True
            e.control.text = "Procesando..."
            self.page.update()

            detalles = [{"productos_id": v["producto_id"], "cantidad": v["cantidad"]} for v in session.temp_carrito.values()]

            registrar_apartado_detallado(
                int(session.current_user_id),
                int(session.current_caja_id),
                int(self.dd_cliente.value),
                fecha_str,
                anticipo,
                session.temp_total,
                detalles,
                self.metodo_pago
            )

            session.temp_carrito = {}
            session.temp_total = 0.0

            self._notificar("APARTADO REGISTRADO CON ÉXITO", es_error=False)

            time.sleep(1.2)
            self.navegar("/ventana_principal")

        except Exception as ex:
            e.control.disabled = False
            e.control.text = "CONFIRMAR Y CREAR APARTADO"
            self._notificar(f"Error: {ex}", es_error=True)
            self.page.update()

    def build(self):
        session = get_session()
        clientes = obtener_clientes()
        
        self.dd_cliente = ft.Dropdown(
            label="Elegir Cliente",
            options=[ft.dropdown.Option(str(c['clientes_id']), c['nombre']) for c in clientes],
            width=400
        )
        
        self.txt_anticipo = ft.TextField(label="Anticipo Recibido ($)", value=str(round(session.temp_total * 0.20, 2)), width=195)
        fecha_minima = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.txt_fecha = ft.TextField(label="Fecha de Entrega (AAAA-MM-DD)", value=fecha_minima, width=195, hint_text="ej. 2026-06-01")

        # Selector de Método de Pago
        selector_pago = ft.Container(
            content=ft.Row([
                ft.Text("PAGO CON:", weight="bold", size=12),
                ft.Row([
                    ft.ElevatedButton("EFECTIVO", icon=ft.Icons.MONEY, data="Efectivo", on_click=self.cambiar_pago, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN if self.metodo_pago=="Efectivo" else "grey", color="white")),
                    ft.ElevatedButton("TARJETA", icon=ft.Icons.CREDIT_CARD, data="Tarjeta", on_click=self.cambiar_pago, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE if self.metodo_pago=="Tarjeta" else "grey", color="white")),
                ], spacing=10)
            ], alignment="center"),
            padding=10
        )

        tarjeta = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BOOKMARK_ADDED, size=50, color="#F6921E"),
                    ft.Text("RESUMEN DE APARTADO", size=24, weight="bold", color=self.COLOR_MARINO),
                    ft.Text(f"Total de la orden: ${session.temp_total:.2f}", size=18, weight="bold", color="#27AE60"),
                    ft.Divider(),
                    self.dd_cliente,
                    ft.Row([self.txt_anticipo, self.txt_fecha], spacing=10, alignment="center"),
                    selector_pago,
                    ft.Divider(),
                    ft.ElevatedButton("CONFIRMAR Y CREAR APARTADO", on_click=self.confirmar, bgcolor="#F6921E", color="white", height=50, width=400),
                    ft.TextButton("CANCELAR", on_click=lambda _: self.navegar("/ventana_principal"))
                ], spacing=15, horizontal_alignment="center"),
                padding=30, width=480
            ),
            elevation=15
        )

        return ft.View(
            route="/registrar_apartado",
            bgcolor="#F0F2F5",
            controls=[
                ft.AppBar(title=ft.Text("Registro de Apartado"), bgcolor=self.COLOR_MARINO, color="white"),
                ft.Container(
                    content=ft.Row([tarjeta], alignment="center"),
                    expand=True,
                    alignment=ft.Alignment(0, 0)
                )
            ]
        )
