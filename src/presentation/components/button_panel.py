"""
Componente de panel de botones principales y reportes
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Callable

from ...application.casos_uso import GestionarCuentaServicio, GenerarReportes
from ...infrastructure.pdf_service import PDFService


class ButtonPanel:
    """Componente de panel de botones principales y reportes"""

    def __init__(self, parent, gestionar_cuenta: GestionarCuentaServicio,
                 generar_reportes: GenerarReportes, pdf_service: PDFService,
                 on_nueva_cuenta: Callable = None,
                 on_editar_cuenta: Callable = None,
                 on_marcar_pagada: Callable = None,
                 on_eliminar_cuenta: Callable = None,
                 on_mostrar_graficos: Callable = None):
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

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del componente"""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)

        # Configurar grid para el frame principal
        self.main_frame.columnconfigure(1, weight=1)  # La columna de reportes se expande

        # Botones principales (lado izquierdo)
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=0, column=0, sticky="w", padx=(0, 10))

        ttk.Button(button_frame, text="Nuevo Registro",
                  command=self.on_nueva_cuenta).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Cuenta",
                  command=self.on_editar_cuenta).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Marcar como Pagada",
                  command=self.on_marcar_pagada).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar Cuenta",
                  command=self.on_eliminar_cuenta).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Gráficos",
                  command=self.on_mostrar_graficos).pack(side=tk.LEFT, padx=5)

        # Frame de reportes (lado derecho)
        report_frame = ttk.LabelFrame(self.main_frame, text="Reportes", padding="5")
        report_frame.grid(row=0, column=1, sticky="e", padx=(0, 20))

        ttk.Button(report_frame, text="Reporte General PDF",
                  command=self.generar_reporte_general).pack(side=tk.LEFT, padx=2)
        ttk.Button(report_frame, text="Resumen Mensual PDF",
                  command=self.generar_resumen_mensual).pack(side=tk.LEFT, padx=2)
        ttk.Button(report_frame, text="Reporte Anual PDF",
                  command=self.generar_reporte_anual).pack(side=tk.LEFT, padx=2)

    def generar_reporte_general(self):
        """Genera un reporte PDF general"""
        try:
            cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
            filepath = self.pdf_service.generar_reporte_cuentas(cuentas)
            messagebox.showinfo("Éxito", f"Reporte generado: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {str(e)}")

    def generar_resumen_mensual(self):
        """Genera un resumen mensual PDF"""
        try:
            # Obtener mes y año actual
            ahora = datetime.now()
            resumen = self.generar_reportes.generar_resumen_mensual(ahora.month, ahora.year)
            filepath = self.pdf_service.generar_reporte_resumen_mensual(resumen)
            messagebox.showinfo("Éxito", f"Resumen mensual generado: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar resumen: {str(e)}")

    def generar_reporte_anual(self):
        """Genera un reporte anual PDF"""
        try:
            año = datetime.now().year
            resumenes = self.generar_reportes.obtener_resumenes_anuales(año)
            filepath = self.pdf_service.generar_reporte_anual(resumenes, año)
            messagebox.showinfo("Éxito", f"Reporte anual generado: {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte anual: {str(e)}")