import flet as ft
from Backend.dao_panaderia import obtener_historial_ventas
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session

class ConsultaVentasView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.COLOR_VERDE = "#2ECC71"
        self.COLOR_NARANJA = "#F6921E"

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
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=10,
            width=110
        )

    def crear_fila(self, v):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(v["folio"]), weight="bold")),
                ft.DataCell(ft.Text(v["fecha"].strftime("%d/%m/%Y %H:%M") if hasattr(v["fecha"], "strftime") else str(v["fecha"]))),
                ft.DataCell(ft.Text(v["cajero"])),
                ft.DataCell(ft.Text(v["producto"])),
                ft.DataCell(ft.Text(str(v["cantidad"]))),
                ft.DataCell(ft.Text(f"${v['precio']:.2f}")),
                ft.DataCell(ft.Text(f"${v['subtotal']:.2f}", weight="bold")),
                ft.DataCell(self.badge_tipo(bool(v["es_apartado"]))),
            ]
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
                    self.btn_oscuro("Salir", on_click=lambda _: self.navegar("/"))
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
            filas = [ft.DataRow(cells=[ft.DataCell(ft.Text(f"Error: {ex}"))] + [ft.DataCell(ft.Text(""))]*7)]

        tabla = ft.Container(
            content=ft.Column([
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Folio")),
                        ft.DataColumn(ft.Text("Fecha/Hora")),
                        ft.DataColumn(ft.Text("Cajero")),
                        ft.DataColumn(ft.Text("Producto")),
                        ft.DataColumn(ft.Text("Cant."), numeric=True),
                        ft.DataColumn(ft.Text("Precio"), numeric=True),
                        ft.DataColumn(ft.Text("Subtotal"), numeric=True),
                        ft.DataColumn(ft.Text("Tipo")),
                    ],
                    rows=filas,
                    heading_row_color="#F4F6F7",
                    column_spacing=20,
                    expand=True
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=20, expand=True
        )

        return ft.View( route="/consulta_ventas", bgcolor="white", padding=0, controls=[header, tabla] )