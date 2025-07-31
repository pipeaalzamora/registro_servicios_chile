"""
Sistema de notificaciones para la aplicación
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import List, Callable
import threading
import time

from models import CuentaServicio
from config import NOTIFICATIONS_CONFIG


class NotificationManager:
    """Gestor de notificaciones"""

    def __init__(self, db_manager, parent_window):
        self.db_manager = db_manager
        self.parent_window = parent_window
        self.config = NOTIFICATIONS_CONFIG
        self.running = False
        self.thread = None
        self.callbacks = []

    def add_callback(self, callback: Callable):
        """Agrega callback para cuando hay notificaciones"""
        self.callbacks.append(callback)

    def start(self):
        """Inicia el sistema de notificaciones"""
        if not self.config['enabled'] or self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._notification_loop, daemon=True)
        self.thread.start()
        print("✅ Sistema de notificaciones iniciado")

    def stop(self):
        """Detiene el sistema de notificaciones"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("🔴 Sistema de notificaciones detenido")

    def _notification_loop(self):
        """Loop principal de notificaciones"""
        while self.running:
            try:
                self._check_notifications()
                time.sleep(self.config['check_interval'])
            except Exception as e:
                print(f"Error en notificaciones: {e}")
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

    def _check_notifications(self):
        """Verifica y envía notificaciones"""
        try:
            # Obtener cuentas pendientes
            cuentas_pendientes = self.db_manager.obtener_cuentas_pendientes()

            notifications = []

            for cuenta in cuentas_pendientes:
                dias_vencer = cuenta.dias_para_vencer()

                # Notificación de vencimiento próximo
                if dias_vencer <= self.config['days_before_due'] and dias_vencer > 0:
                    notifications.append({
                        'type': 'warning',
                        'title': 'Cuenta por vencer',
                        'message': f"{cuenta.descripcion} vence en {dias_vencer} día(s)",
                        'cuenta': cuenta
                    })

                # Notificación de cuenta vencida
                elif dias_vencer <= 0:
                    notifications.append({
                        'type': 'error',
                        'title': 'Cuenta vencida',
                        'message': f"{cuenta.descripcion} está vencida",
                        'cuenta': cuenta
                    })

                # Notificación de riesgo de corte
                if cuenta.esta_en_riesgo_corte():
                    notifications.append({
                        'type': 'critical',
                        'title': 'Riesgo de corte',
                        'message': f"{cuenta.descripcion} en riesgo de corte",
                        'cuenta': cuenta
                    })

            # Enviar notificaciones si hay alguna
            if notifications:
                self._send_notifications(notifications)

        except Exception as e:
            print(f"Error verificando notificaciones: {e}")

    def _send_notifications(self, notifications: List[dict]):
        """Envía las notificaciones"""
        # Notificar a callbacks registrados
        for callback in self.callbacks:
            try:
                callback(notifications)
            except Exception as e:
                print(f"Error en callback de notificación: {e}")

        # Mostrar notificaciones de escritorio si está habilitado
        if self.config['desktop_notifications']:
            self._show_desktop_notifications(notifications)

    def _show_desktop_notifications(self, notifications: List[dict]):
        """Muestra notificaciones de escritorio"""
        try:
            # Usar el thread principal para mostrar notificaciones
            self.parent_window.after(0, lambda: self._show_notification_popup(notifications))
        except Exception as e:
            print(f"Error mostrando notificaciones de escritorio: {e}")

    def _show_notification_popup(self, notifications: List[dict]):
        """Muestra popup de notificaciones"""
        if not notifications:
            return

        # Crear ventana de notificación
        popup = NotificationPopup(self.parent_window, notifications)
        popup.show()


class NotificationPopup:
    """Popup de notificaciones"""

    def __init__(self, parent, notifications: List[dict]):
        self.parent = parent
        self.notifications = notifications
        self.popup = None

    def show(self):
        """Muestra el popup"""
        if self.popup:
            return

        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Notificaciones")
        self.popup.geometry("400x300")
        self.popup.transient(self.parent)

        # Posicionar en esquina superior derecha
        x = self.parent.winfo_x() + self.parent.winfo_width() - 420
        y = self.parent.winfo_y() + 50
        self.popup.geometry(f"+{x}+{y}")

        # Configurar ventana
        self.popup.resizable(False, False)
        self.popup.attributes('-topmost', True)

        self._create_widgets()

        # Auto-cerrar después de 10 segundos
        self.popup.after(10000, self.close)

    def _create_widgets(self):
        """Crea los widgets del popup"""
        # Frame principal
        main_frame = ttk.Frame(self.popup, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(main_frame, text="🔔 Notificaciones",
                               font=('Arial', 12, 'bold'))
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # Frame con scroll para notificaciones
        canvas = tk.Canvas(main_frame, height=200)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Agregar notificaciones
        for i, notification in enumerate(self.notifications):
            self._create_notification_item(scrollable_frame, notification, i)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cerrar",
                  command=self.close).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Ver Cuentas",
                  command=self._show_accounts).pack(side=tk.RIGHT, padx=(0, 5))

    def _create_notification_item(self, parent, notification: dict, index: int):
        """Crea un item de notificación"""
        # Frame para la notificación
        item_frame = ttk.LabelFrame(parent, text="", padding=5)
        item_frame.pack(fill=tk.X, pady=2)

        # Icono según tipo
        icons = {
            'warning': '⚠️',
            'error': '❌',
            'critical': '🚨',
            'info': 'ℹ️'
        }
        icon = icons.get(notification['type'], 'ℹ️')

        # Título con icono
        title_label = ttk.Label(item_frame,
                               text=f"{icon} {notification['title']}",
                               font=('Arial', 9, 'bold'))
        title_label.pack(anchor=tk.W)

        # Mensaje
        message_label = ttk.Label(item_frame,
                                 text=notification['message'],
                                 font=('Arial', 8))
        message_label.pack(anchor=tk.W, padx=(20, 0))

        # Información adicional si hay cuenta
        if 'cuenta' in notification:
            cuenta = notification['cuenta']
            info_text = f"Monto: ${cuenta.monto:,.0f} - Vence: {cuenta.fecha_vencimiento.strftime('%d/%m/%Y')}"
            info_label = ttk.Label(item_frame,
                                  text=info_text,
                                  font=('Arial', 7),
                                  foreground='gray')
            info_label.pack(anchor=tk.W, padx=(20, 0))

    def _show_accounts(self):
        """Muestra las cuentas relacionadas"""
        # Cerrar popup y enfocar ventana principal
        self.close()
        self.parent.focus_force()
        self.parent.lift()

    def close(self):
        """Cierra el popup"""
        if self.popup:
            self.popup.destroy()
            self.popup = None


class NotificationIndicator(ttk.Frame):
    """Indicador de notificaciones en la barra de estado"""

    def __init__(self, parent):
        super().__init__(parent)
        self.notification_count = 0
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del indicador"""
        self.icon_label = ttk.Label(self, text="🔔", font=('Arial', 10))
        self.icon_label.pack(side=tk.LEFT)

        self.count_label = ttk.Label(self, text="0", font=('Arial', 8, 'bold'))
        self.count_label.pack(side=tk.LEFT, padx=(2, 0))

        # Tooltip
        self._create_tooltip()

    def update_count(self, count: int):
        """Actualiza el contador de notificaciones"""
        self.notification_count = count
        self.count_label.config(text=str(count))

        # Cambiar color según cantidad
        if count == 0:
            self.icon_label.config(foreground='gray')
            self.count_label.config(foreground='gray')
        elif count <= 3:
            self.icon_label.config(foreground='orange')
            self.count_label.config(foreground='orange')
        else:
            self.icon_label.config(foreground='red')
            self.count_label.config(foreground='red')

    def _create_tooltip(self):
        """Crea tooltip para el indicador"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            text = f"Notificaciones activas: {self.notification_count}"
            label = ttk.Label(tooltip, text=text, background="lightyellow",
                             relief="solid", borderwidth=1, padding=5)
            label.pack()

            # Auto-destruir después de 2 segundos
            tooltip.after(2000, tooltip.destroy)

        self.icon_label.bind("<Enter>", show_tooltip)
        self.count_label.bind("<Enter>", show_tooltip)