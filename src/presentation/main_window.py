"""
Ventana principal de la aplicación - Refactorizada con componentes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

from ..domain.entities import CuentaServicio
from ..application.casos_uso import GestionarCuentaServicio, GenerarReportes, Notificaciones
from ..infrastructure.pdf_service import PDFService
from .components import CuentaTable, ButtonPanel, CuentaDialog
from .themes import theme_manager
from .utils import error_handler, handle_ui_errors


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
        self.root.geometry("1400x800")

        # Configurar ventana responsive
        self.root.minsize(1000, 600)
        self.root.state('zoomed')  # Maximizar en Windows

        # Cargar configuración de tema
        self.cargar_configuracion_tema()

        # Aplicar tema inicial
        theme_manager.apply_theme_to_widget(self.root)

        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.cargar_cuentas()
        self.mostrar_notificaciones()

        # Configurar eventos de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def cargar_configuracion_tema(self):
        """Carga la configuración de tema guardada"""
        try:
            config_file = "config/theme_settings.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    theme_manager.set_theme(config.get("theme", "light"))
        except Exception:
            # Usar tema por defecto si hay error
            theme_manager.set_theme("light")

    def guardar_configuracion_tema(self):
        """Guarda la configuración de tema"""
        try:
            os.makedirs("config", exist_ok=True)
            config = {
                "theme": theme_manager.current_theme
            }
            with open("config/theme_settings.json", 'w') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass  # Ignorar errores al guardar

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        self.main_frame = ttk.Frame(self.root, padding="3")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Configurar grid responsive
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        # Header con título y controles
        self.setup_header()

        # Panel de botones
        self.button_panel = ButtonPanel(
            parent=self.main_frame,
            gestionar_cuenta=self.gestionar_cuenta,
            generar_reportes=self.generar_reportes,
            pdf_service=self.pdf_service,
            on_nueva_cuenta=self.mostrar_dialogo_nueva_cuenta,
            on_editar_cuenta=self.editar_cuenta_seleccionada,
            on_marcar_pagada=self.marcar_como_pagada,
            on_eliminar_cuenta=self.eliminar_cuenta_seleccionada,
            on_mostrar_graficos=self.mostrar_graficos,
            on_theme_change=self.on_theme_change
        )
        self.button_panel.get_widget().grid(row=1, column=0, sticky="ew", pady=(2, 3))

        # Tabla de cuentas
        self.cuenta_table = CuentaTable(
            parent=self.main_frame,
            gestionar_cuenta=self.gestionar_cuenta,
            on_cuenta_selected=self.editar_cuenta_seleccionada
        )
        self.cuenta_table.get_widget().grid(row=2, column=0, sticky="nsew")

    def setup_header(self):
        """Configura el header de la aplicación"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        header_frame.columnconfigure(0, weight=1)
        header_frame.columnconfigure(1, weight=0)

        # Título principal
        title_label = tk.Label(
            header_frame,
            text="📊 Registro de Servicios Chile",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, sticky="w")

        # Frame para controles del header
        controls_frame = ttk.Frame(header_frame)
        controls_frame.grid(row=0, column=1, sticky="e")

        # Botón de ayuda rápida
        help_button = tk.Button(
            controls_frame,
            text="❓ Ayuda",
            command=self.mostrar_ayuda_rapida,
            relief="flat",
            borderwidth=1,
            cursor="hand2"
        )
        help_button.grid(row=0, column=1, padx=(3, 0))

        # Botón de tutorial
        tutorial_button = tk.Button(
            controls_frame,
            text="📚 Tutorial",
            command=self.mostrar_tutorial,
            relief="flat",
            borderwidth=1,
            cursor="hand2"
        )
        tutorial_button.grid(row=0, column=0, padx=(0, 3))

        # Aplicar tema
        theme_manager.apply_theme_to_widget(title_label)
        theme_manager.apply_theme_to_widget(help_button)
        theme_manager.apply_theme_to_widget(tutorial_button)

    def setup_menu(self):
        """Configura el menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo Registro", command=self.mostrar_dialogo_nueva_cuenta, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing, accelerator="Ctrl+Q")

        # Menú Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Editar Cuenta", command=self.editar_cuenta_seleccionada, accelerator="Ctrl+E")
        edit_menu.add_command(label="Marcar como Pagada", command=self.marcar_como_pagada)
        edit_menu.add_separator()
        edit_menu.add_command(label="Eliminar Cuenta", command=self.eliminar_cuenta_seleccionada)

        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="Gráficos", command=self.mostrar_graficos, accelerator="Ctrl+G")
        view_menu.add_separator()
        view_menu.add_command(label="Cambiar Tema", command=self.toggle_theme, accelerator="Ctrl+T")

        # Menú Reportes
        reports_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reportes", menu=reports_menu)
        reports_menu.add_command(label="Reporte General", command=self.generar_reporte_general, accelerator="Ctrl+R")
        reports_menu.add_command(label="Resumen Mensual", command=self.generar_resumen_mensual)
        reports_menu.add_command(label="Reporte Anual", command=self.generar_reporte_anual)

        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Tutorial", command=self.mostrar_tutorial, accelerator="F1")
        help_menu.add_command(label="Ayuda Rápida", command=self.mostrar_ayuda_rapida)
        help_menu.add_separator()
        help_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)

    def setup_status_bar(self):
        """Configura la barra de estado"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.grid(row=99, column=0, sticky="ew")

        # Label de estado
        self.status_label = tk.Label(
            self.status_bar,
            text="Listo",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.grid(row=0, column=0, sticky="ew")
        self.status_bar.columnconfigure(0, weight=1)

        # Aplicar tema
        theme_manager.apply_theme_to_widget(self.status_label)

    def on_theme_change(self, new_theme: str):
        """Maneja el cambio de tema"""
        # Aplicar tema a toda la aplicación
        theme_manager.apply_theme_to_all_widgets(self.root)

        # Guardar configuración
        self.guardar_configuracion_tema()

        # Actualizar estado
        self.actualizar_estado(f"Tema cambiado a: {new_theme}")

    def toggle_theme(self):
        """Alterna entre temas"""
        new_theme = theme_manager.toggle_theme()
        self.on_theme_change(new_theme)

    def mostrar_ayuda_rapida(self):
        """Muestra la ayuda rápida"""
        from .components.help_dialog import QuickHelpDialog
        QuickHelpDialog(self.root, "general")

    def mostrar_tutorial(self):
        """Muestra el tutorial interactivo"""
        from .components.help_dialog import HelpDialog
        HelpDialog(self.root)

    def mostrar_acerca_de(self):
        """Muestra información sobre la aplicación"""
        messagebox.showinfo(
            "Acerca de",
            "Registro de Servicios Chile\n\n"
            "Versión: 1.0.0\n"
            "Desarrollado para gestionar cuentas de servicios básicos\n\n"
            "Características:\n"
            "• Gestión completa de cuentas\n"
            "• Interfaz moderna y responsive\n"
            "• Modo oscuro/claro\n"
            "• Reportes PDF profesionales\n"
            "• Gráficos y estadísticas\n"
            "• Notificaciones inteligentes\n\n"
            "© 2024 Registro de Servicios Chile"
        )

    def actualizar_estado(self, mensaje: str):
        """Actualiza el mensaje de la barra de estado"""
        self.status_label.config(text=mensaje)

    def cargar_cuentas(self):
        """Carga todas las cuentas en la tabla"""
        self.cuenta_table.cargar_cuentas()
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
        self.actualizar_estado(f"Cuentas cargadas: {len(cuentas)} desde el JSON")

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

    @handle_ui_errors("Error al marcar como pagada", "MainWindow.marcar_como_pagada")
    def marcar_como_pagada(self):
        """Marca la cuenta seleccionada como pagada"""
        cuenta = self.cuenta_table.obtener_cuenta_seleccionada()
        if cuenta:
            self.gestionar_cuenta.marcar_como_pagada(cuenta.id)
            self.cargar_cuentas()
            self.actualizar_estado("Cuenta marcada como pagada")
            messagebox.showinfo("Éxito", "Cuenta marcada como pagada")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta")

    @handle_ui_errors("Error al eliminar", "MainWindow.eliminar_cuenta_seleccionada")
    def eliminar_cuenta_seleccionada(self):
        """Elimina la cuenta seleccionada"""
        cuenta = self.cuenta_table.obtener_cuenta_seleccionada()
        if cuenta:
            if messagebox.askyesno("Confirmar", f"¿Eliminar cuenta de {cuenta.tipo_servicio.value}?"):
                self.gestionar_cuenta.eliminar_cuenta(cuenta.id)
                self.cargar_cuentas()
                self.actualizar_estado("Cuenta eliminada")
                messagebox.showinfo("Éxito", "Cuenta eliminada")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta")

    @handle_ui_errors("Error al generar reporte", "MainWindow.generar_reporte_general")
    def generar_reporte_general(self):
        """Genera un reporte PDF general"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
        filepath = self.pdf_service.generar_reporte_cuentas(cuentas)
        self.actualizar_estado(f"Reporte generado: {os.path.basename(filepath)}")
        messagebox.showinfo("Éxito", f"Reporte generado: {filepath}")

    @handle_ui_errors("Error al generar resumen", "MainWindow.generar_resumen_mensual")
    def generar_resumen_mensual(self):
        """Genera un resumen mensual PDF"""
        ahora = datetime.now()
        resumen = self.generar_reportes.generar_resumen_mensual(ahora.month, ahora.year)
        filepath = self.pdf_service.generar_reporte_resumen_mensual(resumen)
        self.actualizar_estado(f"Resumen mensual generado: {os.path.basename(filepath)}")
        messagebox.showinfo("Éxito", f"Resumen mensual generado: {filepath}")

    @handle_ui_errors("Error al generar reporte anual", "MainWindow.generar_reporte_anual")
    def generar_reporte_anual(self):
        """Genera un reporte anual PDF"""
        año = datetime.now().year
        resumenes = self.generar_reportes.obtener_resumenes_anuales(año)
        filepath = self.pdf_service.generar_reporte_anual(resumenes, año)
        self.actualizar_estado(f"Reporte anual generado: {os.path.basename(filepath)}")
        messagebox.showinfo("Éxito", f"Reporte anual generado: {filepath}")

    def mostrar_notificaciones(self):
        """Muestra notificaciones de cuentas por vencer"""
        try:
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
        except Exception:
            pass  # Ignorar errores en notificaciones

    @handle_ui_errors("Error al abrir gráficos", "MainWindow.mostrar_graficos")
    def mostrar_graficos(self):
        """Muestra la ventana de gráficos"""
        try:
            from .components import GraficosPanel
            graficos_window = tk.Toplevel(self.root)
            graficos_window.title("Gráficos y Estadísticas")
            graficos_window.geometry("900x700")
            graficos_window.minsize(800, 600)

            # Aplicar tema a la ventana de gráficos
            theme_manager.apply_theme_to_widget(graficos_window)

            graficos_panel = GraficosPanel(graficos_window, self.gestionar_cuenta)
            graficos_panel.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            graficos_window.columnconfigure(0, weight=1)
            graficos_window.rowconfigure(0, weight=1)

            self.actualizar_estado("Ventana de gráficos abierta")
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir gráficos: {str(e)}")

    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Está seguro de que desea salir?"):
            self.guardar_configuracion_tema()
            self.root.destroy()

    def run(self):
        """Ejecuta la aplicación"""
        # Configurar atajos de teclado globales
        self.root.bind('<Control-n>', lambda e: self.mostrar_dialogo_nueva_cuenta())
        self.root.bind('<Control-e>', lambda e: self.editar_cuenta_seleccionada())
        self.root.bind('<Control-g>', lambda e: self.mostrar_graficos())
        self.root.bind('<Control-r>', lambda e: self.generar_reporte_general())
        self.root.bind('<Control-t>', lambda e: self.toggle_theme())
        self.root.bind('<F1>', lambda e: self.mostrar_tutorial())
        self.root.bind('<Control-q>', lambda e: self.on_closing())

        # Centrar la ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1400x800+{x}+{y}")

        self.root.mainloop()