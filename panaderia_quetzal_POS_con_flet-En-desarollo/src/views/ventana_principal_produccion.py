import flet as ft
from Backend.dao_panaderia import (
    obtener_productos_por_categoria,
    registrar_produccion,
    registrar_merma
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session

class PrincipalProduccionView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        
        # Paleta de Colores
        self.COLOR_MARINO = "#2C3545"
        self.COLOR_GRIS_CLARO = "#9BA4B5"
        self.COLOR_FONDO_CARTA = "#E0E5EC"
        self.COLOR_ITEM_LISTA = "#768296"

        # ESTADO
        self.categoria_actual = "Salados" 
        self.lista_produccion = {} # { "Nombre": {"productos_id": 1, "cantidad": 2} }
        
        # REFERENCIAS VISUALES
        self.grid_productos = ft.GridView(
            expand=True, runs_count=5, max_extent=160,
            child_aspect_ratio=0.8, spacing=15, run_spacing=15,
        )
        self.row_categorias = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=10)
        self.columna_items_listado = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=5)

    # --- COMPONENTES REUTILIZABLES ---
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

    def categoria_pill(self, texto):
        es_activo = self.categoria_actual == texto
        return ft.Container(
            content=ft.Text(texto, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if es_activo else self.COLOR_MARINO),
            bgcolor=self.COLOR_MARINO if es_activo else self.COLOR_GRIS_CLARO,
            padding=ft.Padding.symmetric(horizontal=20, vertical=10),
            border_radius=15,
            data=texto,
            on_click=self.click_categoria
        )

    def tarjetas_productos(self, lista_datos, url_imagen="../assets/Concha.png"):
        lista_tarjetas = []
        for pan in lista_datos:
            tarjeta = ft.Container(
                content=ft.Column([
                    ft.Image(src=url_imagen, width=150, height=100, fit=1, border_radius=ft.BorderRadius.only(top_left=10, top_right=10)),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(pan["nombre"], weight=ft.FontWeight.BOLD, size=16, color=self.COLOR_MARINO),
                            ft.Text(f"Stock actual: {pan['stock']}", size=12, color=self.COLOR_MARINO)
                        ], spacing=2),
                        padding=10
                    )
                ], spacing=0),
                bgcolor=self.COLOR_FONDO_CARTA,
                border_radius=10, width=150,
                on_click=lambda e, p=pan: self.agregar_a_lista(p),
            )
            lista_tarjetas.append(tarjeta)
        return lista_tarjetas

    def item_lista(self, nombre, datos):
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Image(src="../assets/Concha.png", fit=1, border_radius=ft.BorderRadius.only(top_left=10, top_right=10)),
                ], expand=True, spacing=0),
                ft.Column([
                    ft.Text(nombre, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, size=14),
                ], expand=True, spacing=0),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color=ft.Colors.WHITE_70, icon_size=20, on_click=lambda _: self.modificar_cantidad(nombre, -1)),
                    ft.Text(str(datos["cantidad"]), weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_color=ft.Colors.WHITE_70, icon_size=20, on_click=lambda _: self.modificar_cantidad(nombre, 1)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, icon_size=20, on_click=lambda _: self.borrar_de_lista(nombre)),
                ], spacing=0)
            ]),
            bgcolor=self.COLOR_ITEM_LISTA,
            padding=10, border_radius=10,
        )

    # --- LOGICA DE ESTADO ---
    def click_categoria(self, e):
        self.categoria_actual = e.control.data
        mapa_cat = {
            "Salados": "Pan salado",
            "Dulces": "Pan dulce",
            "Especial": "Pan especial"
        }
        try:
            datos = obtener_productos_por_categoria(mapa_cat.get(self.categoria_actual, "Pan salado"))
        except Exception as ex:
            print(f"Error cargando DB: {ex}")
            datos = []
            
        self.grid_productos.controls = [*self.tarjetas_productos(datos)]
        self.renderizar_categorias()
        self.grid_productos.update()
        self.row_categorias.update()

    def renderizar_categorias(self):
        categorias = ["Dulces", "Salados", "Especial"]
        self.row_categorias.controls = [self.categoria_pill(c) for c in categorias]

    def agregar_a_lista(self, pan):
        nombre = pan["nombre"]
        if nombre in self.lista_produccion:
            self.lista_produccion[nombre]["cantidad"] += 1
        else:
            self.lista_produccion[nombre] = {
                "productos_id": pan.get("productos_id", 0), 
                "cantidad": 1
            }
        self.actualizar_vista_lista()

    def modificar_cantidad(self, nombre, delta):
        if nombre in self.lista_produccion:
            self.lista_produccion[nombre]["cantidad"] += delta
            if self.lista_produccion[nombre]["cantidad"] <= 0:
                self.lista_produccion.pop(nombre)
        self.actualizar_vista_lista()

    def borrar_de_lista(self, nombre):
        if nombre in self.lista_produccion:
            self.lista_produccion.pop(nombre)
        self.actualizar_vista_lista()

    def actualizar_vista_lista(self):
        self.columna_items_listado.controls.clear()
        total_piezas = 0
        for nombre, datos in self.lista_produccion.items():
            total_piezas += datos["cantidad"]
            self.columna_items_listado.controls.append(self.item_lista(nombre, datos))
        
        self.text_total_piezas.value = f"{total_piezas} piezas en lista"
        self.columna_items_listado.update()
        self.text_total_piezas.update()

    def procesar_transaccion(self, e, tipo_transaccion):
        if not self.lista_produccion:
            return
            
        try:
            usuario_id = 1 # Usuario Harcodeado por ahora
            for nombre, datos in self.lista_produccion.items():
                if tipo_transaccion == "Produccion":
                    registrar_produccion(usuario_id, datos["productos_id"], datos["cantidad"])
                elif tipo_transaccion == "Merma":
                    registrar_merma(usuario_id, datos["productos_id"], datos["cantidad"])
                    
            self.lista_produccion.clear()
            self.actualizar_vista_lista()
            
            # Recargar grid para ver el stock actualizado
            self.click_categoria(type('obj', (object,), {'control': type('obj', (object,), {'data': self.categoria_actual})}))
            
            e.control.page.snack_bar = ft.SnackBar(ft.Text(f"{tipo_transaccion} registrada exitosamente. BD Actualizada."))
            e.control.page.snack_bar.open = True
            e.control.page.update()
            
        except Exception as ex:
            e.control.page.snack_bar = ft.SnackBar(ft.Text(f"Error BD: {ex}", color=ft.Colors.WHITE), bgcolor=ft.Colors.RED)
            e.control.page.snack_bar.open = True
            e.control.page.update()

    # --- CONSTRUCCIÓN DE LA VISTA ---
    def build(self):
        self.text_total_piezas = ft.Text("0 piezas en lista", size=20, weight=ft.FontWeight.BOLD, color=self.COLOR_MARINO, expand=True)

        session = get_session()
        rol = getattr(session, "current_role", None)

        btn_venta = ft.TextButton("Venta", icon=ft.Icons.SHOPPING_CART_SHARP, disabled=(rol not in ["admin", "cajero"]), on_click=lambda _: self.navegar("/ventana_principal") ,style=ft.ButtonStyle(color=ft.Colors.GREY))
        btn_prod = ft.TextButton("Producción", icon=ft.Icons.BAKERY_DINING , style=ft.ButtonStyle(color=self.COLOR_MARINO))
        btn_cons = ft.TextButton("Consultas", icon=ft.Icons.SEARCH, disabled=(rol != "admin"), on_click=lambda _: self.navegar("/ventana_principal_consultas"), style=ft.ButtonStyle(color=ft.Colors.GREY))

        header = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(f"Área de Horneado - ({rol})", color="white", weight=ft.FontWeight.BOLD), bgcolor=self.COLOR_MARINO, padding=10, border_radius=5),
                ft.Row([btn_venta, btn_prod, btn_cons], spacing=20),
                self.btn_blanco("Cerrar Sesión", on_click=lambda _: self.navegar("/"))
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(2, self.COLOR_MARINO))
        )

        self.renderizar_categorias()
        
        try:
            datos_iniciales = obtener_productos_por_categoria("Pan salado")
        except:
            datos_iniciales = []
        self.grid_productos.controls = [*self.tarjetas_productos(datos_iniciales)]

        panel_izquierdo = ft.Container(
            content=ft.Column([
                self.row_categorias,
                ft.Divider(color=self.COLOR_MARINO),
                self.grid_productos
            ]),
            expand=7, padding=15
        )

        panel_derecho = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.columna_items_listado,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Text("Total Piezas", size=20, weight=ft.FontWeight.BOLD, color=self.COLOR_MARINO), 
                        self.text_total_piezas
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=self.COLOR_FONDO_CARTA, padding=15, border_radius=10
                ),
                ft.Container(
                    content=ft.Row([
                        ft.Button(
                            content=ft.Text("Reportar Merma", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), 
                            icon=ft.Icons.WARNING_AMBER, style=ft.ButtonStyle(bgcolor=ft.Colors.RED_400, shape=ft.RoundedRectangleBorder(radius=5)),
                            expand=1, on_click=lambda e: self.procesar_transaccion(e, "Merma")
                        ),
                        ft.Button(
                            content=ft.Text("Registrar Producción", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE), 
                            icon=ft.Icons.CHECK, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, shape=ft.RoundedRectangleBorder(radius=5)),
                            expand=1, on_click=lambda e: self.procesar_transaccion(e, "Produccion")
                        )
                    ], spacing=10),
                    margin=ft.Margin(top=10, left=0, right=0, bottom=0)
                )
            ]),
            expand=3, padding=15, border=ft.Border.only(left=ft.BorderSide(2, self.COLOR_FONDO_CARTA))
        )

        return ft.View(
            route="/ventana_principal_produccion", bgcolor=ft.Colors.WHITE, padding=0,
            controls=[
                header,
                ft.Container(
                    content=ft.Row([panel_izquierdo, panel_derecho], vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
                    expand=True
                )
            ]
        )