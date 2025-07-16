"""
Componente de diálogo para crear/editar cuentas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Callable
import re

from ...domain.entities import TipoServicio, CuentaServicio
from ...application.casos_uso import GestionarCuentaServicio
from .calendar_widget import DateEntryWithCalendar


class CuentaDialog:
    """Diálogo para crear/editar cuentas"""

    def __init__(self, parent, gestionar_cuenta: GestionarCuentaServicio,
                 callback_actualizar: Callable, cuenta: Optional[CuentaServicio] = None):
        self.parent = parent
        self.gestionar_cuenta = gestionar_cuenta
        self.callback_actualizar = callback_actualizar
        self.cuenta = cuenta

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Registro" if not cuenta else "Editar Registro")
        self.dialog.geometry("550x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.setup_ui()
        if cuenta:
            self.cargar_datos()

    def setup_ui(self):
        """Configura la interfaz del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tipo de servicio
        ttk.Label(main_frame, text="Tipo de Servicio:").grid(row=0, column=0, sticky="w", pady=5)
        self.tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(main_frame, textvariable=self.tipo_var,
                                 values=[t.value for t in TipoServicio], state="readonly")
        tipo_combo.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

                # Fecha de emisión
        self.fecha_emision_widget = DateEntryWithCalendar(
            main_frame, "Fecha de Emisión:",
            initial_date=datetime.now(),
            min_date=datetime.now() - timedelta(days=3650),  # 10 años atrás
            max_date=datetime.now() + timedelta(days=365),   # 1 año adelante
            row=1, column=0, padx=(0, 10)
        )

        # Fecha de vencimiento
        self.fecha_vencimiento_widget = DateEntryWithCalendar(
            main_frame, "Fecha de Vencimiento:",
            initial_date=datetime.now() + timedelta(days=30),
            min_date=datetime.now(),
            max_date=datetime.now() + timedelta(days=730),   # 2 años adelante
            row=2, column=0, padx=(0, 10)
        )

        # Fecha de próxima lectura
        self.fecha_proxima_lectura_widget = DateEntryWithCalendar(
            main_frame, "Próxima Lectura:",
            initial_date=None,
            min_date=datetime.now(),
            max_date=datetime.now() + timedelta(days=365),   # 1 año adelante
            row=3, column=0, padx=(0, 10)
        )
        ttk.Label(main_frame, text="(Opcional)").grid(row=3, column=2, sticky="w", padx=(5, 0), pady=5)

        # Fecha de corte
        self.fecha_corte_widget = DateEntryWithCalendar(
            main_frame, "Fecha de Corte:",
            initial_date=None,
            min_date=datetime.now(),
            max_date=datetime.now() + timedelta(days=365),   # 1 año adelante
            row=4, column=0, padx=(0, 10)
        )
        ttk.Label(main_frame, text="(Opcional)").grid(row=4, column=2, sticky="w", padx=(5, 0), pady=5)

        # Monto
        ttk.Label(main_frame, text="Monto:").grid(row=5, column=0, sticky="w", pady=5)
        self.monto_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.monto_var).grid(row=5, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=6, column=0, sticky="w", pady=5)
        self.descripcion_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.descripcion_var).grid(row=6, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Observaciones
        ttk.Label(main_frame, text="Observaciones:").grid(row=7, column=0, sticky="w", pady=5)
        self.observaciones_text = tk.Text(main_frame, height=4, width=40)
        self.observaciones_text.grid(row=7, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Frame para mensajes de validación
        self.validation_frame = ttk.Frame(main_frame)
        self.validation_frame.grid(row=8, column=0, columnspan=3, pady=10, sticky="ew")
        self.validation_label = ttk.Label(self.validation_frame, text="", foreground="red")
        self.validation_label.pack()

        # Estado de pago (solo para edición)
        if self.cuenta:
            ttk.Label(main_frame, text="Estado:").grid(row=9, column=0, sticky="w", pady=5)
            self.pagado_var = tk.BooleanVar(value=self.cuenta.pagado)
            ttk.Checkbutton(main_frame, text="Pagado", variable=self.pagado_var).grid(row=9, column=1, sticky="w", padx=(10, 0), pady=5)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=20)

        ttk.Button(button_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Configurar grid
        main_frame.columnconfigure(1, weight=1)

                # Configurar validaciones en tiempo real
        # self.configurar_validaciones_tiempo_real()  # Comentado temporalmente

    def cargar_datos(self):
        """Carga los datos de la cuenta para edición"""
        if not self.cuenta:
            return

        self.tipo_var.set(self.cuenta.tipo_servicio.value)
        self.fecha_emision_widget.set_date(self.cuenta.fecha_emision)
        self.fecha_vencimiento_widget.set_date(self.cuenta.fecha_vencimiento)
        self.monto_var.set(str(self.cuenta.monto))
        self.descripcion_var.set(self.cuenta.descripcion)
        self.observaciones_text.delete('1.0', tk.END)
        self.observaciones_text.insert('1.0', self.cuenta.observaciones)

        # Cargar fechas opcionales
        if self.cuenta.fecha_proxima_lectura:
            self.fecha_proxima_lectura_widget.set_date(self.cuenta.fecha_proxima_lectura)
        if self.cuenta.fecha_corte:
            self.fecha_corte_widget.set_date(self.cuenta.fecha_corte)

    def guardar(self):
        """Guarda la cuenta con validaciones avanzadas"""
        try:
            # Validar datos básicos
            if not self.tipo_var.get():
                messagebox.showerror("Error", "Debe seleccionar un tipo de servicio")
                return

            if not self.monto_var.get():
                messagebox.showerror("Error", "Debe ingresar un monto")
                return

            if not self.descripcion_var.get().strip():
                messagebox.showerror("Error", "Debe ingresar una descripción")
                return

            # Parsear y validar datos con validaciones avanzadas
            tipo_servicio = TipoServicio(self.tipo_var.get())

            # Obtener fechas de los widgets de calendario
            fecha_emision = self.fecha_emision_widget.get_date()
            fecha_vencimiento = self.fecha_vencimiento_widget.get_date()

            if not fecha_emision:
                messagebox.showerror("Error", "Debe seleccionar una fecha de emisión válida")
                return

            if not fecha_vencimiento:
                messagebox.showerror("Error", "Debe seleccionar una fecha de vencimiento válida")
                return

            # Parsear monto
            try:
                monto = float(self.monto_var.get())
            except ValueError:
                messagebox.showerror("Error", "El monto debe ser un número válido")
                return

            # Validar datos básicos
            if monto <= 0:
                messagebox.showerror("Error", "El monto debe ser mayor a 0")
                return

            if monto > 10000000:
                messagebox.showerror("Error", "El monto no puede exceder $10,000,000")
                return

            if fecha_vencimiento <= fecha_emision:
                messagebox.showerror("Error", "La fecha de vencimiento debe ser posterior a la fecha de emisión")
                return

            # Sanitizar texto
            descripcion = self.descripcion_var.get().strip()
            observaciones = self.observaciones_text.get('1.0', tk.END).strip()

            # Remover caracteres peligrosos
            descripcion = re.sub(r'[<>"\']', '', descripcion)
            observaciones = re.sub(r'[<>"\']', '', observaciones)

            # Obtener fechas opcionales de los widgets de calendario
            fecha_proxima_lectura = self.fecha_proxima_lectura_widget.get_date()
            fecha_corte = self.fecha_corte_widget.get_date()

            if self.cuenta:
                # Actualizar cuenta existente
                self.cuenta.tipo_servicio = tipo_servicio
                self.cuenta.fecha_emision = fecha_emision
                self.cuenta.fecha_vencimiento = fecha_vencimiento
                self.cuenta.monto = monto
                self.cuenta.descripcion = descripcion
                self.cuenta.observaciones = observaciones
                self.cuenta.fecha_proxima_lectura = fecha_proxima_lectura
                self.cuenta.fecha_corte = fecha_corte

                if hasattr(self, 'pagado_var'):
                    self.cuenta.pagado = self.pagado_var.get()

                if self.gestionar_cuenta.actualizar_cuenta(self.cuenta):
                    messagebox.showinfo("Éxito", "Cuenta actualizada correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo actualizar la cuenta")
            else:
                # Crear nueva cuenta
                cuenta = self.gestionar_cuenta.crear_cuenta(
                    tipo_servicio=tipo_servicio,
                    fecha_emision=fecha_emision,
                    fecha_vencimiento=fecha_vencimiento,
                    monto=monto,
                    descripcion=descripcion,
                    observaciones=observaciones
                )

                # Actualizar fechas opcionales
                if fecha_proxima_lectura:
                    cuenta.fecha_proxima_lectura = fecha_proxima_lectura
                if fecha_corte:
                    cuenta.fecha_corte = fecha_corte

                self.gestionar_cuenta.actualizar_cuenta(cuenta)
                messagebox.showinfo("Éxito", "Cuenta creada correctamente")

            self.callback_actualizar()
            self.dialog.destroy()

        except ValueError as e:
            messagebox.showerror("Error de Datos", f"Error en los datos: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Error inesperado: {str(e)}")

    def show(self):
        """Muestra el diálogo"""
        self.dialog.wait_window()