"""
Componente de tabla de cuentas con filtros y estadísticas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Callable, Optional

from ...domain.entities import TipoServicio, CuentaServicio
from ...infrastructure.utils import formatear_moneda_clp_simple
from ..themes import theme_manager


class CuentaTable:
    """Componente de tabla para mostrar y gestionar cuentas"""

    def __init__(self, parent, gestionar_cuenta, on_cuenta_selected: Callable = None):
        self.parent = parent
        self.gestionar_cuenta = gestionar_cuenta
        self.on_cuenta_selected = on_cuenta_selected

        # Variables de filtros
        self.tipo_var = tk.StringVar(value="Todos")
        self.estado_var = tk.StringVar(value="Todos")

        # Variables de estadísticas
        self.total_pendiente_var = tk.StringVar(value="Total Pendiente: $0")
        self.total_pagado_var = tk.StringVar(value="Total Pagado: $0")
        self.cuentas_vencidas_var = tk.StringVar(value="Cuentas Vencidas: 0")
        self.cuentas_riesgo_var = tk.StringVar(value="En Riesgo de Corte: 0")

        # Variable para búsqueda
        self.busqueda_var = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del componente"""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        # Configurar grid responsive
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        self.setup_search_bar()
        self.setup_filters()
        self.setup_table()
        self.setup_stats()

    def setup_search_bar(self):
        """Configura la barra de búsqueda"""
        # Frame de búsqueda
        search_frame = ttk.Frame(self.main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 3))
        search_frame.columnconfigure(1, weight=1)

        # Label de búsqueda
        search_label = tk.Label(search_frame, text="🔍 Búsqueda rápida:")
        search_label.grid(row=0, column=0, padx=(0, 3), sticky="w")

        # Entry de búsqueda
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.busqueda_var,
            font=("Arial", 9),
            relief="flat",
            borderwidth=1
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 3))
        self.search_entry.bind('<KeyRelease>', self.aplicar_filtros)

        # Botón limpiar búsqueda
        clear_button = tk.Button(
            search_frame,
            text="✕",
            command=self.limpiar_busqueda,
            relief="flat",
            borderwidth=1,
            width=3,
            cursor="hand2"
        )
        clear_button.grid(row=0, column=2)

        # Aplicar tema
        theme_manager.apply_theme_to_widget(search_label)
        theme_manager.apply_theme_to_widget(self.search_entry)
        theme_manager.apply_theme_to_widget(clear_button)

    def setup_filters(self):
        """Configura el panel de filtros"""
        # Frame de filtros
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filtros", padding="3")
        filter_frame.grid(row=1, column=0, sticky="nw", padx=(0, 3))

        # Filtro por tipo
        tipo_label = tk.Label(filter_frame, text="Tipo de Servicio:")
        tipo_label.grid(row=0, column=0, sticky="w", pady=(0, 2))

        tipo_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.tipo_var,
            values=["Todos"] + [t.value for t in TipoServicio],
            state="readonly",
            width=12
        )
        tipo_combo.grid(row=1, column=0, sticky="ew", pady=(0, 3))
        tipo_combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)

        # Filtro por estado
        estado_label = tk.Label(filter_frame, text="Estado:")
        estado_label.grid(row=2, column=0, sticky="w", pady=(0, 2))

        estado_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.estado_var,
            values=["Todos", "Pendiente", "Pagado", "Vencido", "En Riesgo de Corte"],
            state="readonly",
            width=12
        )
        estado_combo.grid(row=3, column=0, sticky="ew", pady=(0, 3))
        estado_combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)

        # Botón limpiar filtros
        clear_filters_button = tk.Button(
            filter_frame,
            text="🔄 Limpiar Filtros",
            command=self.limpiar_filtros,
            relief="flat",
            borderwidth=1,
            cursor="hand2"
        )
        clear_filters_button.grid(row=4, column=0, pady=(3, 0), sticky="ew")

        # Aplicar tema
        theme_manager.apply_theme_to_widget(tipo_label)
        theme_manager.apply_theme_to_widget(estado_label)
        theme_manager.apply_theme_to_widget(clear_filters_button)

    def setup_table(self):
        """Configura la tabla de cuentas"""
        # Frame de tabla
        table_frame = ttk.Frame(self.main_frame)
        table_frame.grid(row=1, column=1, sticky="nsew")

        # Crear Treeview con columnas responsive
        columns = ('Servicio', 'Emisión', 'Vencimiento', 'Próxima Lectura', 'Fecha Corte', 'Monto', 'Estado', 'Descripción')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        # Configurar columnas con anchos responsive
        column_widths = {
            'Servicio': 100,
            'Emisión': 80,
            'Vencimiento': 80,
            'Próxima Lectura': 100,
            'Fecha Corte': 80,
            'Monto': 100,
            'Estado': 120,
            'Descripción': 200
        }

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c))
            self.tree.column(col, width=column_widths[col], minwidth=50)

        # Variables para ordenamiento
        self.orden_actual = None
        self.columna_orden = None

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Grid de tabla y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Eventos
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_change)

        # Menú contextual
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="✏️ Editar", command=self.on_edit_requested)
        self.context_menu.add_command(label="✅ Marcar como Pagada", command=self.on_mark_paid_requested)
        self.context_menu.add_command(label="📋 Ver Historial", command=self.on_ver_historial_requested)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Eliminar", command=self.on_delete_requested)

        self.tree.bind('<Button-3>', self.mostrar_menu_contextual)

        # Configurar estilos de colores
        self._configurar_estilos()

    def setup_stats(self):
        """Configura el panel de estadísticas"""
        # Frame de estadísticas
        stats_frame = ttk.LabelFrame(self.main_frame, text="📊 Estadísticas", padding="3")
        stats_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(3, 0))

        # Grid para estadísticas
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        # Labels de estadísticas con iconos
        stats_data = [
            (self.total_pendiente_var, "💰", 0),
            (self.total_pagado_var, "✅", 1),
            (self.cuentas_vencidas_var, "⚠️", 2),
            (self.cuentas_riesgo_var, "🔴", 3)
        ]

        for var, icon, col in stats_data:
            label = tk.Label(
                stats_frame,
                textvariable=var,
                font=("Arial", 9, "bold"),
                anchor="center"
            )
            label.grid(row=0, column=col, padx=2, pady=2, sticky="ew")

            # Aplicar tema
            theme_manager.apply_theme_to_widget(label)

    def limpiar_busqueda(self):
        """Limpia el campo de búsqueda"""
        self.busqueda_var.set("")
        self.aplicar_filtros()

    def cargar_cuentas(self):
        """Carga todas las cuentas en la tabla"""
        self.limpiar_tabla()
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
        self.mostrar_cuentas(cuentas)
        self.actualizar_estadisticas()

    def mostrar_cuentas(self, cuentas: List[CuentaServicio]):
        """Muestra las cuentas en la tabla"""
        for cuenta in cuentas:
            estado = cuenta.get_estado()
            # Formatear fechas opcionales
            proxima_lectura = cuenta.fecha_proxima_lectura.strftime('%d/%m/%Y') if cuenta.fecha_proxima_lectura else "-"
            fecha_corte = cuenta.fecha_corte.strftime('%d/%m/%Y') if cuenta.fecha_corte else "-"

            # Determinar tags para colores
            tags = [cuenta.id]
            if cuenta.pagado:
                tags.append('pagado')
            elif cuenta.esta_vencida():
                tags.append('vencido')
            elif cuenta.esta_en_riesgo_corte():
                tags.append('riesgo')
            else:
                tags.append('pendiente')

            self.tree.insert('', 'end', values=(
                cuenta.tipo_servicio.value,
                cuenta.fecha_emision.strftime('%d/%m/%Y'),
                cuenta.fecha_vencimiento.strftime('%d/%m/%Y'),
                proxima_lectura,
                fecha_corte,
                formatear_moneda_clp_simple(cuenta.monto),
                estado,
                cuenta.descripcion
            ), tags=tags)

    def limpiar_tabla(self):
        """Limpia la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def aplicar_filtros(self, event=None):
        """Aplica los filtros seleccionados"""
        self.limpiar_tabla()
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        # Filtrar por búsqueda
        busqueda = self.busqueda_var.get().lower().strip()
        if busqueda:
            cuentas = [c for c in cuentas if (
                busqueda in c.tipo_servicio.value.lower() or
                busqueda in c.descripcion.lower() or
                busqueda in str(int(c.monto)) or
                busqueda in formatear_moneda_clp_simple(c.monto).lower()
            )]

        # Filtrar por tipo
        if self.tipo_var.get() != "Todos":
            tipo_filtro = TipoServicio(self.tipo_var.get())
            cuentas = [c for c in cuentas if c.tipo_servicio == tipo_filtro]

        # Filtrar por estado
        if self.estado_var.get() != "Todos":
            estado_filtro = self.estado_var.get()
            cuentas = [c for c in cuentas if c.get_estado() == estado_filtro]

        self.mostrar_cuentas(cuentas)
        self.actualizar_estadisticas()

    def limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.tipo_var.set("Todos")
        self.estado_var.set("Todos")
        self.busqueda_var.set("")
        self.aplicar_filtros()

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        total_pendiente = sum(c.monto for c in cuentas if not c.pagado)
        total_pagado = sum(c.monto for c in cuentas if c.pagado)
        cuentas_vencidas = len([c for c in cuentas if c.esta_vencida()])
        cuentas_riesgo = len([c for c in cuentas if c.esta_en_riesgo_corte()])

        self.total_pendiente_var.set(f"Total Pendiente: {formatear_moneda_clp_simple(total_pendiente)}")
        self.total_pagado_var.set(f"Total Pagado: {formatear_moneda_clp_simple(total_pagado)}")
        self.cuentas_vencidas_var.set(f"Cuentas Vencidas: {cuentas_vencidas}")
        self.cuentas_riesgo_var.set(f"En Riesgo de Corte: {cuentas_riesgo}")

    def obtener_cuenta_seleccionada(self) -> Optional[CuentaServicio]:
        """Obtiene la cuenta seleccionada en la tabla"""
        selection = self.tree.selection()
        if not selection:
            return None

        item_id = selection[0]
        cuenta_id = self.tree.item(item_id, 'tags')[0]
        return self.gestionar_cuenta.obtener_cuenta(cuenta_id)

    def on_double_click(self, event):
        """Maneja el doble clic en una fila"""
        if self.on_cuenta_selected:
            self.on_cuenta_selected()

    def on_selection_change(self, event):
        """Maneja el cambio de selección"""
        if self.on_cuenta_selected:
            self.on_cuenta_selected()

    def on_edit_requested(self):
        """Maneja la solicitud de edición desde el menú contextual"""
        if self.on_cuenta_selected:
            self.on_cuenta_selected()

    def on_mark_paid_requested(self):
        """Maneja la solicitud de marcar como pagada"""
        cuenta = self.obtener_cuenta_seleccionada()
        if cuenta and not cuenta.pagado:
            try:
                self.gestionar_cuenta.marcar_como_pagada(cuenta.id)
                self.refresh()
                messagebox.showinfo("Éxito", "Cuenta marcada como pagada")
            except Exception as e:
                messagebox.showerror("Error", f"Error al marcar como pagada: {str(e)}")

    def on_ver_historial_requested(self):
        """Maneja la solicitud de ver historial"""
        cuenta = self.obtener_cuenta_seleccionada()
        if cuenta:
            # Aquí se mostraría el diálogo de historial
            messagebox.showinfo("Historial", f"Historial de cambios para {cuenta.tipo_servicio.value}")

    def on_delete_requested(self):
        """Maneja la solicitud de eliminación"""
        cuenta = self.obtener_cuenta_seleccionada()
        if cuenta:
            if messagebox.askyesno("Confirmar", f"¿Eliminar cuenta de {cuenta.tipo_servicio.value}?"):
                try:
                    self.gestionar_cuenta.eliminar_cuenta(cuenta.id)
                    self.refresh()
                    messagebox.showinfo("Éxito", "Cuenta eliminada")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def ordenar_por_columna(self, columna):
        """Ordena la tabla por la columna especificada"""
        # Obtener datos actuales
        items = [(self.tree.set(item, columna), item) for item in self.tree.get_children('')]

        # Determinar orden
        if self.columna_orden == columna:
            self.orden_actual = not self.orden_actual
        else:
            self.orden_actual = True
            self.columna_orden = columna

        # Ordenar
        items.sort(key=lambda x: self._convertir_para_ordenar(x[0], columna), reverse=not self.orden_actual)

        # Reordenar en la tabla
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

        # Actualizar encabezados
        self._actualizar_encabezado_orden(columna)

    def _convertir_para_ordenar(self, valor, columna):
        """Convierte valores para ordenamiento correcto"""
        if columna == 'Monto':
            # Extraer número del formato de moneda
            try:
                return float(valor.replace('$', '').replace('.', '').replace(',', ''))
            except:
                return 0
        elif columna in ['Emisión', 'Vencimiento', 'Próxima Lectura', 'Fecha Corte']:
            # Convertir fecha
            try:
                return datetime.strptime(valor, '%d/%m/%Y')
            except:
                return datetime.min
        else:
            return valor.lower()

    def _configurar_estilos(self):
        """Configura los estilos de colores para la tabla"""
        style = ttk.Style()

        # Configurar colores para diferentes estados
        style.map('Treeview',
                 background=[('selected', '#007bff')],
                 foreground=[('selected', 'white')])

        # Configurar tags de colores
        self.tree.tag_configure('pagado', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('vencido', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('riesgo', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('pendiente', background='#f8f9fa', foreground='#6c757d')

    def _actualizar_encabezado_orden(self, columna):
        """Actualiza el encabezado para mostrar el orden"""
        # Limpiar todos los encabezados
        for col in self.tree['columns']:
            current_text = self.tree.heading(col)['text']
            if current_text.endswith(' ↑') or current_text.endswith(' ↓'):
                current_text = current_text[:-2]
            self.tree.heading(col, text=current_text)

        # Agregar indicador al encabezado actual
        current_text = self.tree.heading(columna)['text']
        indicator = ' ↑' if self.orden_actual else ' ↓'
        self.tree.heading(columna, text=current_text + indicator)

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def refresh(self):
        """Actualiza la tabla"""
        self.cargar_cuentas()

    def focus_search(self):
        """Enfoca el campo de búsqueda"""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def get_widget(self):
        """Retorna el widget principal del componente"""
        return self.main_frame