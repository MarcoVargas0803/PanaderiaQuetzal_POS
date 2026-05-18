import flet as ft
from Backend.dao_panaderia import obtener_catalogo, insertar_catalogo, actualizar_catalogo, eliminar_catalogo
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from session_state import get_session
from components.Toasts import NotificationHelper


class CrudCatalogosView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"
        self.tabla_actual = "productos"

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)
        
        # Mapeo de tablas y sus claves primarias
        self.config_tablas = {
            "productos": {"pk": "productos_id", "columnas": ["nombre", "precio", "stock", "tiempo_vida", "temporadas_id", "categorias_id"]},
            "usuarios": {"pk": "usuarios_id", "columnas": ["nombre", "codigo", "rol_id"]},
            "clientes": {"pk": "clientes_id", "columnas": ["nombre", "telefono"]},
            "categorias_productos": {"pk": "categorias_id", "columnas": ["descripcion"]}
        }
        
        self.datos = []

    def cargar_datos(self):
        try:
            self.datos = obtener_catalogo(self.tabla_actual)
            self.actualizar_tabla()
        except Exception as ex:
            self._notificar(f"Error cargando datos:", es_error=True)

    def cambiar_tabla(self, e):
        self.tabla_actual = self.selector_tabla.value
        self.cargar_datos()

    def mostrar_dialogo_edicion(self, registro=None):
        es_nuevo = registro is None
        titulo = f"{'Añadir' if es_nuevo else 'Editar'} en {self.tabla_actual}"
        
        campos = {}
        columnas = self.config_tablas[self.tabla_actual]["columnas"]
        
        for col in columnas:
            valor = str(registro.get(col, "")) if not es_nuevo else ""
            campos[col] = ft.TextField(label=col.replace('_', ' ').title(), value=valor, width=300)

        def guardar(e):
            datos_guardar = {}
            for col, tf in campos.items():
                if tf.value.strip() == "":
                    self._notificar(f"El campo {col} es obligatorio", es_error=True)
                    return
                # Intentar convertir numéricos
                val = tf.value.strip()
                if val.replace('.','',1).isdigit():
                    val = float(val) if '.' in val else int(val)
                datos_guardar[col] = val

            try:
                pk_col = self.config_tablas[self.tabla_actual]["pk"]
                if es_nuevo:
                    insertar_catalogo(self.tabla_actual, datos_guardar)
                    msg = "Registro creado con éxito"
                else:
                    actualizar_catalogo(self.tabla_actual, pk_col, registro[pk_col], datos_guardar)
                    msg = "Registro actualizado con éxito"
                
                self.cerrar_dialogo()
                self._notificar(msg, es_error=False)
                self.cargar_datos()
            except Exception as ex:
                self._notificar(f"Error BD: {ex}", es_error=True)
            self.page.update()

        self.dialogo = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Column(list(campos.values()), tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Guardar", on_click=guardar, bgcolor=self.COLOR_MARINO, color="white")
            ]
        )
        if hasattr(self.page, "open"):
            self.page.open(self.dialogo)
        else:
            if self.dialogo not in self.page.overlay:
                self.page.overlay.append(self.dialogo)
            self.dialogo.open = True
            self.page.update()

    def mostrar_dialogo_eliminar(self, registro):
        pk_col = self.config_tablas[self.tabla_actual]["pk"]
        id_valor = registro[pk_col]
        
        def confirmar(e):
            try:
                eliminar_catalogo(self.tabla_actual, pk_col, id_valor)
                self.cerrar_dialogo()
                self._notificar("Registro eliminado", es_error=False)
                self.cargar_datos()
            except Exception as ex:
                #Falta implementación de mensaje personalizado para "ex" en la BD. 
                self._notificar(f"Error al eliminar (puede tener dependencias)", es_error=True)
            self.page.update()

        self.dialogo = ft.AlertDialog(
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(f"¿Deseas eliminar el registro con ID {id_valor} de {self.tabla_actual}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.cerrar_dialogo()),
                ft.ElevatedButton("Eliminar", on_click=confirmar, bgcolor="red", color="white")
            ]
        )
        if hasattr(self.page, "open"):
            self.page.open(self.dialogo)
        else:
            if self.dialogo not in self.page.overlay:
                self.page.overlay.append(self.dialogo)
            self.dialogo.open = True
            self.page.update()

    def cerrar_dialogo(self):
        if hasattr(self.page, "close"):
            self.page.close(self.dialogo)
        else:
            self.dialogo.open = False
            self.page.update()

    def actualizar_tabla(self):
        if not self.datos:
            self.cabecera_tabla.content.controls = [ft.Container(content=ft.Text("Sin Datos", weight="bold", color=self.COLOR_MARINO), expand=1)]
            self.lista_registros.controls = []
            self.page.update()
            return

        pk_col = self.config_tablas[self.tabla_actual]["pk"]
        columnas = [pk_col] + self.config_tablas[self.tabla_actual]["columnas"]
        
        # Cabecera responsiva
        cabeceras_ui = []
        for c in columnas:
            cabeceras_ui.append(ft.Container(content=ft.Text(c.replace('_', ' ').title(), weight="bold", color=self.COLOR_MARINO), expand=1))
        cabeceras_ui.append(ft.Container(content=ft.Text("Acciones", weight="bold", color=self.COLOR_MARINO), expand=1))
        
        self.cabecera_tabla.content.controls = cabeceras_ui
        
        filas = []
        for reg in self.datos:
            celdas_ui = []
            for c in columnas:
                celdas_ui.append(ft.Container(content=ft.Text(str(reg.get(c, ""))), expand=1))
            
            def create_edit(r): return lambda e: self.mostrar_dialogo_edicion(r)
            def create_delete(r): return lambda e: self.mostrar_dialogo_eliminar(r)
            
            btn_editar = ft.IconButton(icon=ft.Icons.EDIT, icon_color="blue", tooltip="Editar", on_click=create_edit(reg))
            btn_eliminar = ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", tooltip="Eliminar", on_click=create_delete(reg))
            
            celdas_ui.append(ft.Container(content=ft.Row([btn_editar, btn_eliminar], alignment=ft.MainAxisAlignment.START), expand=1))
            
            filas.append(
                ft.Container(
                    content=ft.Row(celdas_ui, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding(top=10, bottom=10, left=5, right=5),
                    border=ft.Border(bottom=ft.BorderSide(1, "#EEEEEE"))
                )
            )
            
        self.lista_registros.controls = filas
        if self.page:
            self.page.update()

    def build(self):
        self.cabecera_tabla = ft.Container(content=ft.Row([]), bgcolor="#F4F6F7", padding=ft.Padding(15, 15, 5, 5), border_radius=5)
        self.lista_registros = ft.Column([], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        
        header = ft.Container(
            content=ft.Row([
                ft.Text("GESTIÓN DE CATÁLOGOS", size=22, weight="bold", color=self.COLOR_MARINO),
                ft.ElevatedButton("Volver al Panel", icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.navegar("/ventana_principal_consultas"))
            ], alignment="spaceBetween"),
            padding=15, border=ft.Border.only(bottom=ft.BorderSide(1, "#DDDDDD"))
        )

        self.selector_tabla = ft.Dropdown(
            label="Selecciona la tabla a gestionar",
            options=[
                ft.dropdown.Option("productos"),
                ft.dropdown.Option("usuarios"),
                ft.dropdown.Option("clientes"),
                ft.dropdown.Option("categorias_productos")
            ],
            value=self.tabla_actual,
            width=300
        )

        # Cargar datos iniciales
        self.cargar_datos()

        return ft.View(
            route="/crud_catalogos",
            bgcolor="white",
            padding=0,
            controls=[
                header,
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            self.selector_tabla, 
                            ft.ElevatedButton("Cargar Datos", on_click=self.cambiar_tabla, bgcolor=self.COLOR_MARINO, color="white"), 
                            ft.ElevatedButton("Nuevo Registro", icon=ft.Icons.ADD, bgcolor="green", color="white", on_click=lambda e: self.mostrar_dialogo_edicion(None))
                        ]),
                        ft.Divider(),
                        ft.Container(
                            content=ft.Column([
                                self.cabecera_tabla,
                                self.lista_registros
                            ], expand=True),
                            expand=True,
                            border=ft.Border.all(1, "#DDDDDD"),
                            border_radius=5
                        )
                    ]),
                    padding=20, expand=True
                )
            ]
        )
