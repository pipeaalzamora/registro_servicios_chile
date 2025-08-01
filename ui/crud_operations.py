"""
Operaciones CRUD para cuentas de servicios
"""

from tkinter import messagebox
from typing import Optional, List
from models import CuentaServicio, TipoServicio, validar_cuenta
from .components import CuentaDialog


class CrudOperations:
    """Maneja las operaciones CRUD de cuentas"""

    def __init__(self, main_window):
        self.main_window = main_window
        self.db_manager = main_window.db_manager

    def nueva_cuenta(self):
        """Abre diálogo para nueva cuenta"""
        dialog = CuentaDialog(self.main_window.root, "Nueva Cuenta")
        if dialog.result:
            cuenta = dialog.result
            errores = validar_cuenta(cuenta)

            if errores:
                messagebox.showerror("Error de Validación", "\n".join(errores))
                return

            try:
                self.db_manager.crear_cuenta(cuenta)
                self.main_window._load_data()
                messagebox.showinfo("Éxito", "Cuenta creada exitosamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear cuenta: {e}")

    def editar_cuenta(self):
        """Abre diálogo para editar cuenta"""
        cuenta = self.main_window._get_selected_cuenta()
        if not cuenta:
            messagebox.showwarning("Advertencia", "Seleccione una cuenta para editar")
            return

        dialog = CuentaDialog(self.main_window.root, "Editar Cuenta", cuenta)
        if dialog.result:
            cuenta_editada = dialog.result
            cuenta_editada.id = cuenta.id  # Mantener el ID original

            errores = validar_cuenta(cuenta_editada)
            if errores:
                messagebox.showerror("Error de Validación", "\n".join(errores))
                return

            try:
                self.db_manager.actualizar_cuenta(cuenta_editada)
                self.main_window._load_data()
                messagebox.showinfo("Éxito", "Cuenta actualizada exitosamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar cuenta: {e}")

    def eliminar_cuenta(self):
        """Elimina las cuentas seleccionadas"""
        cuentas_seleccionadas = self.main_window._get_selected_cuentas()
        if not cuentas_seleccionadas:
            messagebox.showwarning("Advertencia", "Seleccione una o más cuentas para eliminar")
            return

        # Mensaje de confirmación
        if len(cuentas_seleccionadas) == 1:
            mensaje = f"¿Está seguro de eliminar la cuenta '{cuentas_seleccionadas[0].descripcion}'?"
        else:
            mensaje = f"¿Está seguro de eliminar {len(cuentas_seleccionadas)} cuentas seleccionadas?"

        if messagebox.askyesno("Confirmar Eliminación", mensaje):
            try:
                eliminadas = 0
                errores = 0

                for cuenta in cuentas_seleccionadas:
                    try:
                        if self.db_manager.eliminar_cuenta(cuenta.id):
                            eliminadas += 1
                        else:
                            errores += 1
                    except Exception:
                        errores += 1

                self.main_window._load_data()

                if errores == 0:
                    if eliminadas == 1:
                        messagebox.showinfo("Éxito", "Cuenta eliminada exitosamente")
                    else:
                        messagebox.showinfo("Éxito", f"{eliminadas} cuentas eliminadas exitosamente")
                else:
                    messagebox.showwarning("Parcialmente completado",
                                         f"Eliminadas: {eliminadas}, Errores: {errores}")

            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cuentas: {e}")

    def marcar_pagado(self):
        """Marca la cuenta seleccionada como pagada"""
        cuenta = self.main_window._get_selected_cuenta()
        if not cuenta:
            messagebox.showwarning("Advertencia", "Seleccione una cuenta para marcar como pagada")
            return

        if cuenta.pagado:
            messagebox.showinfo("Información", "La cuenta ya está marcada como pagada")
            return

        if messagebox.askyesno("Confirmar", f"¿Marcar como pagada la cuenta '{cuenta.descripcion}'?"):
            try:
                cuenta.marcar_como_pagado()
                self.db_manager.actualizar_cuenta(cuenta)
                self.main_window._load_data()
                messagebox.showinfo("Éxito", "Cuenta marcada como pagada")
            except Exception as e:
                messagebox.showerror("Error", f"Error al marcar cuenta como pagada: {e}")

    def ver_detalles(self):
        """Muestra detalles de la cuenta seleccionada"""
        if not self.main_window.selected_cuenta:
            messagebox.showwarning("Advertencia", "Seleccione una cuenta para ver detalles")
            return

        cuenta = self.main_window.selected_cuenta

        # Crear ventana de detalles
        import tkinter as tk
        from tkinter import ttk
        from .utils import format_currency, format_date

        details_window = tk.Toplevel(self.main_window.root)
        details_window.title(f"Detalles - {cuenta.descripcion}")
        details_window.geometry("400x500")
        details_window.transient(self.main_window.root)
        details_window.grab_set()

        # Aplicar tema
        from .themes import theme_manager
        theme_manager.apply_theme_to_widget(details_window)

        # Frame principal
        main_frame = ttk.Frame(details_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Información detallada
        info_text = f"""
Tipo de Servicio: {cuenta.tipo_servicio.value}
Descripción: {cuenta.descripcion}
Monto: {format_currency(cuenta.monto)}
Estado: {cuenta.get_estado().value}

Fecha de Emisión: {format_date(cuenta.fecha_emision)}
Fecha de Vencimiento: {format_date(cuenta.fecha_vencimiento)}
Fecha de Corte: {format_date(cuenta.fecha_corte) if cuenta.fecha_corte else "No definida"}
Próxima Lectura: {format_date(getattr(cuenta, 'fecha_lectura_proxima', None)) if hasattr(cuenta, 'fecha_lectura_proxima') and cuenta.fecha_lectura_proxima else "No definida"}

Días para vencer: {cuenta.dias_para_vencer() if not cuenta.pagado else "Pagado"}

Observaciones:
{cuenta.observaciones if cuenta.observaciones else "Sin observaciones"}

Creado: {format_date(cuenta.created_at) if cuenta.created_at else "No disponible"}
Actualizado: {format_date(cuenta.updated_at) if cuenta.updated_at else "No disponible"}
        """.strip()

        # Mostrar información
        info_label = ttk.Label(main_frame, text=info_text, justify='left', style='Small.TLabel')
        info_label.pack(anchor='nw', fill=tk.BOTH, expand=True)

        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar",
                  command=details_window.destroy).pack(pady=(10, 0))