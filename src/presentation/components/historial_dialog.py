"""
Diálogo para mostrar el historial de cambios de una cuenta
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List

from ...domain.entities import CuentaServicio, HistorialCambio, TipoCambio
from ...infrastructure.utils import formatear_moneda_clp_simple


class HistorialDialog:
    """Diálogo para mostrar el historial de una cuenta"""

    def __init__(self, parent, cuenta: CuentaServicio):
        self.parent = parent
        self.cuenta = cuenta

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Historial - {cuenta.tipo_servicio.value}")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        self.cargar_historial()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Información de la cuenta
        info_frame = ttk.LabelFrame(main_frame, text="Información de la Cuenta", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        # Grid para información
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)

        ttk.Label(info_frame, text="Servicio:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Label(info_frame, text=self.cuenta.tipo_servicio.value, font=('Arial', 10, 'bold')).grid(row=0, column=1, sticky="w")

        ttk.Label(info_frame, text="Monto:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        ttk.Label(info_frame, text=formatear_moneda_clp_simple(self.cuenta.monto), font=('Arial', 10, 'bold')).grid(row=0, column=3, sticky="w")

        ttk.Label(info_frame, text="Estado:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        estado_texto = "Pagado" if self.cuenta.pagado else "Pendiente"
        if self.cuenta.esta_vencida():
            estado_texto = "Vencido"
        elif self.cuenta.esta_en_riesgo_corte():
            estado_texto = "En Riesgo de Corte"

        ttk.Label(info_frame, text=estado_texto, font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky="w", pady=(5, 0))

        ttk.Label(info_frame, text="Descripción:").grid(row=1, column=2, sticky="w", padx=(20, 5), pady=(5, 0))
        ttk.Label(info_frame, text=self.cuenta.descripcion).grid(row=1, column=3, sticky="w", pady=(5, 0))

        # Título del historial
        ttk.Label(main_frame, text="Historial de Cambios", font=('Arial', 12, 'bold')).pack(pady=(10, 5))

        # Frame para la tabla de historial
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Crear Treeview para el historial
        columns = ('Fecha', 'Tipo', 'Descripción', 'Detalles')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Configurar columnas
        self.tree.heading('Fecha', text='Fecha')
        self.tree.heading('Tipo', text='Tipo de Cambio')
        self.tree.heading('Descripción', text='Descripción')
        self.tree.heading('Detalles', text='Detalles')

        self.tree.column('Fecha', width=150)
        self.tree.column('Tipo', width=120)
        self.tree.column('Descripción', width=300)
        self.tree.column('Detalles', width=200)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Configurar estilos para diferentes tipos de cambio
        self._configurar_estilos()

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Cerrar", command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _configurar_estilos(self):
        """Configura los estilos para diferentes tipos de cambio"""
        self.tree.tag_configure('creacion', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('pago', background='#cce5ff', foreground='#004085')
        self.tree.tag_configure('edicion', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('eliminacion', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('vencimiento', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('riesgo', background='#fff3cd', foreground='#856404')

    def cargar_historial(self):
        """Carga el historial en la tabla"""
        if not self.cuenta.historial:
            # Si no hay historial, crear entrada de creación
            self._agregar_entrada_creacion()
            return

        # Ordenar historial por fecha (más reciente primero)
        historial_ordenado = sorted(self.cuenta.historial, key=lambda x: x.fecha_cambio, reverse=True)

        for cambio in historial_ordenado:
            self._insertar_cambio(cambio)

    def _agregar_entrada_creacion(self):
        """Agrega una entrada de creación si no hay historial"""
        self.tree.insert('', 'end', values=(
            self.cuenta.fecha_emision.strftime('%d/%m/%Y %H:%M'),
            'Creación',
            'Cuenta creada',
            f'Monto: {formatear_moneda_clp_simple(self.cuenta.monto)}'
        ), tags=('creacion',))

    def _insertar_cambio(self, cambio: HistorialCambio):
        """Inserta un cambio en la tabla"""
        # Determinar tag según el tipo de cambio
        tag = cambio.tipo_cambio.value.lower().replace(' ', '_')

        # Generar detalles
        detalles = self._generar_detalles(cambio)

        self.tree.insert('', 'end', values=(
            cambio.fecha_cambio.strftime('%d/%m/%Y %H:%M'),
            cambio.tipo_cambio.value,
            cambio.descripcion,
            detalles
        ), tags=(tag,))

    def _generar_detalles(self, cambio: HistorialCambio) -> str:
        """Genera los detalles del cambio"""
        if cambio.tipo_cambio == TipoCambio.PAGO:
            return f"Pagado el {cambio.fecha_cambio.strftime('%d/%m/%Y')}"

        elif cambio.tipo_cambio == TipoCambio.EDICION:
            detalles = []
            if cambio.datos_anteriores and cambio.datos_nuevos:
                for campo, valor_anterior in cambio.datos_anteriores.items():
                    if campo in cambio.datos_nuevos:
                        valor_nuevo = cambio.datos_nuevos[campo]
                        if valor_anterior != valor_nuevo:
                            detalles.append(f"{campo}: {valor_anterior} → {valor_nuevo}")
            return "; ".join(detalles) if detalles else "Datos modificados"

        elif cambio.tipo_cambio == TipoCambio.VENCIMIENTO:
            return "Cuenta vencida"

        elif cambio.tipo_cambio == TipoCambio.RIESGO_CORTE:
            return "En riesgo de corte"

        else:
            return ""

    def show(self):
        """Muestra el diálogo"""
        self.dialog.wait_window()