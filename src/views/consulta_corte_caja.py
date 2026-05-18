import flet as ft
from Backend.dao_panaderia import consulta_corte_caja
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session
from components.Toasts import NotificationHelper

class ConsultaCorteCajaView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.COLOR_VERDE = "#2ECC71"
        self.COLOR_NARANJA = "#F6921E"

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)
    
    def _handle_salir(self, e):
        self.navegar("/")
        self._notificar("Sesión cerrada", es_error=False)

    def btn_oscuro(self, texto, expand=0, on_click=None):
        return ft.ElevatedButton(
            content=ft.Text(texto, weight="bold", color="white"), 
            style=ft.ButtonStyle(bgcolor=self.COLOR_MARINO, shape=ft.RoundedRectangleBorder(radius=5)),
            expand=expand, on_click=on_click
        )

    def btn_blanco(self, texto, expand=0, icon=None, on_click=None):
        return ft.Button(
            content=ft.Text(texto, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK), 
            icon=icon,
            style=ft.ButtonStyle(
                color=self.COLOR_MARINO,
                side=ft.BorderSide(1, self.COLOR_MARINO),
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            expand=expand, on_click=on_click
        )

    def crear_tarjeta(self, c):
        folio = str(c.get("cajas_id", ""))
        cajero = str(c.get("cajero", ""))
        apertura = c.get("fecha_apertura")
        apertura = apertura.strftime("%d/%m/%Y %H:%M") if apertura and hasattr(apertura, "strftime") else str(apertura)
        
        cierre = c.get("fecha_cierre")
        if cierre and hasattr(cierre, "strftime"):
            cierre = cierre.strftime("%d/%m/%Y %H:%M")
        else:
            cierre = "Activa" if not cierre else str(cierre)
            
        def fmt(key):
            val = c.get(key)
            if val is None:
                return "$0.00"
            return f"${float(val):.2f}"

        dif_val = float(c.get("diferencia") or 0)
        color_dif = self.COLOR_VERDE if dif_val >= 0 else "red"
        
        # Tarjeta expandible
        return ft.Card(
            elevation=2,
            margin=ft.Margin(0, 0, 0, 10),
            content=ft.ExpansionTile(
                title=ft.Row([
                    ft.Text(f"Corte #{folio}", weight="bold", size=16),
                    ft.Text(f"Cajero: {cajero}", color=self.COLOR_MARINO)
                ], spacing=20),
                subtitle=ft.Row([
                    ft.Text(f"Cierre: {cierre}", color="grey", size=12),
                    ft.Text(f"Diferencia: {fmt('diferencia')}", color=color_dif, weight="bold", size=12)
                ], spacing=20),
                leading=ft.Icon(ft.Icons.RECEIPT_LONG, color=self.COLOR_MARINO),
                controls=[
                    ft.Container(
                        content=ft.Row([
                            # Columna 1: Resumen
                            ft.Column([
                                ft.Text("RESUMEN DE OPERACIÓN", weight="bold", color=self.COLOR_MARINO),
                                ft.Text(f"Apertura: {apertura}", size=12),
                                ft.Text(f"Cierre: {cierre}", size=12),
                                ft.Text(f"Saldo Inicial: {fmt('saldo_inicial')}", size=12),
                                ft.Text(f"Total Cobrado: {fmt('total_cobrado')}", size=12),
                                ft.Text(f"Saldo Final Declarado: {fmt('saldo_final')}", size=12),
                            ], expand=1),
                            # Columna 2: Desglose
                            ft.Column([
                                ft.Text("DESGLOSE DE INGRESOS", weight="bold", color=self.COLOR_MARINO),
                                ft.Text(f"Ventas Efectivo: {fmt('ventas_efectivo')}", size=12),
                                ft.Text(f"Ventas Tarjeta: {fmt('ventas_tarjeta')}", size=12),
                                ft.Text(f"Ventas Transf.: {fmt('ventas_transferencia')}", size=12),
                                ft.Text(f"Anticipos: {fmt('total_anticipos')}", size=12),
                                ft.Text(f"Liquidaciones: {fmt('total_liquidaciones')}", size=12),
                            ], expand=1),
                            # Columna 3: Totales por Método
                            ft.Column([
                                ft.Text("TOTALES METODOS", weight="bold", color=self.COLOR_MARINO),
                                ft.Text(f"Total Efectivo: {fmt('total_efectivo')}", size=12),
                                ft.Text(f"Total Tarjeta: {fmt('total_tarjeta')}", size=12),
                                ft.Text(f"Esperado en Caja: {fmt('saldo_esperado_efectivo')}", weight="bold", color=self.COLOR_MARINO, size=13),
                            ], expand=1),
                        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
                        padding=ft.Padding(15, 10, 15, 20),
                        bgcolor="#F8F9FA",
                        border_radius=ft.BorderRadius(bottom_left=10, bottom_right=10, top_left=0, top_right=0)
                    )
                ]
            )
        )

    def build(self):
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.POINT_OF_SALE, color=self.COLOR_MARINO),
                    ft.Text("HISTORIAL DE CORTES DE CAJA", size=20, weight="bold", color=self.COLOR_MARINO),
                ]),
                ft.Row([
                    self.btn_blanco("Panel Admin", on_click=lambda _: self.navegar("/ventana_principal_consultas"), icon=ft.Icons.DASHBOARD),
                    self.btn_oscuro("Salir", on_click=self._handle_salir)
                ], spacing=10)
            ], alignment="spaceBetween"),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(1, "#DDDDDD"))
        )

        # Cargar Datos
        tarjetas = []
        try:
            cortes = consulta_corte_caja()
            tarjetas = [self.crear_tarjeta(c) for c in cortes]
        except Exception as ex:
            tarjetas = [ft.Text(f"Error cargando datos: {ex}", color="red")]

        lista_tarjetas = ft.Container(
            content=ft.Column(tarjetas, scroll=ft.ScrollMode.AUTO, spacing=5),
            padding=20, expand=True
        )

        return ft.View( route="/consulta_corte_caja", bgcolor="white", padding=0, controls=[header, lista_tarjetas] )
