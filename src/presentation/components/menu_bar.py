"""
Barra de menú de la aplicación
"""

import tkinter as tk
from tkinter import ttk


class MenuBar:
    """Barra de menú principal de la aplicación"""

    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self.menu = tk.Menu(root)

        self.create_archivo_menu()
        self.create_editar_menu()
        self.create_herramientas_menu()
        self.create_ayuda_menu()

    def create_archivo_menu(self):
        """Crea el menú Archivo"""
        archivo_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Archivo", menu=archivo_menu)

        archivo_menu.add_command(
            label="📝 Nueva Cuenta",
            command=self.main_window.mostrar_dialogo_nueva_cuenta,
            accelerator="Ctrl+N"
        )

        archivo_menu.add_command(
            label="✏️ Editar Cuenta",
            command=self.main_window.editar_cuenta_seleccionada,
            accelerator="Ctrl+E"
        )

        archivo_menu.add_separator()

        archivo_menu.add_command(
            label="📄 Generar Reporte",
            command=self.main_window.generar_reporte_general,
            accelerator="Ctrl+R"
        )

        archivo_menu.add_separator()

        archivo_menu.add_command(
            label="🚪 Salir",
            command=self.main_window.on_closing,
            accelerator="Ctrl+Q"
        )

    def create_editar_menu(self):
        """Crea el menú Editar"""
        editar_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Editar", menu=editar_menu)

        editar_menu.add_command(
            label="✅ Marcar como Pagada",
            command=self.main_window.marcar_como_pagada
        )

        editar_menu.add_command(
            label="🗑️ Eliminar Cuenta",
            command=self.main_window.eliminar_cuenta_seleccionada
        )

        editar_menu.add_separator()

        editar_menu.add_command(
            label="🔄 Actualizar Lista",
            command=self.main_window.cargar_cuentas
        )

    def create_herramientas_menu(self):
        """Crea el menú de herramientas"""
        herramientas_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Herramientas", menu=herramientas_menu)

        herramientas_menu.add_command(
            label="📊 Gráficos y Estadísticas",
            command=self.main_window.mostrar_graficos,
            accelerator="Ctrl+G"
        )

        herramientas_menu.add_command(
            label="🤖 Inteligencia Artificial",
            command=self.main_window.mostrar_panel_ia,
            accelerator="Ctrl+I"
        )

        herramientas_menu.add_separator()

        herramientas_menu.add_command(
            label="📅 Generar Resumen Mensual",
            command=self.main_window.generar_resumen_mensual
        )

        herramientas_menu.add_command(
            label="📊 Generar Reporte Anual",
            command=self.main_window.generar_reporte_anual
        )

        herramientas_menu.add_separator()

        herramientas_menu.add_command(
            label="🌙 Cambiar Tema",
            command=self.main_window.toggle_theme,
            accelerator="Ctrl+T"
        )

    def create_ayuda_menu(self):
        """Crea el menú de ayuda"""
        ayuda_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Ayuda", menu=ayuda_menu)

        ayuda_menu.add_command(
            label="❓ Ayuda Rápida",
            command=self.main_window.mostrar_ayuda_rapida
        )

        ayuda_menu.add_command(
            label="📚 Tutorial",
            command=self.main_window.mostrar_tutorial,
            accelerator="F1"
        )

        ayuda_menu.add_separator()

        ayuda_menu.add_command(
            label="ℹ️ Acerca de",
            command=self.main_window.mostrar_acerca_de
        )