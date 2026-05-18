import flet as ft
import asyncio


class NotificationHelper:
    """Clase global para manejar Toasts y avisos en la interfaz."""

    @staticmethod
    async def mostrar_toast(page: ft.Page, mensaje: str, es_error: bool = False):
        # 1. Configuración de estilo (Usa tus constantes de marca si prefieres)
        color_fondo = ft.Colors.RED_400 if es_error else "#2ECC71" # Verde de tu paleta
        icono = ft.Icons.ERROR_OUTLINE if es_error else ft.Icons.CHECK_CIRCLE_OUTLINE

        # 2. Construcción del componente (El "Toast")
        toast = ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=ft.Colors.WHITE, size=20),
                ft.Text(mensaje, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            ], tight=True),
            bgcolor=color_fondo,
            border_radius=10,
            padding=ft.Padding(20, 10, 20, 10),
            opacity=0,
            animate_opacity=300,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK26),
            # Constraints de posición
            top=20,
            right=20,
        )

        # 3. Inserción en la capa superior (Overlay)
        page.overlay.append(toast)
        page.update()

        # 4. Secuencia de animación (Aparece -> Espera -> Se va)
        await asyncio.sleep(0.1)
        toast.opacity = 1
        page.update()

        await asyncio.sleep(2) # Duración del mensaje

        toast.opacity = 0
        page.update()

        await asyncio.sleep(0.3) # Tiempo para que termine la animación
        if toast in page.overlay:
            page.overlay.remove(toast)
        page.update()