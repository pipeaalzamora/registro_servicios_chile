"""
Panel de botones principales de la aplicación
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Callable, Optional

from ...application.casos_uso import GestionarCuentaServicio, GenerarReportes
from ...infrastructure.pdf_service import PDFService
from ..themes import theme_manager
from .help_dialog import HelpDialog, QuickHelpDialog
from ..utils import error_handler, handle_ui_errors


class ButtonPanel:
    """Componente de panel de botones principales y reportes"""

    def __init__(self, parent, gestionar_cuenta: GestionarCuentaServicio,
                 generar_reportes: GenerarReportes, pdf_service: PDFService,
                 on_nueva_cuenta: Optional[Callable] = None,
                 on_editar_cuenta: Optional[Callable] = None,
                 on_marcar_pagada: Optional[Callable] = None,
                 on_eliminar_cuenta: Optional[Callable] = None,
                 on_mostrar_graficos: Optional[Callable] = None,
                 on_theme_change: Optional[Callable] = None):
        self.parent = parent
        self.gestionar_cuenta = gestionar_cuenta
        self.generar_reportes = generar_reportes
        self.pdf_service = pdf_service

        # Callbacks
        self.on_nueva_cuenta = on_nueva_cuenta
        self.on_editar_cuenta = on_editar_cuenta
        self.on_marcar_pagada = on_marcar_pagada
        self.on_eliminar_cuenta = on_eliminar_cuenta
        self.on_mostrar_graficos = on_mostrar_graficos
        self.on_theme_change = on_theme_change

        self.setup_ui()
        self.bind_shortcuts()

    def setup_ui(self):
        """Configura la interfaz del componente"""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)

        # Configurar grid responsive
        self.main_frame.columnconfigure(1, weight=1)  # La columna de reportes se expande
        self.main_frame.rowconfigure(0, weight=1)

        # Botones principales (lado izquierdo)
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=0, column=0, sticky="w", padx=(0, 3))

        # Botones principales con iconos y tooltips
        self.create_main_buttons(button_frame)

        # Frame de reportes (lado derecho)
        report_frame = ttk.LabelFrame(self.main_frame, text="Reportes", padding="2")
        report_frame.grid(row=0, column=1, sticky="e", padx=(0, 5))

        self.create_report_buttons(report_frame)

        # Frame de utilidades (extremo derecho)
        utils_frame = ttk.Frame(self.main_frame)
        utils_frame.grid(row=0, column=2, sticky="e", padx=(3, 0))

        self.create_utility_buttons(utils_frame)

    def create_main_buttons(self, parent):
        """Crea los botones principales con diseño responsive"""
        # Frame para botones principales
        main_buttons_frame = ttk.Frame(parent)
        main_buttons_frame.grid(row=0, column=0, sticky="w")

        # Botones principales
        buttons_data = [
            ("Nuevo Registro", self.on_nueva_cuenta, "➕"),
            ("Editar Cuenta", self.on_editar_cuenta, "✏️"),
            ("Marcar como Pagada", self.on_marcar_pagada, "✅"),
            ("Eliminar Cuenta", self.on_eliminar_cuenta, "🗑️"),
            ("Gráficos", self.on_mostrar_graficos, "📊")
        ]

        for idx, (text, command, icon) in enumerate(buttons_data):
            btn = tk.Button(
                main_buttons_frame,
                text=f"{icon} {text}",
                command=lambda cmd=command: cmd() if cmd else None,
                relief="flat",
                borderwidth=1,
                padx=6,
                pady=2,
                cursor="hand2"
            )
            btn.grid(row=0, column=idx, padx=1, pady=0)
            self.create_tooltip(btn, text)

    def create_report_buttons(self, parent):
        """Crea los botones de reportes"""
        # Frame para botones de reportes
        report_buttons_frame = ttk.Frame(parent)
        report_buttons_frame.grid(row=0, column=0, sticky="w")

        report_buttons = [
            ("📄 Reporte General", self.generar_reporte_general),
            ("📅 Resumen Mensual", self.generar_resumen_mensual),
            ("📊 Reporte Anual", self.generar_reporte_anual)
        ]

        for idx, (text, command) in enumerate(report_buttons):
            btn = tk.Button(
                report_buttons_frame,
                text=text,
                command=command,
                relief="flat",
                borderwidth=1,
                padx=4,
                pady=1,
                cursor="hand2"
            )
            btn.grid(row=0, column=idx, padx=1, pady=0)
            self.create_tooltip(btn, text.split(" ", 1)[1])

    def create_utility_buttons(self, parent):
        """Crea los botones de utilidades (tema y ayuda)"""
        # Botón de tema
        self.theme_button = tk.Button(
            parent,
            text="��",  # Emoji de luna para modo oscuro
            command=self.toggle_theme,
            relief="flat",
            borderwidth=1,
            width=3,
            cursor="hand2"
        )
        self.theme_button.grid(row=0, column=0, padx=1)
        self.create_tooltip(self.theme_button, "Cambiar tema (Claro/Oscuro)")

        # Botón de ayuda
        help_button = tk.Button(
            parent,
            text="❓",
            command=self.show_help,
            relief="flat",
            borderwidth=1,
            width=3,
            cursor="hand2"
        )
        help_button.grid(row=0, column=1, padx=1)
        self.create_tooltip(help_button, "Ayuda y tutorial")

        # Botón de ayuda rápida
        quick_help_button = tk.Button(
            parent,
            text="ℹ️",
            command=self.show_quick_help,
            relief="flat",
            borderwidth=1,
            width=3,
            cursor="hand2"
        )
        quick_help_button.grid(row=0, column=2, padx=1)
        self.create_tooltip(quick_help_button, "Ayuda rápida")

    def create_tooltip(self, widget, text):
        """Crea un tooltip para un widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(tooltip, text=text, justify=tk.LEFT,
                           background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                           font=("Arial", 8, "normal"))
            label.grid(row=0, column=0, padx=5, pady=2)

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())
            tooltip.bind('<Leave>', lambda e: hide_tooltip())

        widget.bind('<Enter>', show_tooltip)

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        new_theme = theme_manager.toggle_theme()

        # Actualizar icono del botón
        if new_theme == "dark":
            self.theme_button.config(text="☀️")  # Sol para modo claro
        else:
            self.theme_button.config(text="🌙")  # Luna para modo oscuro

        # Aplicar tema a toda la aplicación
        if self.on_theme_change:
            self.on_theme_change(new_theme)

        # Aplicar tema a este componente
        theme_manager.apply_theme_to_all_widgets(self.main_frame)

    def show_help(self):
        """Muestra el tutorial interactivo"""
        HelpDialog(self.parent)

    def show_quick_help(self):
        """Muestra la ayuda rápida"""
        QuickHelpDialog(self.parent, "general")

    def bind_shortcuts(self):
        """Vincula atajos de teclado"""
        if self.on_nueva_cuenta:
            self.parent.bind('<Control-n>', lambda e: self.on_nueva_cuenta())
        self.parent.bind('<Control-f>', lambda e: self.focus_search())
        self.parent.bind('<Control-r>', lambda e: self.generar_reporte_general())
        self.parent.bind('<Control-t>', lambda e: self.toggle_theme())
        self.parent.bind('<F1>', lambda e: self.show_help())

    def focus_search(self):
        """Enfoca el campo de búsqueda"""
        # Este método se implementará cuando se conecte con el componente de tabla
        pass

    @handle_ui_errors("Error al generar reporte", "ButtonPanel.generar_reporte_general")
    def generar_reporte_general(self):
        """Genera un reporte PDF general"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
        filepath = self.pdf_service.generar_reporte_cuentas(cuentas)
        messagebox.showinfo("Éxito", f"Reporte generado: {filepath}")

    @handle_ui_errors("Error al generar resumen", "ButtonPanel.generar_resumen_mensual")
    def generar_resumen_mensual(self):
        """Genera un resumen mensual PDF"""
        # Obtener mes y año actual
        ahora = datetime.now()
        resumen = self.generar_reportes.generar_resumen_mensual(ahora.month, ahora.year)
        filepath = self.pdf_service.generar_reporte_resumen_mensual(resumen)
        messagebox.showinfo("Éxito", f"Resumen mensual generado: {filepath}")

    @handle_ui_errors("Error al generar reporte anual", "ButtonPanel.generar_reporte_anual")
    def generar_reporte_anual(self):
        """Genera un reporte anual PDF"""
        año = datetime.now().year
        resumenes = self.generar_reportes.obtener_resumenes_anuales(año)
        filepath = self.pdf_service.generar_reporte_anual(resumenes, año)
        messagebox.showinfo("Éxito", f"Reporte anual generado: {filepath}")

    def get_widget(self):
        """Retorna el widget principal del componente"""
        return self.main_frame