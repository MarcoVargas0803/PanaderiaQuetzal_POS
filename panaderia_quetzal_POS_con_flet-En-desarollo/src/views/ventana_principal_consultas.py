import flet as ft
from Backend.dao_panaderia import (
    obtener_resumen_dashboard, obtener_saldos_apartados, 
    obtener_proximas_entregas, obtener_productos_caducar
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session

class PrincipalConsultasView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.COLOR_FONDO_CARTA = "#E0E5EC"
        self.COLOR_VERDE = "#2ECC71"
        self.COLOR_ROJO = "#E74C3C"
        self.COLOR_NARANJA = "#F6921E"

    def btn_oscuro(self, texto, expand=0, on_click=None):
        return ft.ElevatedButton(
            content=ft.Text(texto, weight="bold", color="white"), 
            style=ft.ButtonStyle(bgcolor=self.COLOR_MARINO, shape=ft.RoundedRectangleBorder(radius=5)),
            expand=expand, on_click=on_click
        )

    def widget_tarjeta(self, titulo: str, valor: str, icono: str, color_icono: str):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=color_icono, size=24),
                ft.Column([
                    ft.Text(titulo, size=9, color="grey", weight="bold"),
                    ft.Text(valor, size=18, weight="bold", color=self.COLOR_MARINO),
                ], spacing=0)
            ]),
            padding=12, bgcolor=self.COLOR_FONDO_CARTA, border_radius=10, expand=True
        )

    def build(self):
        resumen = obtener_resumen_dashboard()
        entregas = obtener_proximas_entregas()
        caducidad = obtener_productos_caducar()
        stock_bajo = resumen.get('inventario_critico', [])
        rentabilidad = resumen.get('rentabilidad', [])
        balance = resumen.get('balance', [])
        estrellas = resumen.get('productos_estrella', [])

        header = ft.Container(
            content=ft.Row([
                ft.Text("PANEL DE ADMINISTRACIÓN", size=22, weight="bold", color=self.COLOR_MARINO),
                ft.Row([
                    ft.TextButton("Dashboard", icon=ft.Icons.DASHBOARD, style=ft.ButtonStyle(color=self.COLOR_MARINO)),
                ], spacing=10),
                ft.ElevatedButton("Salir", icon=ft.Icons.LOGOUT, on_click=lambda _: self.navegar("/"), bgcolor=self.COLOR_ROJO, color="white")
            ], alignment="spaceBetween"),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(1, "#DDDDDD"))
        )

        metricas = ft.Row([
            self.widget_tarjeta("VENTAS HOY", str(resumen.get('ventas_directas', 0)), ft.Icons.SHOPPING_BAG, self.COLOR_VERDE),
            self.widget_tarjeta("INGRESOS", f"${resumen.get('ingresos_hoy', 0):.2f}", ft.Icons.ATTACH_MONEY, self.COLOR_VERDE),
            self.widget_tarjeta("APARTADOS", str(resumen.get('apartados_creados', 0)), ft.Icons.ADD_TASK, self.COLOR_NARANJA),
            self.widget_tarjeta("POR COBRAR", f"${resumen.get('total_pendiente', 0):.2f}", ft.Icons.MONEY_OFF, self.COLOR_NARANJA),
            self.widget_tarjeta("MERMAS", str(resumen.get('unidades_mermadas', 0)), ft.Icons.DELETE_OUTLINE, self.COLOR_ROJO),
        ], spacing=10)

        # SECCIÓN DE ALERTAS CRÍTICAS CON DESCRIPCIÓN
        alertas = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.LOCAL_SHIPPING, size=18, color=self.COLOR_MARINO), ft.Text("ENTREGAS", weight="bold")]),
                    ft.Text("Pedidos para hoy/mañana", size=9, italic=True, color="black"),
                    ft.Column([ft.Text(f" {e['cliente']} ({e['producto']})", size=11) for e in entregas] if entregas else [ft.Text("Sin entregas", size=11)], scroll=ft.ScrollMode.AUTO, height=60),
                ]), expand=1, bgcolor="#E8F5E9", padding=12, border_radius=10
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.INVENTORY_2, color="white", size=18), ft.Text("STOCK BAJO", weight="bold", color="white")]),
                    ft.Text("Productos por agotarse", size=9, italic=True, color="white"),
                    ft.Column([ft.Text(f" {p['producto']}: {p['stock']} pz", color="white", size=11) for p in stock_bajo] if stock_bajo else [ft.Text("Stock OK", color="white", size=11)], scroll=ft.ScrollMode.AUTO, height=60),
                ]), expand=1, bgcolor=self.COLOR_ROJO, padding=12, border_radius=10
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.EVENT_BUSY, color="white", size=18), ft.Text("CADUCIDAD", weight="bold", color="white")]),
                    ft.Text("Vencimiento próximo", size=9, italic=True, color="white"),
                    ft.Column([ft.Text(f" {c['producto']}: {c['dias_restantes']} días", color="white", size=11) for c in caducidad] if caducidad else [ft.Text("Sin riesgos", color="white", size=11)], scroll=ft.ScrollMode.AUTO, height=60),
                ]), expand=1, bgcolor="#D35400", padding=12, border_radius=10
            )
        ], spacing=15)

        # FUNCIONES DE AYUDA PARA GRÁFICOS SENCILLOS
        def barra_progreso(titulo, valor_str, pct, color):
            return ft.Column([
                ft.Row([ft.Text(titulo, size=11, weight="bold"), ft.Text(valor_str, size=11, color=color, weight="bold")], alignment="spaceBetween"),
                ft.ProgressBar(value=pct, color=color, bgcolor="#E0E0E0", height=8, border_radius=4)
            ], spacing=2)

        max_rent = max([float(r['rentabilidad_neta']) for r in rentabilidad]) if rentabilidad else 1
        rentabilidad_ui = ft.Column([barra_progreso(r['producto'], f"${float(r['rentabilidad_neta']):.2f}", min(float(r['rentabilidad_neta'])/max_rent, 1), self.COLOR_VERDE) for r in rentabilidad], spacing=10)

        max_ventas = max([float(p['unidades_vendidas']) for p in estrellas]) if estrellas else 1
        estrellas_ui = ft.Column([barra_progreso(p['producto'], f"{int(p['unidades_vendidas'])} pzas ({p['porcentaje_ventas']}%)", min(float(p['unidades_vendidas'])/max_ventas, 1), self.COLOR_NARANJA) for p in estrellas], spacing=10)

        # SECCIÓN DE EFICIENCIA Y NEGOCIO CON DATOS COMPLETOS
        seccion_negocio = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.ANALYTICS, size=18, color=self.COLOR_MARINO), ft.Text("VENTAS VS MERMAS", weight="bold")]),
                    ft.Text("Balance de eficiencia operativa", size=10, italic=True, color="grey"),
                    ft.Column([
                        ft.Row([
                            ft.Text(f"{b['producto']}", size=11, expand=True), 
                            ft.Text(f"V:{int(b['unidades_vendidas'])}", color=self.COLOR_VERDE, size=10, weight="bold"),
                            ft.Text("/", size=10),
                            ft.Text(f"M:{int(b['unidades_merma'])}", color=self.COLOR_ROJO, size=10, weight="bold")
                        ]) for b in balance[:5]
                    ], scroll=ft.ScrollMode.AUTO, height=130),
                ]), expand=1, bgcolor="#F4F6F7", padding=15, border_radius=10, border=ft.Border.all(1, "#DDDDDD")
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.STAR, size=18, color=self.COLOR_NARANJA), ft.Text("PRODUCTOS ESTRELLA", weight="bold")]),
                    ft.Text("Participación en el ingreso total", size=10, italic=True, color="grey"),
                    ft.Container(content=estrellas_ui, height=130)
                ]), expand=1, bgcolor=self.COLOR_FONDO_CARTA, padding=15, border_radius=10
            ),
            ft.Container(
                content=ft.Column([
                    ft.Row([ft.Icon(ft.Icons.TRENDING_UP, size=18, color=self.COLOR_VERDE), ft.Text("RENTABILIDAD", weight="bold")]),
                    ft.Text("Ganancia real tras costos", size=10, italic=True, color="grey"),
                    ft.Container(content=rentabilidad_ui, height=130)
                ]), expand=1, bgcolor=self.COLOR_FONDO_CARTA, padding=15, border_radius=10
            )
        ], spacing=15)

        return ft.View(
            route="/ventana_principal_consultas", bgcolor="white", padding=0,
            controls=[
                header,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Dashboard de Gestión Administrativa", size=26, weight="bold", color=self.COLOR_MARINO),
                        metricas,
                        ft.Container(
                            content=ft.Row([
                                self.btn_oscuro("Historial de Ventas", expand=1, on_click=lambda _: self.navegar("/consulta_ventas")),
                                self.btn_oscuro("Registro de Auditoría", expand=1, on_click=lambda _: self.navegar("/consulta_auditoria")),
                                ft.ElevatedButton("Catálogos (CRUD)", expand=1, icon=ft.Icons.STORAGE, bgcolor=self.COLOR_MARINO, color="white", on_click=lambda _: self.navegar("/crud_catalogos")),
                            ], spacing=15),
                            padding=ft.padding.symmetric(vertical=10)
                        ),
                        ft.Text("Alertas de Operación", size=18, weight="bold", color=self.COLOR_MARINO),
                        alertas,
                        ft.Divider(height=10, color="transparent"),
                        ft.Text("Análisis de Eficiencia y Rentabilidad", size=18, weight="bold", color=self.COLOR_MARINO),
                        seccion_negocio
                    ], scroll=ft.ScrollMode.AUTO),
                    padding=20, expand=True
                )
            ]
        )