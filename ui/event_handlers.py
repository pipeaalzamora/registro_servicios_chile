"""
Manejadores de eventos para la interfaz de usuario
"""

import tkinter as tk
from tkinter import messagebox
from typing import List, Optional
from models import CuentaServicio


class EventHandlers:
    """Maneja todos los eventos de la interfaz de usuario"""

    def __init__(self, main_window):
        self.main_window = main_window

    def setup_keyboard_shortcuts(self):
        """Configura atajos de teclado"""
        from config import UI_CONFIG

        if not UI_CONFIG.get('enable_keyboard_shortcuts', True):
            return

        root = self.main_window.root

        # Atajos principales
        root.bind('<Control-n>', lambda e: self.main_window.crud_operations.nueva_cuenta())
        root.bind('<Control-e>', lambda e: self.main_window.crud_operations.editar_cuenta())
        root.bind('<Control-d>', lambda e: self.main_window.crud_operations.eliminar_cuenta())
        root.bind('<Control-p>', lambda e: self.main_window.crud_operations.marcar_pagado())
        root.bind('<F5>', lambda e: self.main_window._refresh_data())
        root.bind('<Control-r>', lambda e: self.main_window._generar_reporte_mensual())
        root.bind('<Escape>', lambda e: self.main_window._clear_selection())

    def on_search_change(self, search_text: str):
        """Maneja cambios en la búsqueda"""
        self.main_window.filtro_actual = search_text
        self.main_window._update_table()

    def on_filter_change(self, event=None):
        """Maneja cambios en los filtros"""
        self.main_window._update_table()

    def on_double_click(self, event):
        """Maneja doble click en la tabla"""
        self.main_window.crud_operations.editar_cuenta()

    def on_table_double_click(self, cuenta: CuentaServicio):
        """Maneja doble click en tabla mejorada"""
        self.main_window.selected_cuenta = cuenta
        self.main_window.crud_operations.editar_cuenta()

    def on_table_right_click(self, event, cuenta: CuentaServicio):
        """Maneja click derecho en tabla mejorada"""
        self.main_window.selected_cuenta = cuenta
        self.show_context_menu(event)

    def show_context_menu(self, event):
        """Muestra menú contextual mejorado"""
        if not self.main_window.selected_cuenta:
            return

        # Crear menú contextual
        context_menu = tk.Menu(self.main_window.root, tearoff=0)

        # Opciones del menú
        context_menu.add_command(label="✏️ Editar", command=self.main_window.crud_operations.editar_cuenta)
        context_menu.add_command(label="✅ Marcar Pagado", command=self.main_window.crud_operations.marcar_pagado)
        context_menu.add_separator()
        context_menu.add_command(label="📄 Ver Detalles", command=self.main_window.crud_operations.ver_detalles)
        context_menu.add_separator()
        context_menu.add_command(label="📊 Generar Reporte Individual",
                               command=self.main_window._generar_reporte_individual)
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Eliminar", command=self.main_window.crud_operations.eliminar_cuenta)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def on_notifications_received(self, notifications: List[dict]):
        """Maneja notificaciones recibidas"""
        if hasattr(self.main_window, 'notification_indicator'):
            self.main_window.notification_indicator.update_notifications(notifications)

        # Actualizar barra de estado con notificaciones críticas
        critical_count = sum(1 for n in notifications if n.get('type') == 'critical')
        if critical_count > 0:
            self.main_window._update_status(f"⚠️ {critical_count} cuenta(s) en riesgo de corte")

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        # Detener notificaciones
        if hasattr(self.main_window, 'notification_manager') and self.main_window.notification_manager:
            self.main_window.notification_manager.stop()

        # Cerrar base de datos
        self.main_window.db_manager.close()
        self.main_window.root.destroy()

    def show_graphics_window(self):
        """Muestra la ventana de gráficos interactivos"""
        try:
            if not self.main_window.graphics_window:
                from .graphics_window import GraphicsWindow
                self.main_window.graphics_window = GraphicsWindow(self.main_window.root, self.main_window.cuentas_actuales)
            else:
                self.main_window.graphics_window.update_data(self.main_window.cuentas_actuales)
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo ventana de gráficos: {e}")

    def get_selected_cuenta(self) -> Optional[CuentaServicio]:
        """Obtiene la cuenta seleccionada"""
        selection = self.main_window.tree.selection()
        if not selection:
            return None

        item = selection[0]
        return self.get_cuenta_from_item(item)

    def get_selected_cuentas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas seleccionadas"""
        selection = self.main_window.tree.selection()
        if not selection:
            return []

        cuentas = []
        for item in selection:
            cuenta = self.get_cuenta_from_item(item)
            if cuenta:
                cuentas.append(cuenta)

        return cuentas

    def get_cuenta_from_item(self, item) -> Optional[CuentaServicio]:
        """Obtiene una cuenta desde un item del tree"""
        values = self.main_window.tree.item(item, 'values')
        if not values:
            return None

        try:
            # Usar descripción y monto como identificadores únicos más robustos
            descripcion_mostrada = values[1]  # Columna descripción
            monto_mostrado = values[2]        # Columna monto

            # Limpiar descripción truncada
            descripcion_limpia = descripcion_mostrada.replace("...", "").strip()

            # Limpiar formato de monto
            monto_limpio = monto_mostrado.replace("$", "").replace(".", "").replace(",", "")
            monto_valor = float(monto_limpio) if monto_limpio else 0

            # Buscar la cuenta que coincida
            for cuenta in self.main_window.cuentas_actuales:
                if (cuenta.descripcion.startswith(descripcion_limpia) or
                    descripcion_limpia in cuenta.descripcion) and cuenta.monto == monto_valor:
                    return cuenta

        except (ValueError, IndexError, AttributeError) as e:
            print(f"Error obteniendo cuenta del item: {e}")

            # Fallback: usar índice si falla la búsqueda por contenido
            try:
                all_items = self.main_window.tree.get_children()
                item_index = list(all_items).index(item)
                if 0 <= item_index < len(self.main_window.cuentas_actuales):
                    return self.main_window.cuentas_actuales[item_index]
            except (ValueError, IndexError):
                pass

        return None