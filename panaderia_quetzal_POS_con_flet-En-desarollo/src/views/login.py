import flet as ft
from session_state import get_session

class LoginView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    def intentar_login(self, e):
        pin = self.txt_pin.value.strip() if self.txt_pin.value else ""
        if not pin:
            e.page.snack_bar = ft.SnackBar(ft.Text("El código de empleado está vacío"), bgcolor=ft.Colors.RED)
            e.page.snack_bar.open = True
            e.page.update()
            return
        
        session = get_session()
        import mysql.connector

        try:
            # Conexión maestra silenciosa para buscar el empleado por código
            conn = mysql.connector.connect(
                host="localhost",
                user="admin_quetzal",
                password="Admin@Quetzal2026",
                database="panaderia"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT usuarios_id, rol_id, nombre FROM usuarios WHERE codigo = %s", (pin,))
            usr = cursor.fetchone()
            conn.close()

            if not usr:
                e.page.snack_bar = ft.SnackBar(ft.Text("Código inválido, empleado no encontrado."), bgcolor=ft.Colors.RED)
                e.page.snack_bar.open = True
                e.page.update()
                return
                
            session.current_user_id = int(usr['usuarios_id'])
            r_id = int(usr['rol_id'])
            nombre = usr['nombre']
            
            # --- DETECCIÓN DE CAJA CON PRIVILEGIOS DE ADMIN (VERDAD ABSOLUTA) ---
            # Usamos la misma conexión de arriba que ya es admin
            conn = mysql.connector.connect(
                host="localhost", user="admin_quetzal", password="Admin@Quetzal2026", database="panaderia"
            )
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT cajas_id FROM cajas WHERE usuarios_id = %s AND fecha_cierre IS NULL LIMIT 1", (session.current_user_id,))
            activa = cursor.fetchone()
            conn.close()

            # Asignar credenciales de BD según el rol
            # Guardar ruta a navegar
            ruta_destino = None
            if r_id == 1:
                session.current_user = "admin_quetzal"
                session.current_password = "Admin@Quetzal2026"
                session.current_role = "admin"
                ruta_destino = "/ventana_principal_consultas"
            elif r_id == 2:
                session.current_user = "cajero_quetzal"
                session.current_password = "Cajero@Quetzal2026"
                session.current_role = "cajero"
                if activa:
                    session.current_caja_id = int(activa['cajas_id'])
                    ruta_destino = "/ventana_principal"
                else:
                    ruta_destino = "/abrir_caja"
            elif r_id == 3:
                session.current_user = "panadero_quetzal"
                session.current_password = "Panadero@Quetzal2026"
                session.current_role = "panadero"
                ruta_destino = "/ventana_principal_produccion"

            # Mostrar mensaje ANTES de navegar
            page = e.page
            page.snack_bar = ft.SnackBar(ft.Text(f"Bienvenido/a {nombre}"), bgcolor=ft.Colors.GREEN)
            page.snack_bar.open = True
            page.update()
            
            # Navegar al final
            if ruta_destino:
                self.navegar(ruta_destino)

        except Exception as ex:
            print(f"ERROR LOGIN: {ex}")
            # Intentar mostrar error si la página aún existe
            try:
                e.page.snack_bar = ft.SnackBar(ft.Text(f"Fallo: {ex}"), bgcolor=ft.Colors.RED)
                e.page.snack_bar.open = True
                e.page.update()
            except: pass

    def build(self):
        self.txt_pin = ft.TextField(
            hint_text="Código de Empleado (Ej: cajera456)",
            border_color=self.COLOR_MARINO,
            width=400,
            password=True,
            can_reveal_password=True,
            on_submit=self.intentar_login
        )
        
        return ft.View(
            route="/login",
            controls=[
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text("Inicio de Sesión", color="white", weight=ft.FontWeight.BOLD),
                            bgcolor=self.COLOR_MARINO, padding=10, border_radius=5
                        ),
                        ft.Button("Retroceder >", on_click=lambda _: self.navegar("/"), style=ft.ButtonStyle(bgcolor=self.COLOR_MARINO, color="white"))
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=20,
                    border=ft.Border.only(bottom=ft.BorderSide(2, self.COLOR_MARINO))
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Panel de Autenticación", size=24, weight=ft.FontWeight.BOLD, color=self.COLOR_MARINO),
                        ft.Text("Código de Empleado", weight=ft.FontWeight.BOLD, size=16, color=self.COLOR_MARINO),
                        self.txt_pin,
                        ft.Container(height=20),
                        ft.Button(
                            "Iniciar Sesión",
                            on_click=self.intentar_login,
                            width=220, height=45,
                            style=ft.ButtonStyle(bgcolor=self.COLOR_MARINO, color="white")
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.Alignment(0, 0)
                )
            ],
            bgcolor="white"
        )