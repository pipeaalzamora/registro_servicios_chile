"""
Componentes de UI reutilizables
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Optional

from models import CuentaServicio, TipoServicio
from .utils import format_currency, parse_currency_input


class StatsPanel(ttk.Frame):
    """Panel de estadísticas en la parte superior"""

    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets del panel"""
        # Frame para las estadísticas
        stats_frame = ttk.LabelFrame(self, text="Resumen General", padding=10)
        stats_frame.pack(fill=tk.X)

        # Variables para las estadísticas
        self.total_cuentas_var = tk.StringVar(value="0")
        self.total_gastos_var = tk.StringVar(value="$0")
        self.total_pagado_var = tk.StringVar(value="$0")
        self.total_pendiente_var = tk.StringVar(value="$0")
        self.cuentas_vencidas_var = tk.StringVar(value="0")

        # Primera fila
        row1 = ttk.Frame(stats_frame)
        row1.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(row1, text="Total Cuentas:").pack(side=tk.LEFT)
        ttk.Label(row1, textvariable=self.total_cuentas_var, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(row1, text="Total Gastos:").pack(side=tk.LEFT)
        ttk.Label(row1, textvariable=self.total_gastos_var, font=('Arial', 10, 'bold'), foreground='blue').pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(row1, text="Cuentas Vencidas:").pack(side=tk.LEFT)
        ttk.Label(row1, textvariable=self.cuentas_vencidas_var, font=('Arial', 10, 'bold'), foreground='red').pack(side=tk.LEFT, padx=(5, 0))

        # Segunda fila
        row2 = ttk.Frame(stats_frame)
        row2.pack(fill=tk.X)

        ttk.Label(row2, text="Total Pagado:").pack(side=tk.LEFT)
        ttk.Label(row2, textvariable=self.total_pagado_var, font=('Arial', 10, 'bold'), foreground='green').pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(row2, text="Total Pendiente:").pack(side=tk.LEFT)
        ttk.Label(row2, textvariable=self.total_pendiente_var, font=('Arial', 10, 'bold'), foreground='orange').pack(side=tk.LEFT, padx=(5, 0))

    def update_stats(self, stats: dict):
        """Actualiza las estadísticas mostradas"""
        self.total_cuentas_var.set(str(stats.get('total_cuentas', 0)))
        self.total_gastos_var.set(format_currency(stats.get('total_gastos', 0)))
        self.total_pagado_var.set(format_currency(stats.get('total_pagado', 0)))
        self.total_pendiente_var.set(format_currency(stats.get('total_pendiente', 0)))
        self.cuentas_vencidas_var.set(str(stats.get('cuentas_vencidas', 0)))


class CuentaDialog:
    """Diálogo para crear/editar cuentas"""

    def __init__(self, parent, title: str, cuenta: Optional[CuentaServicio] = None):
        self.result = None
        self.cuenta = cuenta
        self.meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x650")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar diálogo
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))

        self._create_widgets()
        self._load_data()

        # Esperar hasta que se cierre el diálogo
        self.dialog.wait_window()

    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tipo de servicio
        ttk.Label(main_frame, text="Tipo de Servicio:").pack(anchor=tk.W, pady=(0, 5))
        self.tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(main_frame, textvariable=self.tipo_var,
                                 values=[tipo.value for tipo in TipoServicio],
                                 state="readonly", width=40)
        tipo_combo.pack(fill=tk.X, pady=(0, 15))

        # Descripción
        ttk.Label(main_frame, text="Descripción:").pack(anchor=tk.W, pady=(0, 5))
        self.descripcion_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.descripcion_var, width=40).pack(fill=tk.X, pady=(0, 15))

        # Monto
        ttk.Label(main_frame, text="Monto (CLP):").pack(anchor=tk.W, pady=(0, 5))
        self.monto_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.monto_var, width=40).pack(fill=tk.X, pady=(0, 15))

        # Fecha de emisión
        ttk.Label(main_frame, text="Fecha de Emisión:").pack(anchor=tk.W, pady=(0, 5))
        fecha_emision_frame = ttk.Frame(main_frame)
        fecha_emision_frame.pack(fill=tk.X, pady=(0, 15))

        self.dia_emision_var = tk.StringVar()
        self.mes_emision_var = tk.StringVar()
        self.año_emision_var = tk.StringVar()

        ttk.Label(fecha_emision_frame, text="Día:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_emision_frame, textvariable=self.dia_emision_var,
                    values=[str(i) for i in range(1, 32)], width=5, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_emision_frame, text="Mes:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_emision_frame, textvariable=self.mes_emision_var,
                    values=self.meses_nombres, width=12, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_emision_frame, text="Año:").pack(side=tk.LEFT)
        ttk.Entry(fecha_emision_frame, textvariable=self.año_emision_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        # Fecha de vencimiento
        ttk.Label(main_frame, text="Fecha de Vencimiento:").pack(anchor=tk.W, pady=(0, 5))
        fecha_venc_frame = ttk.Frame(main_frame)
        fecha_venc_frame.pack(fill=tk.X, pady=(0, 15))

        self.dia_venc_var = tk.StringVar()
        self.mes_venc_var = tk.StringVar()
        self.año_venc_var = tk.StringVar()

        ttk.Label(fecha_venc_frame, text="Día:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_venc_frame, textvariable=self.dia_venc_var,
                    values=[str(i) for i in range(1, 32)], width=5, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_venc_frame, text="Mes:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_venc_frame, textvariable=self.mes_venc_var,
                    values=self.meses_nombres, width=12, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_venc_frame, text="Año:").pack(side=tk.LEFT)
        ttk.Entry(fecha_venc_frame, textvariable=self.año_venc_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        # Fecha de corte (opcional)
        ttk.Label(main_frame, text="Fecha de Corte (opcional):").pack(anchor=tk.W, pady=(0, 5))
        fecha_corte_frame = ttk.Frame(main_frame)
        fecha_corte_frame.pack(fill=tk.X, pady=(0, 15))

        self.dia_corte_var = tk.StringVar()
        self.mes_corte_var = tk.StringVar()
        self.año_corte_var = tk.StringVar()

        ttk.Label(fecha_corte_frame, text="Día:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_corte_frame, textvariable=self.dia_corte_var,
                    values=[""] + [str(i) for i in range(1, 32)], width=5, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_corte_frame, text="Mes:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_corte_frame, textvariable=self.mes_corte_var,
                    values=[""] + self.meses_nombres, width=12, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_corte_frame, text="Año:").pack(side=tk.LEFT)
        ttk.Entry(fecha_corte_frame, textvariable=self.año_corte_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        # Fecha de lectura próxima (opcional)
        ttk.Label(main_frame, text="Fecha de Lectura Próxima (opcional):").pack(anchor=tk.W, pady=(0, 5))
        fecha_lectura_frame = ttk.Frame(main_frame)
        fecha_lectura_frame.pack(fill=tk.X, pady=(0, 15))

        self.dia_lectura_var = tk.StringVar()
        self.mes_lectura_var = tk.StringVar()
        self.año_lectura_var = tk.StringVar()

        ttk.Label(fecha_lectura_frame, text="Día:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_lectura_frame, textvariable=self.dia_lectura_var,
                    values=[""] + [str(i) for i in range(1, 32)], width=5, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_lectura_frame, text="Mes:").pack(side=tk.LEFT)
        ttk.Combobox(fecha_lectura_frame, textvariable=self.mes_lectura_var,
                    values=[""] + self.meses_nombres, width=12, state="readonly").pack(side=tk.LEFT, padx=(5, 10))

        ttk.Label(fecha_lectura_frame, text="Año:").pack(side=tk.LEFT)
        ttk.Entry(fecha_lectura_frame, textvariable=self.año_lectura_var, width=8).pack(side=tk.LEFT, padx=(5, 0))

        # Observaciones
        ttk.Label(main_frame, text="Observaciones:").pack(anchor=tk.W, pady=(0, 5))
        self.observaciones_text = tk.Text(main_frame, height=4, width=40)
        self.observaciones_text.pack(fill=tk.X, pady=(0, 15))

        # Estado pagado (solo para edición)
        if self.cuenta:
            self.pagado_var = tk.BooleanVar()
            ttk.Checkbutton(main_frame, text="Cuenta Pagada",
                           variable=self.pagado_var).pack(anchor=tk.W, pady=(0, 15))

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="Cancelar",
                  command=self._cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Guardar",
                  command=self._save).pack(side=tk.RIGHT)

    def _load_data(self):
        """Carga los datos de la cuenta si está editando"""
        if self.cuenta:
            self.tipo_var.set(self.cuenta.tipo_servicio.value)
            self.descripcion_var.set(self.cuenta.descripcion)
            self.monto_var.set(format_currency(self.cuenta.monto))

            # Fecha de emisión
            if self.cuenta.fecha_emision:
                self.dia_emision_var.set(str(self.cuenta.fecha_emision.day))
                self.mes_emision_var.set(self.meses_nombres[self.cuenta.fecha_emision.month - 1])
                self.año_emision_var.set(str(self.cuenta.fecha_emision.year))

            # Fecha de vencimiento
            if self.cuenta.fecha_vencimiento:
                self.dia_venc_var.set(str(self.cuenta.fecha_vencimiento.day))
                self.mes_venc_var.set(self.meses_nombres[self.cuenta.fecha_vencimiento.month - 1])
                self.año_venc_var.set(str(self.cuenta.fecha_vencimiento.year))

            # Fecha de corte
            if self.cuenta.fecha_corte:
                self.dia_corte_var.set(str(self.cuenta.fecha_corte.day))
                self.mes_corte_var.set(self.meses_nombres[self.cuenta.fecha_corte.month - 1])
                self.año_corte_var.set(str(self.cuenta.fecha_corte.year))
            else:
                # Limpiar campos si no hay fecha
                self.dia_corte_var.set("")
                self.mes_corte_var.set("")
                self.año_corte_var.set("")

            # Fecha de lectura próxima
            if hasattr(self.cuenta, 'fecha_lectura_proxima') and self.cuenta.fecha_lectura_proxima:
                self.dia_lectura_var.set(str(self.cuenta.fecha_lectura_proxima.day))
                self.mes_lectura_var.set(self.meses_nombres[self.cuenta.fecha_lectura_proxima.month - 1])
                self.año_lectura_var.set(str(self.cuenta.fecha_lectura_proxima.year))
            else:
                # Limpiar campos si no hay fecha
                self.dia_lectura_var.set("")
                self.mes_lectura_var.set("")
                self.año_lectura_var.set("")

            self.observaciones_text.insert('1.0', self.cuenta.observaciones)

            if hasattr(self, 'pagado_var'):
                self.pagado_var.set(self.cuenta.pagado)
        else:
            # Valores por defecto para nueva cuenta
            now = datetime.now()
            self.dia_emision_var.set(str(now.day))
            self.mes_emision_var.set(self.meses_nombres[now.month - 1])
            self.año_emision_var.set(str(now.year))

            # Vencimiento por defecto: 15 días después
            venc = now.replace(day=min(now.day + 15, 28))  # Evitar problemas con días del mes
            self.dia_venc_var.set(str(venc.day))
            self.mes_venc_var.set(self.meses_nombres[venc.month - 1])
            self.año_venc_var.set(str(venc.year))

            # Valores por defecto para fechas opcionales (año actual)
            self.año_corte_var.set(str(now.year))
            self.año_lectura_var.set(str(now.year))

    def _save(self):
        """Guarda los datos del formulario"""
        try:
            # Convertir nombres de meses a números
            mes_emision_num = self.meses_nombres.index(self.mes_emision_var.get()) + 1
            mes_venc_num = self.meses_nombres.index(self.mes_venc_var.get()) + 1

            # Validar y crear fechas
            fecha_emision = datetime(
                int(self.año_emision_var.get()),
                mes_emision_num,
                int(self.dia_emision_var.get())
            )

            fecha_vencimiento = datetime(
                int(self.año_venc_var.get()),
                mes_venc_num,
                int(self.dia_venc_var.get())
            )

            fecha_corte = None
            if (self.dia_corte_var.get().strip() and self.mes_corte_var.get().strip() and
                self.año_corte_var.get().strip()):
                try:
                    mes_corte_num = self.meses_nombres.index(self.mes_corte_var.get()) + 1
                    fecha_corte = datetime(
                        int(self.año_corte_var.get()),
                        mes_corte_num,
                        int(self.dia_corte_var.get())
                    )
                except (ValueError, IndexError):
                    # Si hay error en la fecha, dejarla como None
                    fecha_corte = None

            fecha_lectura_proxima = None
            if (self.dia_lectura_var.get().strip() and self.mes_lectura_var.get().strip() and
                self.año_lectura_var.get().strip()):
                try:
                    mes_lectura_num = self.meses_nombres.index(self.mes_lectura_var.get()) + 1
                    fecha_lectura_proxima = datetime(
                        int(self.año_lectura_var.get()),
                        mes_lectura_num,
                        int(self.dia_lectura_var.get())
                    )
                except (ValueError, IndexError):
                    # Si hay error en la fecha, dejarla como None
                    fecha_lectura_proxima = None

            # Crear cuenta
            cuenta = CuentaServicio(
                tipo_servicio=TipoServicio(self.tipo_var.get()),
                descripcion=self.descripcion_var.get().strip(),
                monto=parse_currency_input(self.monto_var.get()),
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                fecha_corte=fecha_corte,
                fecha_lectura_proxima=fecha_lectura_proxima,
                observaciones=self.observaciones_text.get('1.0', tk.END).strip()
            )

            # Si está editando, mantener estado de pago
            if self.cuenta and hasattr(self, 'pagado_var'):
                cuenta.pagado = self.pagado_var.get()
                if cuenta.pagado and self.cuenta.fecha_pago:
                    cuenta.fecha_pago = self.cuenta.fecha_pago

            self.result = cuenta
            self.dialog.destroy()

        except ValueError as e:
            tk.messagebox.showerror("Error", f"Error en los datos ingresados: {e}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error inesperado: {e}")

    def _cancel(self):
        """Cancela el diálogo"""
        self.dialog.destroy()