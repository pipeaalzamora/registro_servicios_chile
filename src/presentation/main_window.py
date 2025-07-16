"""
Ventana principal de la aplicación - Refactorizada con componentes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from ..domain.entities import CuentaServicio
from ..application.casos_uso import GestionarCuentaServicio, GenerarReportes, Notificaciones
from ..infrastructure.pdf_service import PDFService
from .components import CuentaTable, ButtonPanel, CuentaDialog


class MainWindow:
    """Ventana principal de la aplicación"""

    def __init__(self, gestionar_cuenta: GestionarCuentaServicio,
                 generar_reportes: GenerarReportes,
                 notificaciones: Notificaciones,
                 pdf_service: PDFService):
        self.gestionar_cuenta = gestionar_cuenta
        self.generar_reportes = generar_reportes
        self.notificaciones = notificaciones
        self.pdf_service = pdf_service

        self.root = tk.Tk()
        self.root.title("Registro de Servicios Chile")
        self.root.geometry("1400x700")
        self.root.configure(bg='#f0f0f0')

        self.setup_ui()
        self.cargar_cuentas()
        self.mostrar_notificaciones()

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Título
        title_label = ttk.Label(main_frame, text="Registro de Servicios Chile",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Panel de botones
        self.button_panel = ButtonPanel(
            parent=main_frame,
            gestionar_cuenta=self.gestionar_cuenta,
            generar_reportes=self.generar_reportes,
            pdf_service=self.pdf_service,
            on_nueva_cuenta=self.mostrar_dialogo_nueva_cuenta,
            on_editar_cuenta=self.editar_cuenta_seleccionada,
            on_marcar_pagada=self.marcar_como_pagada,
            on_eliminar_cuenta=self.eliminar_cuenta_seleccionada,
            on_mostrar_graficos=self.mostrar_graficos
        )
        self.button_panel.main_frame.grid(row=1, column=0, sticky="ew")

        # Tabla de cuentas
        self.cuenta_table = CuentaTable(
            parent=main_frame,
            gestionar_cuenta=self.gestionar_cuenta,
            on_cuenta_selected=self.editar_cuenta_seleccionada
        )
        self.cuenta_table.main_frame.grid(row=2, column=0, sticky="nsew")

    def cargar_cuentas(self):
        """Carga todas las cuentas en la tabla"""
        self.cuenta_table.cargar_cuentas()

    def mostrar_dialogo_nueva_cuenta(self):
        """Muestra el diálogo para crear una nueva cuenta"""
        dialog = CuentaDialog(self.root, self.gestionar_cuenta, self.cargar_cuentas)
        dialog.show()

    def editar_cuenta_seleccionada(self, event=None):
        """Edita la cuenta seleccionada"""
        cuenta = self.cuenta_table.obtener_cuenta_seleccionada()
        if cuenta:
            dialog = CuentaDialog(self.root, self.gestionar_cuenta, self.cargar_cuentas, cuenta)
            dialog.show()
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta para editar")

    def marcar_como_pagada(self):
        """Marca la cuenta seleccionada como pagada"""
        cuenta = self.cuenta_table.obtener_cuenta_seleccionada()
        if cuenta:
            if self.gestionar_cuenta.marcar_como_pagada(cuenta.id):
                messagebox.showinfo("Éxito", "Cuenta marcada como pagada")
                self.cargar_cuentas()
            else:
                messagebox.showerror("Error", "No se pudo marcar la cuenta como pagada")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta")

    def eliminar_cuenta_seleccionada(self):
        """Elimina la cuenta seleccionada"""
        cuenta = self.cuenta_table.obtener_cuenta_seleccionada()
        if cuenta:
            if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta cuenta?"):
                if self.gestionar_cuenta.eliminar_cuenta(cuenta.id):
                    messagebox.showinfo("Éxito", "Cuenta eliminada")
                    self.cargar_cuentas()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la cuenta")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta")

    def mostrar_notificaciones(self):
        """Muestra notificaciones de cuentas por vencer"""
        cuentas_por_vencer = self.notificaciones.obtener_cuentas_por_vencer(7)
        cuentas_vencidas_hoy = self.notificaciones.obtener_cuentas_vencidas_hoy()
        cuentas_riesgo = [c for c in self.gestionar_cuenta.obtener_todas_las_cuentas() if c.esta_en_riesgo_corte()]

        if cuentas_por_vencer or cuentas_vencidas_hoy or cuentas_riesgo:
            mensaje = ""
            if cuentas_vencidas_hoy:
                mensaje += f"⚠️ {len(cuentas_vencidas_hoy)} cuenta(s) vencen hoy\n"
            if cuentas_riesgo:
                mensaje += f"🚨 {len(cuentas_riesgo)} cuenta(s) en riesgo de corte\n"
            if cuentas_por_vencer:
                mensaje += f"📅 {len(cuentas_por_vencer)} cuenta(s) vencen en los próximos 7 días"

            if mensaje:
                messagebox.showwarning("Notificaciones", mensaje)

    def mostrar_graficos(self):
        """Muestra la ventana de gráficos"""
        from .components import GraficosPanel
        graficos_window = tk.Toplevel(self.root)
        graficos_window.title("Gráficos y Estadísticas")
        graficos_window.geometry("800x600")

        graficos_panel = GraficosPanel(graficos_window, self.gestionar_cuenta)
        graficos_panel.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()