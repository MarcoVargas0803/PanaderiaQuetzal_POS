import flet as ft
from database import get_db_connection
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session

class ConsultaAuditoriaView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.COLOR_VERDE = "#2ECC71"
        self.COLOR_NARANJA = "#F39C12"
        self.COLOR_ROJO = "#E74C3C"
        self.COLOR_AZUL = "#3498DB"

    def obtener_auditoria(self):
        datos = []
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM vista_auditoria_general ORDER BY fecha DESC LIMIT 100")
                datos = cursor.fetchall()
        except Exception as ex:
            print(f"Error auditoria: {ex}")
        return datos

    def badge_operacion(self, op: str):
        colores = {
            "INSERT": self.COLOR_VERDE,
            "UPDATE": self.COLOR_AZUL,
            "DELETE": self.COLOR_ROJO
        }
        color_fondo = colores.get(op, "grey")
        
        return ft.Container(
            content=ft.Text(op, weight="bold", color="white", size=10),
            bgcolor=color_fondo,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=5,
            alignment=ft.alignment.center,
            width=70
        )

    def crear_fila(self, d):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(d['auditoria_id']), weight="bold", size=12)),
                ft.DataCell(ft.Text(d['fecha'].strftime("%d/%m/%Y %H:%M") if hasattr(d['fecha'], "strftime") else str(d['fecha']), size=12)),
                ft.DataCell(ft.Text(str(d['empleado']), size=12)),
                ft.DataCell(ft.Text(str(d['modulo_afectado']).upper(), weight="bold", size=11, color=self.COLOR_MARINO)),
                ft.DataCell(self.badge_operacion(str(d['operacion']))),
                ft.DataCell(ft.Container(content=ft.Text(str(d['detalle']), size=11), width=400)),
            ]
        )

    def build(self):
        datos = self.obtener_auditoria()
        
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SHIELD_MOON, color=self.COLOR_MARINO),
                    ft.Text("REGISTRO DE AUDITORÍA", size=20, weight="bold", color=self.COLOR_MARINO),
                ]),
                ft.Row([
                    ft.ElevatedButton("Panel Admin", icon=ft.Icons.DASHBOARD, on_click=lambda _: self.navegar("/ventana_principal_consultas"), bgcolor=self.COLOR_MARINO, color="white"),
                    ft.ElevatedButton("Salir", icon=ft.Icons.LOGOUT, on_click=lambda _: self.navegar("/"), bgcolor=self.COLOR_ROJO, color="white")
                ], spacing=10)
            ], alignment="spaceBetween"),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(1, "#DDDDDD"))
        )

        tabla_ui = ft.Container(
            content=ft.Column([
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Fecha/Hora")),
                        ft.DataColumn(ft.Text("Empleado")),
                        ft.DataColumn(ft.Text("Módulo")),
                        ft.DataColumn(ft.Text("Operación")),
                        ft.DataColumn(ft.Text("Detalle del Cambio")),
                    ],
                    rows=[self.crear_fila(d) for d in datos],
                    heading_row_color="#F4F6F7",
                    column_spacing=20,
                    expand=True
                )
            ], scroll=ft.ScrollMode.AUTO),
            padding=20, expand=True
        )

        return ft.View(
            route="/consulta_auditoria",
            bgcolor="white",
            padding=0,
            controls=[
                header,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Bitácora de movimientos en el sistema", size=16, color="grey"),
                        tabla_ui
                    ]),
                    padding=20, expand=True
                )
            ]
        )
