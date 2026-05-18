import flet as ft
from database import get_db_connection
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session
from components.Toasts import NotificationHelper

class ConsultaAuditoriaView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.COLOR_VERDE = "#2ECC71"
        self.COLOR_NARANJA = "#F39C12"
        self.COLOR_ROJO = "#E74C3C"
        self.COLOR_AZUL = "#3498DB"

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)
    
    def _handle_salir(self, e):
        self.navegar("/")
        self._notificar("Sesión cerrada", es_error=False)

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
            padding=ft.Padding(left=8, top=4, right=8, bottom=4),
            border_radius=5,
            alignment=ft.Alignment(0, 0),
            width=70
        )

    def crear_fila(self, d):
        return ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(str(d['auditoria_id']), weight="bold", size=12), expand=1),
                ft.Container(content=ft.Text(d['fecha'].strftime("%d/%m/%Y %H:%M") if hasattr(d['fecha'], "strftime") else str(d['fecha']), size=12), expand=2),
                ft.Container(content=ft.Text(str(d['empleado']), size=12), expand=2),
                ft.Container(content=ft.Text(str(d['modulo_afectado']).upper(), weight="bold", size=11, color=self.COLOR_MARINO), expand=2),
                ft.Container(content=self.badge_operacion(str(d['operacion'])), expand=1),
                ft.Container(content=ft.Text(str(d['detalle']), size=11), expand=3),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(top=10, bottom=10, left=5, right=5),
            border=ft.Border(bottom=ft.BorderSide(1, "#EEEEEE"))
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
                    ft.ElevatedButton("Salir", icon=ft.Icons.LOGOUT, on_click=self._handle_salir, bgcolor=self.COLOR_ROJO, color="white")
                ], spacing=10)
            ], alignment="spaceBetween"),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(1, "#DDDDDD"))
        )

        lista_registros = ft.Column([self.crear_fila(d) for d in datos], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

        def set_filter(modulo):
            if modulo == 'general':
                lista_registros.controls = [self.crear_fila(d) for d in datos]
            else:
                lista_registros.controls = [self.crear_fila(d) for d in datos if d['modulo_afectado'].lower() == 'movimientos']
            self.page.update()

        filtros = ft.Row([
            ft.ElevatedButton("Auditoría General", icon=ft.Icons.LIST, bgcolor=self.COLOR_MARINO, color="white", on_click=lambda _: set_filter('general')),
            ft.ElevatedButton("Mermas y Producción (Movimientos)", icon=ft.Icons.WARNING, bgcolor=self.COLOR_NARANJA, color="white", on_click=lambda _: set_filter('movimientos')),
        ], spacing=10)

        cabecera_tabla = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("ID", weight="bold", color=self.COLOR_MARINO), expand=1),
                ft.Container(content=ft.Text("Fecha/Hora", weight="bold", color=self.COLOR_MARINO), expand=2),
                ft.Container(content=ft.Text("Empleado", weight="bold", color=self.COLOR_MARINO), expand=2),
                ft.Container(content=ft.Text("Módulo", weight="bold", color=self.COLOR_MARINO), expand=2),
                ft.Container(content=ft.Text("Operación", weight="bold", color=self.COLOR_MARINO), expand=1),
                ft.Container(content=ft.Text("Detalle del Cambio", weight="bold", color=self.COLOR_MARINO), expand=3),
            ]),
            bgcolor="#F4F6F7",
            padding=ft.Padding(top=15, bottom=15, left=5, right=5),
            border_radius=5
        )

        tabla_ui = ft.Container(
            content=ft.Column([
                cabecera_tabla,
                lista_registros
            ], expand=True),
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
                        filtros,
                        tabla_ui
                    ]),
                    padding=20, expand=True
                )
            ]
        )
