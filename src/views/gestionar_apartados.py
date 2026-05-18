import flet as ft
from Backend.dao_panaderia import obtener_saldos_apartados, liquidar_apartado, cancelar_apartado
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session
from components.Toasts import NotificationHelper

class GestionarApartadosView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.periodo_actual = "Todos"

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)

    def cargar_datos(self):
        try:
            datos = obtener_saldos_apartados(self.periodo_actual)
            # Filtrar solo los que tienen saldo pendiente > 0 o estado Pendiente
            self.apartados_pendientes = [d for d in datos if d.get('saldo_pendiente', 0) > 0]
            self.actualizar_lista()
        except Exception as ex:
            print(f"Error cargando apartados: {ex}")

    def mostrar_dialogo_pago(self, apartado):
        session = get_session()
        caja_id = session.current_caja_id
        if not caja_id:
            self._notificar("Debes abrir caja para cobrar", es_error=True)
            return

        saldo = float(apartado['saldo_pendiente'])
        txt_monto = ft.TextField(
            label="Monto a Pagar ($)", 
            value=str(saldo), 
            width=200,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9.]", replacement_string=""),
            max_length=10
        )
        dd_metodo = ft.Dropdown(
            label="Método de Pago",
            options=[
                ft.dropdown.Option("Efectivo"),
                ft.dropdown.Option("Tarjeta"),
                ft.dropdown.Option("Transferencia"),
            ],
            value="Efectivo",
            width=200
        )
        error_text = ft.Text("", color="red", weight="bold")

        def procesar_pago(e):
            try:
                monto_pagar = float(txt_monto.value)
                if monto_pagar <= 0 or monto_pagar > saldo:
                    error_text.value = "Monto inválido"
                    self.page.update()
                    return
                
                liquidar_apartado(apartado['apartados_id'], caja_id, monto_pagar, dd_metodo.value)
                self.cerrar_dialogo()
                self._notificar("Apartado liquidado/abonado con éxito", es_error=False)
                self.cargar_datos()
            except Exception as ex:
                error_text.value = f"Error DB: {ex}"
                self.page.update()

        self.dialogo = ft.AlertDialog(
            title=ft.Text(f"Liquidar Apartado #{apartado['apartados_id']}"),
            content=ft.Column([
                ft.Text(f"Saldo pendiente: ${saldo:.2f}", weight="bold"),
                txt_monto,
                dd_metodo,
                error_text
            ], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Procesar Pago", on_click=procesar_pago, bgcolor="green", color="white")
            ]
        )
        if hasattr(self.page, "open"):
            self.page.open(self.dialogo)
        else:
            if self.dialogo not in self.page.overlay:
                self.page.overlay.append(self.dialogo)
            self.dialogo.open = True
            self.page.update()

    def mostrar_dialogo_cancelar(self, apartado):
        def confirmar_cancelacion(e):
            try:
                cancelar_apartado(apartado['apartados_id'])
                self.cerrar_dialogo()
                self._notificar("Apartado cancelado exitosamente", es_error=False)
                self.cargar_datos()
            except Exception as ex:
                self.cerrar_dialogo()
                self._notificar(f"Error al cancelar: {ex}", es_error=True)
            self.page.update()

        self.dialogo = ft.AlertDialog(
            title=ft.Text(f"Cancelar Apartado #{apartado['apartados_id']}"),
            content=ft.Text("¿Estás seguro de que deseas cancelar este apartado? Esta acción no se puede deshacer y el saldo pendiente será descartado."),
            actions=[
                ft.TextButton("Volver", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Sí, Cancelar", on_click=confirmar_cancelacion, bgcolor="red", color="white")
            ]
        )
        if hasattr(self.page, "open"):
            self.page.open(self.dialogo)
        else:
            if self.dialogo not in self.page.overlay:
                self.page.overlay.append(self.dialogo)
            self.dialogo.open = True
            self.page.update()

    def volver_atras(self, e):
        session = get_session()
        if session.current_role == "admin":
            self.navegar("/ventana_principal_consultas")
        else:
            self.navegar("/ventana_principal")

    def cerrar_dialogo(self):
        if hasattr(self.page, "close"):
            self.page.close(self.dialogo)
        else:
            self.dialogo.open = False
            self.page.update()

    def actualizar_lista(self):
        if not hasattr(self, 'lista_ui'): return
        
        self.lista_ui.controls.clear()
        if not self.apartados_pendientes:
            self.lista_ui.controls.append(ft.Text("No hay apartados pendientes", italic=True))
        else:
            for ap in self.apartados_pendientes:
                def create_pago(apartado_val): return lambda e: self.mostrar_dialogo_pago(apartado_val)
                def create_cancel(apartado_val): return lambda e: self.mostrar_dialogo_cancelar(apartado_val)
                
                tarjeta = ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"Apartado #{ap['apartados_id']} - {ap['cliente']}", weight="bold", size=16),
                                ft.Text(f"Entrega: {ap['fecha_entrega']} | Total: ${ap['total_apartado']:.2f}")
                            ], expand=True),
                            ft.Column([
                                ft.Text(f"Deuda: ${ap['saldo_pendiente']:.2f}", color="red", weight="bold", size=16),
                                ft.Row([
                                    ft.IconButton(icon=ft.Icons.CANCEL, icon_color="red", tooltip="Cancelar Apartado", on_click=create_cancel(ap)),
                                    ft.ElevatedButton("Liquidar", icon=ft.Icons.PAYMENT, bgcolor="green", color="white", on_click=create_pago(ap))
                                ])
                            ], alignment="end")
                        ]),
                        padding=15
                    ),
                    elevation=2
                )
                self.lista_ui.controls.append(tarjeta)
        if self.page:
            self.page.update()

    def build(self):
        self.lista_ui = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        header = ft.Container(
            content=ft.Row([
                ft.Text("LIQUIDACIÓN DE APARTADOS", size=22, weight="bold", color=self.COLOR_MARINO),
                ft.ElevatedButton("Volver", icon=ft.Icons.ARROW_BACK, on_click=self.volver_atras)
            ], alignment="spaceBetween"),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(1, "#DDDDDD"))
        )

        self.dd_periodo = ft.Dropdown(
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Hoy"),
                ft.dropdown.Option("Esta semana"),
                ft.dropdown.Option("Este mes")
            ],
            value="Todos",
            width=150,
            label="Período"
        )

        def aplicar_filtro(e):
            self.periodo_actual = self.dd_periodo.value
            self.cargar_datos()

        filtros = ft.Row([
            self.dd_periodo, 
            ft.ElevatedButton("Filtrar", icon=ft.Icons.FILTER_LIST, on_click=aplicar_filtro, bgcolor=self.COLOR_MARINO, color="white")
        ], alignment="start")

        self.cargar_datos()

        return ft.View(
            route="/gestionar_apartados",
            bgcolor=ft.Colors.WHITE,
            padding=0,
            controls=[
                header,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Selecciona un apartado para registrar su pago y completarlo.", color="grey"),
                        filtros,
                        ft.Divider(height=10, color="transparent"),
                        self.lista_ui
                    ]),
                    padding=20,
                    expand=True
                )
            ]
        )
