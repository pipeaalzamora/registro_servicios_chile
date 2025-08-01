"""
Ventana principal refactorizada de la aplicación
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
from typing import List, Optional

from models import CuentaServicio, TipoServicio, validar_cuenta
from database_manager import DatabaseManager
from reports import ReportManager
from .components import StatsPanel, CuentaDialog
from .enhanced_components import EnhancedStatsPanel, EnhancedCuentaTable, SearchBox, ProgressDialog
from .notifications import NotificationManager, NotificationIndicator
from .themes import theme_manager
from .utils import format_currency, format_date
from .crud_operations import CrudOperations

from .event_handlers import EventHandlers
from config import APP_CONFIG, UI_CONFIG, NOTIFICATIONS_CONFIG


class MainWindow:
    """Ventana principal de la aplicación"""

    def __init__(self, db_manager: DatabaseManager, report_generator: ReportManager):
        self.db_manager = db_manager
        self.report_generator = report_generator

        self.root = tk.Tk()
        self.root.title(APP_CONFIG.get('title', 'Registro de Servicios Chile'))
        self.root.geometry(APP_CONFIG.get('window_size', '1400x800'))
        self.root.minsize(*map(int, APP_CONFIG.get('min_window_size', '1000x700').split('x')))

        # Variables
        self.cuentas_actuales = []
        self.filtro_actual = ""
        self.selected_cuenta = None
        self.graphics_window = None

        # Inicializar gestores
        self.crud_operations = CrudOperations(self)

        self.event_handlers = EventHandlers(self)

        # Configurar tema
        self._setup_theme()

        # Configurar UI
        self._setup_ui()

        # Configurar notificaciones
        self._setup_notifications()

        # Configurar atajos de teclado
        self.event_handlers.setup_keyboard_shortcuts()

        # Cargar datos
        self._load_data()

        # Auto-refresh si está habilitado
        if UI_CONFIG.get('auto_refresh', True):
            self._start_auto_refresh()

    def _setup_theme(self):
        """Configura el tema visual"""
        theme_manager.configure_ttk_styles()
        theme_manager.apply_theme_to_widget(self.root)

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panel superior - Estadísticas mejorado
        self.stats_panel = EnhancedStatsPanel(main_frame)
        self.stats_panel.pack(fill=tk.X, pady=(0, 10))

        # Panel de controles mejorado
        self._create_enhanced_controls_panel(main_frame)

        # Panel de tabla mejorado
        self._create_enhanced_table_panel(main_frame)

        # Barra de estado mejorada
        self._create_enhanced_status_bar()

    def _setup_notifications(self):
        """Configura el sistema de notificaciones"""
        if NOTIFICATIONS_CONFIG.get('enabled', True):
            self.notification_manager = NotificationManager(self.db_manager, self.root)
            self.notification_manager.add_callback(self._on_notifications_received)
            self.notification_manager.start()
        else:
            self.notification_manager = None

    def _setup_keyboard_shortcuts(self):
        """Configura atajos de teclado"""
        if not UI_CONFIG.get('enable_keyboard_shortcuts', True):
            return

        # Los atajos de teclado ahora se manejan en event_handlers
        self.root.bind('<Control-f>', lambda e: self.search_box.search_entry.focus())
        self.root.bind('<Control-r>', lambda e: self._refresh_data())
        self.root.bind('<F5>', lambda e: self._refresh_data())
        self.root.bind('<Escape>', lambda e: self._clear_selection())

    def _start_auto_refresh(self):
        """Inicia el auto-refresh de datos"""
        interval = UI_CONFIG.get('refresh_interval', 60) * 1000  # Convertir a ms
        self.root.after(interval, self._auto_refresh_callback)

    def _auto_refresh_callback(self):
        """Callback para auto-refresh"""
        try:
            self._refresh_data()
        except Exception as e:
            print(f"Error en auto-refresh: {e}")
        finally:
            # Programar siguiente refresh
            if UI_CONFIG.get('auto_refresh', True):
                self._start_auto_refresh()

    def _create_enhanced_controls_panel(self, parent):
        """Crea el panel de controles mejorado"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Frame izquierdo - Búsqueda mejorada
        left_frame = ttk.Frame(controls_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Caja de búsqueda mejorada
        self.search_box = SearchBox(left_frame, self._on_search_change)
        self.search_box.pack(side=tk.LEFT, padx=(0, 15))

        # Filtros mejorados
        filters_frame = ttk.LabelFrame(left_frame, text="Filtros", padding=5)
        filters_frame.pack(side=tk.LEFT, padx=(0, 10))

        # Filtro por tipo
        ttk.Label(filters_frame, text="Tipo:", style='Small.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.tipo_filter = ttk.Combobox(filters_frame, width=12, state="readonly", font=theme_manager.get_font('small'))
        self.tipo_filter.grid(row=0, column=1, padx=(0, 10))
        self.tipo_filter['values'] = ['Todos'] + [tipo.value for tipo in TipoServicio]
        self.tipo_filter.set('Todos')
        self.tipo_filter.bind('<<ComboboxSelected>>', self._on_filter_change)

        # Filtro por estado
        ttk.Label(filters_frame, text="Estado:", style='Small.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.estado_filter = ttk.Combobox(filters_frame, width=12, state="readonly", font=theme_manager.get_font('small'))
        self.estado_filter.grid(row=0, column=3)
        self.estado_filter['values'] = ['Todos', 'Pendiente', 'Pagado', 'Vencido', 'En Riesgo de Corte']
        self.estado_filter.set('Todos')
        self.estado_filter.bind('<<ComboboxSelected>>', self._on_filter_change)

        # Frame derecho - Botones mejorados
        right_frame = ttk.Frame(controls_frame)
        right_frame.pack(side=tk.RIGHT)

        # Botones de acción principales
        action_frame = ttk.LabelFrame(right_frame, text="Acciones", padding=5)
        action_frame.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(action_frame, text="➕ Nueva", style='Action.TButton',
                  command=self.crud_operations.nueva_cuenta).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(action_frame, text="✏️ Editar",
                  command=self.crud_operations.editar_cuenta).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(action_frame, text="🗑️ Eliminar", style='Error.TButton',
                  command=self.crud_operations.eliminar_cuenta).grid(row=0, column=2, padx=2, pady=2)
        ttk.Button(action_frame, text="✅ Pagado", style='Success.TButton',
                  command=self.crud_operations.marcar_pagado).grid(row=0, column=3, padx=2, pady=2)

        # Menú de reportes mejorado
        reports_frame = ttk.LabelFrame(right_frame, text="Reportes", padding=5)
        reports_frame.pack(side=tk.LEFT, padx=(0, 10))

        reports_menu = tk.Menubutton(reports_frame, text="📊 Generar", relief=tk.RAISED)
        reports_menu.pack()

        reports_submenu = tk.Menu(reports_menu, tearoff=0)
        reports_submenu.add_command(label="📅 Reporte Mensual", command=self._generar_reporte_mensual)
        reports_submenu.add_command(label="📆 Reporte Anual", command=self._generar_reporte_anual)
        reports_submenu.add_command(label="📋 Reporte por Tipo", command=self._generar_reporte_por_tipo)
        reports_submenu.add_separator()
        reports_submenu.add_command(label="📈 Gráfico Mensual", command=self._generar_grafico_mensual)
        reports_submenu.add_command(label="🥧 Gráfico por Tipo", command=self._generar_grafico_tipo)

        reports_menu.config(menu=reports_submenu)

        # Botón de gráficos interactivos
        graphics_frame = ttk.LabelFrame(right_frame, text="Visualización", padding=5)
        graphics_frame.pack(side=tk.LEFT)

        ttk.Button(graphics_frame, text="📊 Gráficos", style='Action.TButton',
                  command=self._show_graphics_window).pack()

    def _create_enhanced_table_panel(self, parent):
        """Crea el panel de tabla mejorado"""
        table_frame = ttk.LabelFrame(parent, text="📋 Cuentas de Servicios", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Tabla mejorada
        self.enhanced_table = EnhancedCuentaTable(table_frame)
        self.enhanced_table.pack(fill=tk.BOTH, expand=True)

        # Configurar callbacks
        self.enhanced_table.on_double_click = self._on_table_double_click
        self.enhanced_table.on_right_click = self._on_table_right_click
        self.enhanced_table.on_edit = self._editar_cuenta
        self.enhanced_table.on_delete = self._eliminar_cuenta

        # Mantener referencia al tree para compatibilidad
        self.tree = self.enhanced_table.tree

    def _create_enhanced_status_bar(self):
        """Crea la barra de estado mejorada"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)

        # Separador
        ttk.Separator(status_frame, orient='horizontal').pack(fill=tk.X, pady=(0, 2))

        # Frame interno para elementos de estado
        inner_frame = ttk.Frame(status_frame)
        inner_frame.pack(fill=tk.X)

        # Mensaje de estado principal
        self.status_label = ttk.Label(inner_frame, text="Listo",
                                     font=theme_manager.get_font('small'))
        self.status_label.pack(side=tk.LEFT)

        # Indicador de notificaciones
        if NOTIFICATIONS_CONFIG.get('enabled', True):
            self.notification_indicator = NotificationIndicator(inner_frame)
            self.notification_indicator.pack(side=tk.RIGHT, padx=(0, 10))

        # Información de conexión de BD
        conn_info = self.db_manager.get_connection_info()
        db_label = ttk.Label(inner_frame,
                            text=f"BD: {conn_info['type']}",
                            font=theme_manager.get_font('small'))
        db_label.pack(side=tk.RIGHT, padx=(0, 10))

        # Hora de última actualización
        self.last_update_label = ttk.Label(inner_frame,
                                          text="",
                                          font=theme_manager.get_font('small'))
        self.last_update_label.pack(side=tk.RIGHT, padx=(0, 10))

    def _load_data(self):
        """Carga los datos desde la base de datos"""
        try:
            self.cuentas_actuales = self.db_manager.obtener_todas_las_cuentas()
            self._update_table()
            self._update_stats()
            self._update_status(f"Cargadas {len(self.cuentas_actuales)} cuentas")
            self._update_last_refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")
            self._update_status("Error al cargar datos")

    def _refresh_data(self):
        """Refresca los datos"""
        self._load_data()

    def _update_status(self, message: str):
        """Actualiza el mensaje de estado"""
        self.status_label.config(text=message)

    def _update_last_refresh(self):
        """Actualiza la hora de última actualización"""
        now = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"Actualizado: {now}")

    def _clear_selection(self):
        """Limpia la selección actual"""
        self.selected_cuenta = None
        if hasattr(self, 'enhanced_table'):
            self.enhanced_table.selected_cuenta = None

    def _update_table(self):
        """Actualiza la tabla con las cuentas filtradas"""
        # Aplicar filtros
        cuentas_filtradas = self._apply_filters()

        # Actualizar tabla mejorada
        if hasattr(self, 'enhanced_table'):
            self.enhanced_table.update_cuentas(cuentas_filtradas)
        else:
            # Fallback para compatibilidad
            self._update_legacy_table(cuentas_filtradas)

    def _update_legacy_table(self, cuentas_filtradas):
        """Actualiza tabla legacy (para compatibilidad)"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Agregar cuentas a la tabla
        for cuenta in cuentas_filtradas:
            estado = cuenta.get_estado()
            dias_vencer = cuenta.dias_para_vencer() if not cuenta.pagado else 0

            # Formatear fechas opcionales
            fecha_corte = format_date(cuenta.fecha_corte) if cuenta.fecha_corte else "-"
            fecha_lectura = format_date(getattr(cuenta, 'fecha_lectura_proxima', None)) if hasattr(cuenta, 'fecha_lectura_proxima') and cuenta.fecha_lectura_proxima else "-"

            # Truncar observaciones para la tabla
            observaciones_truncadas = cuenta.observaciones[:30] + "..." if len(cuenta.observaciones) > 30 else cuenta.observaciones if cuenta.observaciones else "-"

            values = (
                cuenta.tipo_servicio.value,
                cuenta.descripcion[:30] + "..." if len(cuenta.descripcion) > 30 else cuenta.descripcion,
                format_currency(cuenta.monto),
                format_date(cuenta.fecha_emision),
                format_date(cuenta.fecha_vencimiento),
                fecha_corte,
                fecha_lectura,
                estado.value,
                str(dias_vencer) if dias_vencer > 0 else "-",
                observaciones_truncadas
            )

            self.tree.insert('', tk.END, values=values)

    def _apply_filters(self) -> List[CuentaServicio]:
        """Aplica los filtros actuales"""
        cuentas = self.cuentas_actuales.copy()

        # Filtro de búsqueda
        if self.filtro_actual:
            cuentas = [c for c in cuentas if
                      self.filtro_actual.lower() in c.descripcion.lower() or
                      self.filtro_actual.lower() in c.tipo_servicio.value.lower() or
                      self.filtro_actual.lower() in c.observaciones.lower()]

        # Filtro por tipo
        tipo_seleccionado = self.tipo_filter.get()
        if tipo_seleccionado != 'Todos':
            cuentas = [c for c in cuentas if c.tipo_servicio.value == tipo_seleccionado]

        # Filtro por estado
        estado_seleccionado = self.estado_filter.get()
        if estado_seleccionado != 'Todos':
            cuentas = [c for c in cuentas if c.get_estado().value == estado_seleccionado]

        # Ordenar por fecha de vencimiento
        cuentas.sort(key=lambda x: x.fecha_vencimiento)

        return cuentas

    def _update_stats(self):
        """Actualiza las estadísticas"""
        stats = self.db_manager.obtener_estadisticas_generales()
        self.stats_panel.update_stats(stats)

    def _on_search_change(self, search_text: str):
        """Maneja cambios en la búsqueda"""
        self.filtro_actual = search_text
        self._update_table()

    def _on_notifications_received(self, notifications: List[dict]):
        """Maneja notificaciones recibidas"""
        if hasattr(self, 'notification_indicator'):
            self.notification_indicator.update_count(len(notifications))

        # Actualizar estado si hay notificaciones críticas
        critical_count = sum(1 for n in notifications if n.get('type') == 'critical')
        if critical_count > 0:
            self._update_status(f"⚠️ {critical_count} cuenta(s) en riesgo de corte")

    def _on_table_double_click(self, cuenta: CuentaServicio):
        """Maneja doble click en tabla mejorada"""
        self.selected_cuenta = cuenta
        self._editar_cuenta()

    def _on_table_right_click(self, event, cuenta: CuentaServicio):
        """Maneja click derecho en tabla mejorada"""
        self.selected_cuenta = cuenta
        self._show_context_menu(event)

    def _on_filter_change(self, event=None):
        """Maneja cambios en los filtros"""
        self._update_table()

    def _on_double_click(self, event):
        """Maneja doble click en la tabla"""
        self._editar_cuenta()

    def _show_context_menu(self, event):
        """Muestra menú contextual mejorado"""
        if not self.selected_cuenta:
            return

        context_menu = tk.Menu(self.root, tearoff=0)

        # Opciones según estado de la cuenta
        if not self.selected_cuenta.pagado:
            context_menu.add_command(label="✅ Marcar como Pagado",
                                   command=self._marcar_pagado)
            context_menu.add_separator()

        context_menu.add_command(label="✏️ Editar", command=self._editar_cuenta)
        context_menu.add_command(label="📄 Ver Detalles", command=self._ver_detalles)
        context_menu.add_separator()
        context_menu.add_command(label="📊 Generar Reporte Individual",
                               command=self._generar_reporte_individual)
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ Eliminar", command=self._eliminar_cuenta)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _ver_detalles(self):
        """Muestra detalles de la cuenta seleccionada"""
        if not self.selected_cuenta:
            return

        # Crear ventana de detalles
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalles - {self.selected_cuenta.descripcion}")
        details_window.geometry("500x400")
        details_window.transient(self.root)

        # Contenido de detalles
        main_frame = ttk.Frame(details_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        cuenta = self.selected_cuenta

        # Información básica
        info_text = f"""
Tipo de Servicio: {cuenta.tipo_servicio.value}
Descripción: {cuenta.descripcion}
Monto: {format_currency(cuenta.monto)}
Estado: {cuenta.get_estado().value}

Fechas:
• Emisión: {format_date(cuenta.fecha_emision)}
• Vencimiento: {format_date(cuenta.fecha_vencimiento)}
• Corte: {format_date(cuenta.fecha_corte) if cuenta.fecha_corte else 'No especificada'}
• Pago: {format_date(cuenta.fecha_pago) if cuenta.fecha_pago else 'No pagada'}

Días para vencer: {cuenta.dias_para_vencer() if not cuenta.pagado else 'N/A'}

Observaciones:
{cuenta.observaciones or 'Sin observaciones'}
        """

        text_widget = tk.Text(main_frame, wrap=tk.WORD, font=theme_manager.get_font('default'))
        text_widget.insert('1.0', info_text.strip())
        text_widget.config(state='disabled')
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar",
                  command=details_window.destroy).pack(pady=(10, 0))

    def _generar_reporte_individual(self):
        """Genera reporte individual de la cuenta seleccionada"""
        if not self.selected_cuenta:
            return

        try:
            # Crear lista con una sola cuenta
            cuentas = [self.selected_cuenta]

            # Solicitar ubicación de guardado
            filename = f"reporte_individual_{self.selected_cuenta.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = filedialog.asksaveasfilename(
                title="Guardar Reporte Individual",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=filename
            )

            if filepath:
                final_path = self.report_generator.generar_reporte_por_tipo({
                    self.selected_cuenta.tipo_servicio.value: cuentas
                }, filepath)
                messagebox.showinfo("Éxito", f"Reporte individual generado: {final_path}")
            else:
                return

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte individual: {e}")

    def _get_selected_cuenta(self) -> Optional[CuentaServicio]:
        """Obtiene la cuenta seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return None

        item = selection[0]
        return self._get_cuenta_from_item(item)

    def _get_selected_cuentas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas seleccionadas"""
        selection = self.tree.selection()
        if not selection:
            return []

        cuentas = []
        for item in selection:
            cuenta = self._get_cuenta_from_item(item)
            if cuenta:
                cuentas.append(cuenta)

        return cuentas

    def _get_cuenta_from_item(self, item) -> Optional[CuentaServicio]:
        """Obtiene una cuenta desde un item del tree"""
        values = self.tree.item(item, 'values')
        if not values:
            return None

        try:
            # Usar descripción y monto como identificadores únicos más robustos
            descripcion_mostrada = values[1]  # Columna descripción
            monto_mostrado = values[2]        # Columna monto

            # Limpiar descripción truncada
            descripcion_limpia = descripcion_mostrada.replace("...", "").strip()

            # Limpiar formato de monto
            monto_limpio = monto_mostrado.replace("$", "").replace(".", "").replace(",", "")
            monto_valor = float(monto_limpio) if monto_limpio else 0

            # Buscar la cuenta que coincida
            for cuenta in self.cuentas_actuales:
                if (cuenta.descripcion.startswith(descripcion_limpia) or
                    descripcion_limpia in cuenta.descripcion) and cuenta.monto == monto_valor:
                    return cuenta

        except (ValueError, IndexError, AttributeError) as e:
            print(f"Error obteniendo cuenta del item: {e}")

            # Fallback: usar índice si falla la búsqueda por contenido
            try:
                all_items = self.tree.get_children()
                item_index = list(all_items).index(item)
                if 0 <= item_index < len(self.cuentas_actuales):
                    return self.cuentas_actuales[item_index]
            except (ValueError, IndexError):
                pass

        return None

    def _nueva_cuenta(self):
        """Abre diálogo para nueva cuenta"""
        dialog = CuentaDialog(self.root, "Nueva Cuenta")
        if dialog.result:
            cuenta = dialog.result
            errores = validar_cuenta(cuenta)

            if errores:
                messagebox.showerror("Error de Validación", "\n".join(errores))
                return

            try:
                self.db_manager.crear_cuenta(cuenta)
                self._load_data()
                messagebox.showinfo("Éxito", "Cuenta creada exitosamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear cuenta: {e}")

    def _editar_cuenta(self):
        """Abre diálogo para editar cuenta"""
        cuenta = self._get_selected_cuenta()
        if not cuenta:
            messagebox.showwarning("Advertencia", "Seleccione una cuenta para editar")
            return

        dialog = CuentaDialog(self.root, "Editar Cuenta", cuenta)
        if dialog.result:
            cuenta_editada = dialog.result
            cuenta_editada.id = cuenta.id  # Mantener el ID original

            errores = validar_cuenta(cuenta_editada)
            if errores:
                messagebox.showerror("Error de Validación", "\n".join(errores))
                return

            try:
                self.db_manager.actualizar_cuenta(cuenta_editada)
                self._load_data()
                messagebox.showinfo("Éxito", "Cuenta actualizada exitosamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al actualizar cuenta: {e}")

    def _eliminar_cuenta(self):
        """Elimina las cuentas seleccionadas"""
        cuentas_seleccionadas = self._get_selected_cuentas()
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
                        self.db_manager.eliminar_cuenta(cuenta.id)
                        eliminadas += 1
                    except Exception as e:
                        print(f"Error eliminando cuenta {cuenta.id}: {e}")
                        errores += 1

                self._load_data()

                # Mostrar resultado
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

    def _marcar_pagado(self):
        """Marca la cuenta seleccionada como pagada"""
        cuenta = self._get_selected_cuenta()
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
                self._load_data()
                messagebox.showinfo("Éxito", "Cuenta marcada como pagada")
            except Exception as e:
                messagebox.showerror("Error", f"Error al marcar cuenta como pagada: {e}")

    def _generar_reporte_mensual(self):
        """Genera reporte mensual"""
        # Diálogo mejorado para seleccionar mes y año
        dialog = tk.Toplevel(self.root)
        dialog.title("Generar Reporte Mensual")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Centrar diálogo
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")

        # Frame principal
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(main_frame, text="📊 Generar Reporte Mensual",
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 20))

        # Frame para selección
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 20))

        # Mes
        ttk.Label(selection_frame, text="Mes:", font=('Arial', 10)).grid(row=0, column=0, sticky='w', pady=5)
        mes_var = tk.StringVar(value=str(datetime.now().month))
        meses = ['1 - Enero', '2 - Febrero', '3 - Marzo', '4 - Abril', '5 - Mayo', '6 - Junio',
                '7 - Julio', '8 - Agosto', '9 - Septiembre', '10 - Octubre', '11 - Noviembre', '12 - Diciembre']
        mes_combo = ttk.Combobox(selection_frame, textvariable=mes_var, values=meses,
                                state="readonly", width=25)
        mes_combo.set(f"{datetime.now().month} - {meses[datetime.now().month-1].split(' - ')[1]}")
        mes_combo.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)

        # Año
        ttk.Label(selection_frame, text="Año:", font=('Arial', 10)).grid(row=1, column=0, sticky='w', pady=5)
        año_var = tk.StringVar(value=str(datetime.now().year))
        año_entry = ttk.Entry(selection_frame, textvariable=año_var, width=25)
        año_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)

        # Configurar columnas
        selection_frame.columnconfigure(1, weight=1)

        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        def generar():
            try:
                mes_texto = mes_var.get()
                mes = int(mes_texto.split(' - ')[0])
                año = int(año_var.get())

                # Mostrar progreso
                progress_dialog = ProgressDialog(dialog, "Generando Reporte",
                                               f"Generando reporte para {mes_texto.split(' - ')[1]} {año}...")
                progress_dialog.update_progress(25, "Obteniendo datos...")

                cuentas_mes = self.db_manager.obtener_cuentas_por_mes(mes, año)
                progress_dialog.update_progress(50, "Procesando cuentas...")

                if not cuentas_mes:
                    progress_dialog.close()
                    messagebox.showwarning("Sin Datos", f"No hay cuentas para {mes_texto.split(' - ')[1]} {año}")
                    return

                progress_dialog.update_progress(75, "Generando PDF...")

                # Solicitar ubicación de guardado
                filename = f"reporte_mensual_{año}_{mes:02d}.pdf"
                filepath = filedialog.asksaveasfilename(
                    title="Guardar Reporte Mensual",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=filename
                )

                if filepath:
                    final_path = self.report_generator.generar_reporte_mensual(cuentas_mes, mes, año, filepath)
                    progress_dialog.update_progress(100, "Completado")
                    progress_dialog.close()
                    messagebox.showinfo("Éxito", f"Reporte generado exitosamente:\n{final_path}")
                    dialog.destroy()
                else:
                    progress_dialog.close()

            except Exception as e:
                if 'progress_dialog' in locals():
                    progress_dialog.close()
                messagebox.showerror("Error", f"Error al generar reporte: {e}")

        def cancelar():
            dialog.destroy()

        # Botones
        ttk.Button(button_frame, text="Cancelar", command=cancelar).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="📊 Generar Reporte", style='Action.TButton',
                  command=generar).pack(side=tk.RIGHT)

    def _generar_reporte_anual(self):
        """Genera reporte anual"""
        año = tk.simpledialog.askinteger("Año", "Ingrese el año:", initialvalue=datetime.now().year)
        if año:
            try:
                resumenes = []
                for mes in range(1, 13):
                    resumen = self.db_manager.obtener_resumen_mensual(mes, año)
                    resumenes.append(resumen)

                # Solicitar ubicación de guardado
                filename = f"reporte_anual_{año}.pdf"
                filepath = filedialog.asksaveasfilename(
                    title="Guardar Reporte Anual",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialfile=filename
                )

                if filepath:
                    final_path = self.report_generator.generar_reporte_anual(resumenes, año, filepath)
                    messagebox.showinfo("Éxito", f"Reporte generado: {final_path}")
                else:
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Error al generar reporte: {e}")

    def _generar_reporte_por_tipo(self):
        """Genera reporte por tipo de servicio"""
        try:
            cuentas_por_tipo = {}
            for tipo in TipoServicio:
                cuentas = self.db_manager.obtener_cuentas_por_tipo(tipo)
                if cuentas:
                    cuentas_por_tipo[tipo.value] = cuentas

            if not cuentas_por_tipo:
                messagebox.showwarning("Advertencia", "No hay cuentas para generar el reporte")
                return

            # Solicitar ubicación de guardado
            filename = f"reporte_por_tipo_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = filedialog.asksaveasfilename(
                title="Guardar Reporte por Tipo",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=filename
            )

            if filepath:
                final_path = self.report_generator.generar_reporte_por_tipo(cuentas_por_tipo, filepath)
                messagebox.showinfo("Éxito", f"Reporte generado: {final_path}")
            else:
                return

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")

    def _generar_grafico_mensual(self):
        """Genera gráfico de gastos mensuales"""
        año = tk.simpledialog.askinteger("Año", "Ingrese el año:", initialvalue=datetime.now().year)
        if año:
            try:
                resumenes = []
                for mes in range(1, 13):
                    resumen = self.db_manager.obtener_resumen_mensual(mes, año)
                    resumenes.append(resumen)

                # Solicitar ubicación de guardado
                filename = f"grafico_gastos_mensuales_{año}.png"
                filepath = filedialog.asksaveasfilename(
                    title="Guardar Gráfico Mensual",
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                    initialfile=filename
                )

                if filepath:
                    final_path = self.report_generator.crear_grafico_gastos_mensuales(resumenes, año, filepath)
                    messagebox.showinfo("Éxito", f"Gráfico generado: {final_path}")
                else:
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Error al generar gráfico: {e}")

    def _generar_grafico_tipo(self):
        """Genera gráfico por tipo de servicio"""
        try:
            totales_por_tipo = self.db_manager.obtener_total_por_tipo()

            if not totales_por_tipo:
                messagebox.showwarning("Advertencia", "No hay datos para generar el gráfico")
                return

            # Solicitar ubicación de guardado
            filename = f"grafico_por_tipo_{datetime.now().strftime('%Y%m%d')}.png"
            filepath = filedialog.asksaveasfilename(
                title="Guardar Gráfico por Tipo",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=filename
            )

            if filepath:
                final_path = self.report_generator.crear_grafico_por_tipo(totales_por_tipo, filepath)
                messagebox.showinfo("Éxito", f"Gráfico generado: {final_path}")
            else:
                return

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráfico: {e}")

    def _show_graphics_window(self):
        """Muestra la ventana de gráficos interactivos"""
        try:
            if self.graphics_window is None or not self.graphics_window.window.winfo_exists():
                self.graphics_window = GraphicsWindow(self.root, self.db_manager)
            else:
                self.graphics_window.show()
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo ventana de gráficos: {e}")

    def run(self):
        """Ejecuta la aplicación"""
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        try:
            self.root.mainloop()
        finally:
            self._cleanup()

    def _on_closing(self):
        """Maneja el cierre de la aplicación"""
        # Detener notificaciones
        if hasattr(self, 'notification_manager') and self.notification_manager:
            self.notification_manager.stop()

        # Cerrar ventana
        self.root.destroy()

    def _cleanup(self):
        """Limpia recursos al cerrar"""
        try:
            if hasattr(self, 'notification_manager') and self.notification_manager:
                self.notification_manager.stop()
        except Exception as e:
            print(f"Error en cleanup: {e}")