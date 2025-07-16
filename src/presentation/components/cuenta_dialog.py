"""
Componente de diálogo para crear/editar cuentas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Callable

from ...domain.entities import TipoServicio, CuentaServicio
from ...domain.validators import CuentaServicioValidator, TextValidator
from ...application.casos_uso import GestionarCuentaServicio
from .calendar_widget import DateEntryWithCalendar
from ..utils import error_handler, handle_validation_errors


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
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

        # Variables
        self.tipo_var = tk.StringVar()
        self.monto_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()

        # Crear widgets
        self.crear_widgets(main_frame)

    def crear_widgets(self, parent):
        """Crea los widgets del formulario"""
        # Tipo de servicio
        ttk.Label(parent, text="Tipo de Servicio:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        tipo_combo = ttk.Combobox(parent, textvariable=self.tipo_var,
                                 values=[t.value for t in TipoServicio], state="readonly")
        tipo_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Fecha de emisión
        self.fecha_emision_widget = DateEntryWithCalendar(
            parent, "Fecha de Emisión:",
            initial_date=datetime.now(),
            min_date=datetime.now() - timedelta(days=3650),
            max_date=datetime.now() + timedelta(days=365),
            row=2, column=0, sticky="ew"
        )

        # Fecha de vencimiento
        self.fecha_vencimiento_widget = DateEntryWithCalendar(
            parent, "Fecha de Vencimiento:",
            initial_date=datetime.now() + timedelta(days=30),
            min_date=datetime.now(),
            max_date=datetime.now() + timedelta(days=730),
            row=4, column=0, sticky="ew"
        )

        # Monto
        ttk.Label(parent, text="Monto (CLP):").grid(row=6, column=0, sticky="w", pady=(0, 5))
        monto_entry = ttk.Entry(parent, textvariable=self.monto_var)
        monto_entry.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Descripción
        ttk.Label(parent, text="Descripción:").grid(row=8, column=0, sticky="w", pady=(0, 5))
        descripcion_entry = ttk.Entry(parent, textvariable=self.descripcion_var)
        descripcion_entry.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Fecha próxima lectura (opcional)
        self.fecha_proxima_lectura_widget = DateEntryWithCalendar(
            parent, "Próxima Lectura (opcional):",
            initial_date=None,
            min_date=datetime.now(),
            max_date=datetime.now() + timedelta(days=365),
            row=10, column=0, sticky="ew"
        )

        # Fecha de corte (opcional)
        self.fecha_corte_widget = DateEntryWithCalendar(
            parent, "Fecha de Corte (opcional):",
            initial_date=None,
            min_date=datetime.now(),
            max_date=datetime.now() + timedelta(days=365),
            row=12, column=0, sticky="ew"
        )

        # Observaciones
        ttk.Label(parent, text="Observaciones:").grid(row=14, column=0, sticky="w", pady=(0, 5))
        self.observaciones_text = tk.Text(parent, height=4, width=50)
        self.observaciones_text.grid(row=15, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Checkbox para pagado (solo en edición)
        if self.cuenta:
            self.pagado_var = tk.BooleanVar(value=self.cuenta.pagado)
            pagado_check = ttk.Checkbutton(parent, text="Marcar como pagada",
                                          variable=self.pagado_var)
            pagado_check.grid(row=16, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Botones
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=17, column=0, columnspan=2, pady=(20, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        ttk.Button(button_frame, text="Guardar", command=self.guardar).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Cancelar", command=self.dialog.destroy).grid(row=0, column=1, padx=(5, 0))

    def cargar_datos(self):
        """Carga los datos de la cuenta existente"""
        if not self.cuenta:
            return

        self.tipo_var.set(self.cuenta.tipo_servicio.value)
        self.monto_var.set(str(int(self.cuenta.monto)))
        self.descripcion_var.set(self.cuenta.descripcion)

        self.fecha_emision_widget.set_date(self.cuenta.fecha_emision)
        self.fecha_vencimiento_widget.set_date(self.cuenta.fecha_vencimiento)

        if self.cuenta.fecha_proxima_lectura:
            self.fecha_proxima_lectura_widget.set_date(self.cuenta.fecha_proxima_lectura)
        if self.cuenta.fecha_corte:
            self.fecha_corte_widget.set_date(self.cuenta.fecha_corte)

        self.observaciones_text.delete('1.0', tk.END)
        self.observaciones_text.insert('1.0', self.cuenta.observaciones)

    @handle_validation_errors("CuentaDialog.guardar")
    def guardar(self):
        """Guarda la cuenta usando el validador centralizado"""
        # Validaciones básicas
        if not self.tipo_var.get():
            error_handler.handle_validation_error("Debe seleccionar un tipo de servicio")
            return

        if not self.monto_var.get():
            error_handler.handle_validation_error("Debe ingresar un monto")
            return

        if not self.descripcion_var.get().strip():
            error_handler.handle_validation_error("Debe ingresar una descripción")
            return

        # Parsear datos
        tipo_servicio = TipoServicio(self.tipo_var.get())

        fecha_emision = self.fecha_emision_widget.get_date()
        fecha_vencimiento = self.fecha_vencimiento_widget.get_date()

        if not fecha_emision:
            error_handler.handle_validation_error("Debe seleccionar una fecha de emisión válida")
            return

        if not fecha_vencimiento:
            error_handler.handle_validation_error("Debe seleccionar una fecha de vencimiento válida")
            return

        # Parsear monto
        try:
            monto = float(self.monto_var.get())
        except ValueError:
            error_handler.handle_data_error("El monto debe ser un número válido")
            return

        # Sanitizar texto usando el validador centralizado
        descripcion = TextValidator.sanitizar_texto(self.descripcion_var.get().strip())
        observaciones = TextValidator.sanitizar_texto(self.observaciones_text.get('1.0', tk.END).strip())

        # Obtener fechas opcionales
        fecha_proxima_lectura = self.fecha_proxima_lectura_widget.get_date()
        fecha_corte = self.fecha_corte_widget.get_date()

        # Validar usando el validador centralizado
        errores = CuentaServicioValidator.validar_cuenta_completa(
            tipo_servicio=tipo_servicio,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            monto=monto,
            descripcion=descripcion,
            observaciones=observaciones,
            fecha_proxima_lectura=fecha_proxima_lectura,
            fecha_corte=fecha_corte
        )

        if errores:
            error_handler.handle_validation_error("\n".join(errores))
            return

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
                error_handler.handle_ui_error("No se pudo actualizar la cuenta")
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

    def show(self):
        """Muestra el diálogo"""
        self.dialog.wait_window()