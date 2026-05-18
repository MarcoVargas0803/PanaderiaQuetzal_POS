import flet as ft
from Backend.dao_panaderia import obtener_historial_ventas
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session
from components.Toasts import NotificationHelper

class ConsultaVentasView:
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

    def badge_tipo(self, es_apartado: bool):
        texto = "APARTADO" if es_apartado else "DIRECTA"
        color_fondo = self.COLOR_NARANJA if es_apartado else self.COLOR_VERDE
        icono = ft.Icons.BOOKMARK if es_apartado else ft.Icons.SHOPPING_CART
        
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, size=14, color="white"),
                ft.Text(texto, weight="bold", color="white", size=11)
            ], alignment="center", spacing=5),
            bgcolor=color_fondo,
            padding=ft.Padding(left=10, top=5, right=10, bottom=5),
            border_radius=10,
            width=110
        )

    def crear_fila(self, v):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(str(v["folio"]), weight="bold"), expand=1),
                ft.Container(content=ft.Text(v["fecha"].strftime("%d/%m/%Y %H:%M") if hasattr(v["fecha"], "strftime") else str(v["fecha"])), expand=2),
                ft.Container(content=ft.Text(v["cajero"]), expand=2),
                ft.Container(content=ft.Text(v["producto"]), expand=3),
                ft.Container(content=ft.Text(str(v["cantidad"])), expand=1),
                ft.Container(content=ft.Text(f"${v['precio']:.2f}"), expand=1),
                ft.Container(content=ft.Text(f"${v['subtotal']:.2f}", weight="bold"), expand=1),
                ft.Container(content=self.badge_tipo(bool(v["es_apartado"])), expand=2),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(top=10, bottom=10, left=5, right=5),
            border=ft.Border(bottom=ft.BorderSide(1, "#EEEEEE"))
        )

    def build(self):
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.HISTORY, color=self.COLOR_MARINO),
                    ft.Text("HISTORIAL DE VENTAS", size=20, weight="bold", color=self.COLOR_MARINO),
                ]),
                ft.Row([
                    self.btn_blanco("Panel Admin", on_click=lambda _: self.navegar("/ventana_principal_consultas"), icon=ft.Icons.DASHBOARD),
                    self.btn_oscuro("Salir", on_click=self._handle_salir)
                ], spacing=10)
            ], alignment="spaceBetween"),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(1, "#DDDDDD"))
        )

        # Cargar Datos
        filas = []
        try:
            ventas = obtener_historial_ventas(limite=50)
            filas = [self.crear_fila(v) for v in ventas]
        except Exception as ex:
            filas = [ft.Text(f"Error: {ex}", color="red")]

        cabecera_tabla = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("Folio", weight="bold", color=self.COLOR_MARINO), expand=1),
                ft.Container(content=ft.Text("Fecha/Hora", weight="bold", color=self.COLOR_MARINO), expand=2),
                ft.Container(content=ft.Text("Cajero", weight="bold", color=self.COLOR_MARINO), expand=2),
                ft.Container(content=ft.Text("Producto", weight="bold", color=self.COLOR_MARINO), expand=3),
                ft.Container(content=ft.Text("Cant.", weight="bold", color=self.COLOR_MARINO), expand=1),
                ft.Container(content=ft.Text("Precio", weight="bold", color=self.COLOR_MARINO), expand=1),
                ft.Container(content=ft.Text("Subtotal", weight="bold", color=self.COLOR_MARINO), expand=1),
                ft.Container(content=ft.Text("Tipo", weight="bold", color=self.COLOR_MARINO), expand=2),
            ]),
            bgcolor="#F4F6F7",
            padding=ft.Padding(top=15, bottom=15, left=5, right=5),
            border_radius=5
        )

        lista_registros = ft.Column(filas, scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

        tabla = ft.Container(
            content=ft.Column([
                cabecera_tabla,
                lista_registros
            ], expand=True),
            padding=20, expand=True
        )

        return ft.View( route="/consulta_ventas", bgcolor="white", padding=0, controls=[header, tabla] )