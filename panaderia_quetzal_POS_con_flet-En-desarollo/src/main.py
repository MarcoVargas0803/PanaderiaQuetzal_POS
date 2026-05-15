import flet as ft
class App:
    def __init__(self, page: ft.Page):
        self.page = page

        # Configurar la página
        self.page.title = "Punto de Venta - Panadería Quetzal"
        self.page.window_width = 1000
        self.page.window_height = 700
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0

        # Configurar eventos
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

        # Iniciar en /
        self.page.route = "/"
        self.route_change(None)

    def navegar(self, ruta):
        self.page.route = ruta
        self.route_change(None)
        self.page.update()

    def route_change(self, e):
        try:
            from session_state import get_session
            session = get_session()
            self.page.views.clear()

            # Si regresamos al inicio, reseteamos la sesión
            if self.page.route == "/":
                session.reset()
                from views.inicio import InicioView
                self.page.views.append(InicioView(self.navegar, self.page).build())
            elif self.page.route == "/login":
                from views.login import LoginView
                self.page.views.append(LoginView(self.navegar, self.page).build())
            elif self.page.route == "/register":
                from views.registro import RegistroView
                self.page.views.append(RegistroView(self.navegar, self.page).build())
            elif self.page.route == "/ventana_principal":
                from views.ventana_principal import PrincipalView
                self.page.views.append(PrincipalView(self.navegar, self.page).build())
            elif self.page.route == "/abrir_caja":
                from views.abrir_caja import AbrirCajaView
                self.page.views.append(AbrirCajaView(self.navegar, self.page).build())
            elif self.page.route == "/consulta_ventas":
                from views.consulta_ventas import ConsultaVentasView
                self.page.views.append(ConsultaVentasView(self.navegar, self.page).build())
            elif self.page.route == "/ventana_principal_produccion":
                from views.ventana_principal_produccion import PrincipalProduccionView
                self.page.views.append(PrincipalProduccionView(self.navegar, self.page).build())
            elif self.page.route == "/registrar_cliente":
                from views.registrar_cliente import RegistrarClienteView
                self.page.views.append(RegistrarClienteView(self.navegar, self.page).build())
            elif self.page.route == "/registrar_apartado":
                from views.registrar_apartado import RegistrarApartadoView
                self.page.views.append(RegistrarApartadoView(self.navegar, self.page).build())
            elif self.page.route == "/corte_caja":
                from views.corte_caja import CorteCajaView
                self.page.views.append(CorteCajaView(self.navegar, self.page).build())
            elif self.page.route == "/consulta_auditoria":
                from views.consulta_auditoria import ConsultaAuditoriaView
                self.page.views.append(ConsultaAuditoriaView(self.navegar, self.page).build())
            elif self.page.route == "/ventana_principal_consultas":
                from views.ventana_principal_consultas import PrincipalConsultasView
                self.page.views.append(PrincipalConsultasView(self.navegar, self.page).build())
            elif self.page.route == "/crud_catalogos":
                from views.crud_catalogos import CrudCatalogosView
                self.page.views.append(CrudCatalogosView(self.navegar, self.page).build())
            elif self.page.route == "/gestionar_apartados":
                from views.gestionar_apartados import GestionarApartadosView
                self.page.views.append(GestionarApartadosView(self.navegar, self.page).build())
            
            self.page.update()
        except Exception as ex:
            print(f"!!! CRITICAL ERROR !!!: {ex}")
            import traceback
            traceback.print_exc()
            error_view = ft.View(
                route="/error",
                controls=[
                    ft.AppBar(title=ft.Text("Error de Carga"), bgcolor="red"),
                    ft.Text(f"Se produjo un error al cargar la aplicación:\n{ex}", size=20, color="red"),
                    ft.Text("Revisa la consola para más detalles.", size=14)
                ]
            )
            self.page.views.append(error_view)
            self.page.update()


    def view_pop(self, view):
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.navegar(top_view.route)

def main(page: ft.Page):
    app = App(page)

if __name__ == '__main__':
    ft.run(main)