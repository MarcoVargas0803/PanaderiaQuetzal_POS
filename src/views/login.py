import flet as ft
from session_state import get_session
import os
from pathlib import Path
from dotenv import load_dotenv
from components.Toasts import NotificationHelper

# Asegurar que el .env se cargue robustamente también aquí
# (parent.parent.parent porque estamos en src/views/login.py)
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class LoginView:
    def __init__(self, navegar_callback, page_reference):
        self.navegar = navegar_callback
        self.page = page_reference
        self.COLOR_MARINO = "#2C3545"

    def _notificar(self, mensaje, es_error=False):
        self.page.run_task(NotificationHelper.mostrar_toast, self.page, mensaje, es_error)

    def _handle_inciar_sesion(self, e):
        self.intentar_login(e)

    def intentar_login(self, e):
        pin = self.txt_pin.value.strip() if self.txt_pin.value else ""
        if not pin:
            self._notificar("El código de empleado está vacío", es_error=True)
            return
        
        session = get_session()
        from database import create_raw_connection

        try:
            # Intento de conexión con Failover y verificación de read_only (Maestro -> Esclavo)
            conn, is_replica, is_ro = create_raw_connection("admin_quetzal", "Admin@Quetzal2026")

            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT usuarios_id, rol_id, nombre FROM usuarios WHERE codigo = %s", (pin,))
            usr = cursor.fetchone()
            conn.close()

            if not usr:
                self._notificar("Código inválido, empleado no encontrado.", es_error=True)
                return
                
            session.current_user_id = int(usr['usuarios_id'])
            session.current_user_name = usr['nombre']
            r_id = int(usr['rol_id'])
            nombre = usr['nombre']
            
            # Reutilizamos la lógica para detectar la caja
            conn2, _, _ = create_raw_connection("admin_quetzal", "Admin@Quetzal2026")

            cursor2 = conn2.cursor(dictionary=True)
            cursor2.execute("SELECT cajas_id FROM cajas WHERE usuarios_id = %s AND fecha_cierre IS NULL LIMIT 1", (session.current_user_id,))
            activa = cursor2.fetchone()
            conn2.close()

            # Registrar el estado en la sesión
            session.is_read_only = is_ro
            session.is_replica = is_replica

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

            # Notificaciones de read_only y bienvenida
            if is_replica:
                if is_ro:
                    self._notificar(f"Bienvenido/a {nombre}. ⚠️ MODO SOLO LECTURA: No podrá guardar datos.", es_error=True)
                else:
                    self._notificar(f"Bienvenido/a {nombre}. Conectado a respaldo (escritura).", es_error=False)
            else:
                self._notificar(f"Bienvenido/a {nombre}", es_error=False)
            # Navegar al final
            if ruta_destino:
                self.navegar(ruta_destino)

        except Exception as ex:
            print(f"ERROR LOGIN: {ex}")
            # Intentar mostrar error si la página aún existe
            try:
                self._notificar(f"Fallo: {ex}", es_error=True)
            except: pass

    def build(self):
        self.txt_pin = ft.TextField(
            hint_text="Ingrese su código de acceso",
            border_color=self.COLOR_MARINO,
            width=400,
            password=True,
            can_reveal_password=True,
            on_submit=self._handle_inciar_sesion
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
                            on_click=self._handle_inciar_sesion,
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