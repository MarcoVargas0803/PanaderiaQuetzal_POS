import flet as ft
from Backend.dao_panaderia import (
    obtener_productos_por_categoria, registrar_venta_directa
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session

class PrincipalView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        
        self.COLOR_MARINO = "#2C3545"
        self.COLOR_GRIS_CLARO = "#9BA4B5"
        self.COLOR_FONDO_CARTA = "#E0E5EC"
        self.COLOR_ITEM_LISTA = "#768296"

        self.categoria_actual = "Salados"
        self.carrito = {}
        self.total = 0.0
        self.metodo_pago_actual = "Efectivo"

        self.grid_productos = ft.GridView(expand=True, runs_count=5, max_extent=160, child_aspect_ratio=0.8, spacing=15, run_spacing=15)
        self.row_categorias = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=10)
        self.columna_items_carrito = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)

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

    def ir_a_apartado(self, e):
        if not self.carrito:
            self.page.snack_bar = ft.SnackBar(ft.Text("⚠️ El carrito está vacío"), bgcolor="orange")
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        # GUARDAR CARRITO EN SESIÓN ANTES DE NAVEGAR
        session = get_session()
        session.temp_carrito = self.carrito
        session.temp_total = self.total
        self.navegar("/registrar_apartado")

    def categoria_pill(self, texto):
        es_activo = self.categoria_actual == texto
        return ft.Container(
            content=ft.Text(texto, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if es_activo else self.COLOR_MARINO),
            bgcolor=self.COLOR_MARINO if es_activo else self.COLOR_GRIS_CLARO,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border_radius=15,
            data=texto,
            on_click=self.click_categoria
        )

    def tarjeta_producto(self, pan):
        return ft.Container(
            content=ft.Column([
                ft.Image(src="../assets/Concha.png", width=150, height=100, fit="cover", border_radius=ft.BorderRadius.only(top_left=10, top_right=10)),
                ft.Container(
                    content=ft.Column([
                        ft.Text(pan["nombre"], weight=ft.FontWeight.BOLD, size=16, color=self.COLOR_MARINO),
                        ft.Text(f"${pan['precio']:.2f}", size=12, color=self.COLOR_MARINO)
                    ], spacing=2),
                    padding=10
                )
            ], spacing=0),
            bgcolor=self.COLOR_FONDO_CARTA,
            border_radius=10, width=150,
            on_click=lambda _: self.agregar_al_carrito(pan),
        )

    def item_carrito(self, nombre, datos):
        sub = datos["precio"] * datos["cantidad"]
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(nombre, weight="bold", color="white", size=13, expand=True),
                    ft.Text(f"${datos['precio']:.2f} c/u", color="white", size=11),
                ], expand=True, spacing=0),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", icon_size=20, on_click=lambda _, name=nombre: self.modificar_cant(name, -1)),
                    ft.Text(str(datos["cantidad"]), weight="bold", color="white"),
                    ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", icon_size=20, on_click=lambda _, name=nombre: self.modificar_cant(name, 1)),
                ], spacing=0),
                ft.Text(f"${sub:.2f}", weight="bold", color="white", width=60, text_align="right")
            ]),
            bgcolor=self.COLOR_ITEM_LISTA, padding=10, border_radius=10
        )

    def renderizar_categorias(self):
        categorias = ["Dulces", "Salados", "Especial"]
        self.row_categorias.controls = [self.categoria_pill(c) for c in categorias]

    def renderizar_productos(self):
        mapa = {"Salados": "Pan salado", "Dulces": "Pan dulce", "Especial": "Pan especial"}
        try:
            prods = obtener_productos_por_categoria(mapa.get(self.categoria_actual, "Pan salado"))
            self.grid_productos.controls = [self.tarjeta_producto(p) for p in prods]
        except: pass

    def click_categoria(self, e):
        self.categoria_actual = e.control.data
        self.renderizar_productos()
        self.renderizar_categorias()
        self.page.update()

    def agregar_al_carrito(self, p):
        n = p["nombre"]
        if n in self.carrito: self.carrito[n]["cantidad"] += 1
        else: self.carrito[n] = {"producto_id": int(p["productos_id"]), "precio": float(p["precio"]), "cantidad": 1}
        self.actualizar_carrito_visual()

    def actualizar_carrito_visual(self):
        self.columna_items_carrito.controls = [self.item_carrito(n, d) for n, d in self.carrito.items()]
        self.total = sum(d["precio"] * d["cantidad"] for d in self.carrito.values())
        self.txt_total.value = f"${self.total:.2f}"
        self.page.update()

    def modificar_cant(self, n, d):
        if n in self.carrito:
            self.carrito[n]["cantidad"] += d
            if self.carrito[n]["cantidad"] <= 0: self.carrito.pop(n)
        self.actualizar_carrito_visual()

    def finalizar_venta(self, e):
        if not self.carrito: return
        session = get_session()
        detalles = [{"productos_id": v["producto_id"], "cantidad": v["cantidad"]} for v in self.carrito.values()]
        try:
            registrar_venta_directa(int(session.current_user_id), int(session.current_caja_id), self.total, detalles, self.metodo_pago_actual)
            self.carrito.clear()
            self.actualizar_carrito_visual()
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Venta Exitosa"), bgcolor="green")
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ Error: {ex}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def build(self):
        session = get_session()
        self.txt_total = ft.Text("$0.00", size=24, weight="bold", color=self.COLOR_MARINO)
        self.renderizar_categorias()
        self.renderizar_productos()

        header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(f"Punto de Venta - ({session.current_user})", color="white", weight=ft.FontWeight.BOLD), bgcolor=self.COLOR_MARINO, padding=10, border_radius=5),
                ft.Row([
                    ft.TextButton("Venta", icon=ft.Icons.SHOPPING_CART_SHARP, style=ft.ButtonStyle(color=self.COLOR_MARINO)),
                ], spacing=20),
                ft.Row([
                    ft.ElevatedButton("Liquidar Apartados", icon=ft.Icons.ATTACH_MONEY, on_click=lambda _: self.navegar("/gestionar_apartados"), bgcolor="#27AE60", color="white"),
                    self.btn_blanco("Cerrar Sesión", on_click=lambda _: self.navegar("/")),
                    ft.ElevatedButton("Cerrar Caja", icon=ft.Icons.OUTBOX, on_click=lambda _: self.navegar("/corte_caja"), bgcolor="red", color="white")
                ], spacing=10)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(2, self.COLOR_MARINO))
        )

        panel_derecho = ft.Container(
            content=ft.Column([
                ft.Text("CARRITO ACTUAL", weight="bold", size=18, color=self.COLOR_MARINO),
                ft.Container(content=self.columna_items_carrito, expand=True),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("Total", size=20, weight="bold", color=self.COLOR_MARINO), self.txt_total], alignment="spaceBetween"),
                        ft.Row([
                            ft.ElevatedButton("CLIENTE", on_click=lambda _: self.navegar("/registrar_cliente"), expand=1, bgcolor=self.COLOR_ITEM_LISTA, color="white"),
                            ft.ElevatedButton("APARTADO", on_click=self.ir_a_apartado, expand=1, bgcolor="#F6921E", color="white"),
                        ], spacing=10),
                        ft.ElevatedButton("COBRAR VENTA", icon=ft.Icons.CHECK, on_click=self.finalizar_venta, bgcolor="#27AE60", color="white", expand=True, height=50)
                    ]),
                    bgcolor=self.COLOR_FONDO_CARTA, padding=15, border_radius=10
                )
            ]),
            expand=3, padding=15, border=ft.Border.only(left=ft.BorderSide(2, self.COLOR_FONDO_CARTA))
        )

        return ft.View(
            route="/ventana_principal", bgcolor=ft.Colors.WHITE, padding=0,
            controls=[header, ft.Container(content=ft.Row([ft.Container(content=ft.Column([self.row_categorias, ft.Divider(color=self.COLOR_MARINO), self.grid_productos]), expand=7, padding=15), panel_derecho], expand=True), expand=True)]
        )