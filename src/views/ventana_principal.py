import flet as ft
from Backend.dao_panaderia import (
    obtener_productos_por_categoria, registrar_venta_directa, obtener_nombre_usuario, registrar_cliente,
    obtener_clientes, registrar_apartado_detallado
)
import sys
import os
from datetime import date, datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session
from components.Toasts import NotificationHelper

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

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)

    def _handle_salir(self, e):
        self.navegar("/")
        self._notificar("Sesión cerrada")

    def mostrar_dialogo_cliente(self, e):
        txt_nombre = ft.TextField(label="Nombre Completo", autofocus=True, prefix_icon=ft.Icons.PERSON)
        txt_telefono = ft.TextField(
            label="Teléfono (10 dígitos)", 
            prefix_icon=ft.Icons.PHONE,
            input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
            max_length=10
        )

        def guardar(e):
            nombre = txt_nombre.value.strip()
            telefono = txt_telefono.value.strip()

            if not nombre:
                txt_nombre.error_text = "El nombre es obligatorio"
                txt_nombre.update()
                return
            else:
                txt_nombre.error_text = None
                txt_nombre.update()

            if telefono and (not telefono.isdigit() or len(telefono) != 10):
                txt_telefono.error_text = "El teléfono debe tener 10 dígitos numéricos"
                txt_telefono.update()
                return
            else:
                txt_telefono.error_text = None
                txt_telefono.update()

            try:
                registrar_cliente(nombre, telefono if telefono else None)
                self._notificar("¡Cliente registrado con éxito!", es_error=False)
                self.cerrar_dialogo_cliente(self.dialogo_cliente)
            except Exception as ex:
                self._notificar(f"Error al registrar: {ex}", es_error=True)
                self.page.update()

        self.dialogo_cliente = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PERSON_ADD, size=50, color=self.COLOR_MARINO),
                    ft.Text("REGISTRO DE CLIENTE", size=22, weight="bold", color=self.COLOR_MARINO),
                    ft.Text("Ingrese los datos para habilitar apartados", color="grey"),
                    ft.Divider(),
                    txt_nombre,
                    txt_telefono,
                    ft.Divider(),
                    ft.Row([
                        ft.ElevatedButton("GUARDAR", on_click=guardar, bgcolor="#27AE60", color="white", height=45, expand=1),
                        ft.TextButton("CANCELAR", on_click=lambda _: self.cerrar_dialogo_cliente(self.dialogo_cliente), height=45)
                    ], spacing=10)
                ], spacing=20, horizontal_alignment="center", tight=True),
                padding=20,
                width=400
            )
        )
        
        if hasattr(self.page, "open"):
            self.page.open(self.dialogo_cliente)
        else:
            if self.dialogo_cliente not in self.page.overlay:
                self.page.overlay.append(self.dialogo_cliente)
            self.dialogo_cliente.open = True
            self.page.update()

    def cerrar_dialogo_cliente(self, dialog):
        if hasattr(self.page, "close"):
            self.page.close(dialog)
        else:
            dialog.open = False
            self.page.update()

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

    def mostrar_dialogo_apartado(self, e):
        if not self.carrito:
            self._notificar("El carrito está vacío", es_error=True)
            return

        session = get_session()
        clientes = obtener_clientes()
        
        dd_cliente = ft.Dropdown(
            label="Elegir Cliente",
            options=[ft.dropdown.Option(str(c['clientes_id']), c['nombre']) for c in clientes],
            width=400
        )
        
        txt_anticipo = ft.TextField(label="Anticipo Recibido ($)", value=str(round(self.total * 0.20, 2)), width=195)
        fecha_minima = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        txt_fecha = ft.TextField(label="Fecha de Entrega (AAAA-MM-DD)", value=fecha_minima, width=195, hint_text="ej. 2026-06-01")

        self.metodo_pago_apartado = "Efectivo"
        
        btn_efectivo = ft.ElevatedButton("EFECTIVO", icon=ft.Icons.MONEY, style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN, color="white"))
        btn_tarjeta = ft.ElevatedButton("TARJETA", icon=ft.Icons.CREDIT_CARD, style=ft.ButtonStyle(bgcolor="grey", color="white"))

        def cambiar_pago(e, metodo):
            self.metodo_pago_apartado = metodo
            btn_efectivo.style.bgcolor = ft.Colors.GREEN if metodo == "Efectivo" else "grey"
            btn_tarjeta.style.bgcolor = ft.Colors.BLUE if metodo == "Tarjeta" else "grey"
            self.dialogo_apartado.update()

        btn_efectivo.on_click = lambda e: cambiar_pago(e, "Efectivo")
        btn_tarjeta.on_click = lambda e: cambiar_pago(e, "Tarjeta")

        selector_pago = ft.Container(
            content=ft.Row([
                ft.Text("PAGO CON:", weight="bold", size=12),
                ft.Row([btn_efectivo, btn_tarjeta], spacing=10)
            ], alignment="center"),
            padding=10
        )

        def confirmar(e):
            if not dd_cliente.value:
                self._notificar("Seleccione un cliente para continuar", es_error=True)
                return

            try:
                anticipo = round(float(str(txt_anticipo.value or "0").replace(",", ".")), 2)
            except ValueError:
                txt_anticipo.error_text = "Ingrese un monto válido"
                txt_anticipo.update()
                return

            minimo = round(self.total * 0.20, 2)
            if anticipo <= 0:
                self._notificar("El anticipo debe ser mayor a cero", es_error=True)
                txt_anticipo.error_text = "El anticipo debe ser mayor a cero"
                txt_anticipo.update()
                return
            elif anticipo < minimo:
                self._notificar(f"El anticipo mínimo es ${minimo:.2f} (20% del total)", es_error=True)
                txt_anticipo.error_text = f"El anticipo mínimo es ${minimo:.2f} (20% del total)"
                txt_anticipo.update()
                return
            elif anticipo > self.total:
                self._notificar("El anticipo no puede superar el total", es_error=True)
                txt_anticipo.error_text = "El anticipo no puede superar el total del pedido"
                txt_anticipo.update()
                return
            else:
                txt_anticipo.error_text = None
                txt_anticipo.update()

            fecha_str = txt_fecha.value.strip()
            try:
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                self._notificar("Formato de fecha inválido", es_error=True)
                txt_fecha.error_text = "Formato inválido. Use: AAAA-MM-DD"
                txt_fecha.update()
                return

            if fecha_obj <= date.today():
                self._notificar("La fecha de entrega debe ser futura", es_error=True)
                txt_fecha.error_text = "La fecha debe ser futura"
                txt_fecha.update()
                return
            else:
                txt_fecha.error_text = None
                txt_fecha.update()

            try:
                e.control.disabled = True
                e.control.text = "Procesando..."
                self.dialogo_apartado.update()

                detalles = [{"productos_id": v["producto_id"], "cantidad": v["cantidad"]} for v in self.carrito.values()]

                registrar_apartado_detallado(
                    int(session.current_user_id),
                    int(session.current_caja_id),
                    int(dd_cliente.value),
                    fecha_str,
                    anticipo,
                    self.total,
                    detalles,
                    self.metodo_pago_apartado
                )

                self.carrito.clear()
                self.actualizar_carrito_visual()

                self._notificar("APARTADO REGISTRADO CON ÉXITO", es_error=False)
                self.cerrar_dialogo_apartado(self.dialogo_apartado)

            except Exception as ex:
                e.control.disabled = False
                e.control.text = "CONFIRMAR Y CREAR APARTADO"
                self._notificar(f"Error: {ex}", es_error=True)
                self.dialogo_apartado.update()

        self.dialogo_apartado = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.BOOKMARK_ADDED, size=50, color="#F6921E"),
                    ft.Text("RESUMEN DE APARTADO", size=24, weight="bold", color=self.COLOR_MARINO),
                    ft.Text(f"Total de la orden: ${self.total:.2f}", size=18, weight="bold", color="#27AE60"),
                    ft.Divider(),
                    dd_cliente,
                    ft.Row([txt_anticipo, txt_fecha], spacing=10, alignment="center"),
                    selector_pago,
                    ft.Divider(),
                    ft.ElevatedButton("CONFIRMAR Y CREAR APARTADO", on_click=confirmar, bgcolor="#F6921E", color="white", height=50, width=400),
                    ft.TextButton("CANCELAR", on_click=lambda _: self.cerrar_dialogo_apartado(self.dialogo_apartado))
                ], spacing=15, horizontal_alignment="center", tight=True),
                padding=30, width=480
            )
        )
        
        if hasattr(self.page, "open"):
            self.page.open(self.dialogo_apartado)
        else:
            if self.dialogo_apartado not in self.page.overlay:
                self.page.overlay.append(self.dialogo_apartado)
            self.dialogo_apartado.open = True
            self.page.update()

    def cerrar_dialogo_apartado(self, dialog):
        if hasattr(self.page, "close"):
            self.page.close(dialog)
        else:
            dialog.open = False
            self.page.update()

    def categoria_pill(self, texto):
        es_activo = self.categoria_actual == texto
        return ft.Container(
            content=ft.Text(texto, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if es_activo else self.COLOR_MARINO),
            bgcolor=self.COLOR_MARINO if es_activo else self.COLOR_GRIS_CLARO,
            padding=ft.Padding(left=20, top=10, right=20, bottom=10),
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
            content=ft.Column([
                # Parte superior: Imagen y Detalles
                ft.Row([
                    ft.Image(src="../assets/Concha.png", width=100, height=100, fit="cover", border_radius=5),
                    ft.Column([
                        ft.Text(nombre, weight="bold", color="white", size=20, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"${datos['precio']:.2f} c/u", color=ft.Colors.WHITE70, size=12),
                    ], expand=True, spacing=2),
                ]),
                # Parte inferior: Controles y Subtotal
                ft.Row([
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_color="white", icon_size=20, on_click=lambda _, name=nombre: self.modificar_cant(name, -1)),
                        ft.Text(str(datos["cantidad"]), weight="bold", color="white", size=14),
                        ft.IconButton(icon=ft.Icons.ADD_CIRCLE_OUTLINE, icon_color="white", icon_size=20, on_click=lambda _, name=nombre: self.modificar_cant(name, 1)),
                        ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_300, icon_size=20, on_click=lambda _, name=nombre: self.modificar_cant(name, -datos["cantidad"])),
                    ], spacing=0),
                    ft.Text(f"${sub:.2f}", weight="bold", color="white", size=14)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ], spacing=10),
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
            self.actualizar_header_visual()
        except: pass

    def actualizar_header_visual(self):
        try:
            session = get_session()
            nombre_cajero = session.current_user_name if session.current_user_name else session.current_user
            titulo = f"Punto de Venta - ({nombre_cajero})"
            bg_color = self.COLOR_MARINO
            
            if getattr(session, 'is_replica', False):
                if getattr(session, 'is_read_only', False):
                    titulo += " [SOLO LECTURA]"
                    bg_color = ft.Colors.RED_900
                else:
                    titulo += " [SERVIDOR DE RESPALDO]"
                    bg_color = ft.Colors.ORANGE_800
                    
            self.header_title_text.value = titulo
            self.header_title_box.bgcolor = bg_color
            self.header_title_box.update()
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
            self._notificar("Venta Exitosa", es_error=False)
        except Exception as ex:
            self._notificar(f"Error: {ex}", es_error=True)

    def build(self):
        session = get_session()
        
        # Usar el nombre guardado en la sesión para evitar consultar la tabla usuarios
        nombre_cajero = session.current_user_name if session.current_user_name else session.current_user

        self.txt_total = ft.Text("$0.00", size=24, weight="bold", color=self.COLOR_MARINO)
        self.renderizar_categorias()
        self.renderizar_productos()

        titulo = f"Punto de Venta - ({nombre_cajero})"
        bg_color = self.COLOR_MARINO
        
        if getattr(session, 'is_replica', False):
            if getattr(session, 'is_read_only', False):
                titulo += " [SOLO LECTURA]"
                bg_color = ft.Colors.RED_900
            else:
                titulo += " [SERVIDOR DE RESPALDO]"
                bg_color = ft.Colors.ORANGE_800

        self.header_title_text = ft.Text(titulo, color="white", weight=ft.FontWeight.BOLD)
        self.header_title_box = ft.Container(content=self.header_title_text, bgcolor=bg_color, padding=10, border_radius=5)

        header = ft.Container(
            content=ft.Row([
                self.header_title_box,
                ft.Row([
                    ft.ElevatedButton("Registrar Nuevo Cliente", on_click=self.mostrar_dialogo_cliente, expand=1, bgcolor=self.COLOR_ITEM_LISTA, color="white"),
                    ft.ElevatedButton("Liquidar Apartados", icon=ft.Icons.ATTACH_MONEY, on_click=lambda _: self.navegar("/gestionar_apartados"), bgcolor="#27AE60", color="white"),
                    ft.ElevatedButton("Cerrar Caja", icon=ft.Icons.OUTBOX, on_click=lambda _: self.navegar("/corte_caja"), bgcolor="red", color="white"),
                    self.btn_blanco("Cerrar Sesión", on_click=self._handle_salir),

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
                            ft.ElevatedButton("REALIZAR VENTA", icon=ft.Icons.CHECK, on_click=self.finalizar_venta, bgcolor="#27AE60", color="white", expand=True, height=50),
                            ft.ElevatedButton("REALIZAR APARTADO", icon=ft.Icons.BOOKMARK_ADD_SHARP, on_click=self.mostrar_dialogo_apartado, bgcolor="#F6921E", color="white", expand=True, height=50),
                        ], spacing=10),
                        
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