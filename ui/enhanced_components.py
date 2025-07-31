"""
Componentes mejorados de UI con mejor UX
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Optional, Callable, List, Dict, Any
import threading

from models import CuentaServicio, TipoServicio, validar_cuenta
from .themes import theme_manager, ThemedWidget
from .utils import format_currency, format_date


class EnhancedStatsPanel(ttk.Frame, ThemedWidget):
    """Panel de estadísticas mejorado con animaciones y colores"""

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        ThemedWidget.__init__(self, theme_manager)

        self.stats_data = {}
        self._create_widgets()
        self._setup_animations()

    def _create_widgets(self):
        """Crea los widgets del panel"""
        # Frame principal con estilo (simplificado)
        try:
            self.main_frame = ttk.LabelFrame(self, text="📊 Resumen General",
                                            style='Stats.TLabelFrame', padding=15)
        except tk.TclError:
            # Fallback si el estilo no está disponible
            self.main_frame = ttk.LabelFrame(self, text="📊 Resumen General", padding=15)

        self.main_frame.pack(fill=tk.X, pady=(0, 10))

        # Grid de estadísticas
        self.stats_grid = ttk.Frame(self.main_frame)
        self.stats_grid.pack(fill=tk.X)

        # Crear cards de estadísticas
        self.cards = {}
        self._create_stat_cards()

    def _create_stat_cards(self):
        """Crea las tarjetas de estadísticas"""
        stats_config = [
            {
                'key': 'total_cuentas',
                'title': 'Total Cuentas',
                'icon': '📋',
                'color': 'accent',
                'row': 0, 'col': 0
            },
            {
                'key': 'total_gastos',
                'title': 'Total Gastos',
                'icon': '💰',
                'color': 'accent',
                'format': 'currency',
                'row': 0, 'col': 1
            },
            {
                'key': 'cuentas_pagadas',
                'title': 'Pagadas',
                'icon': '✅',
                'color': 'success',
                'row': 0, 'col': 2
            },
            {
                'key': 'total_pagado',
                'title': 'Total Pagado',
                'icon': '💚',
                'color': 'success',
                'format': 'currency',
                'row': 1, 'col': 0
            },
            {
                'key': 'cuentas_pendientes',
                'title': 'Pendientes',
                'icon': '⏳',
                'color': 'warning',
                'row': 1, 'col': 1
            },
            {
                'key': 'total_pendiente',
                'title': 'Total Pendiente',
                'icon': '🟡',
                'color': 'warning',
                'format': 'currency',
                'row': 1, 'col': 2
            },
            {
                'key': 'cuentas_vencidas',
                'title': 'Vencidas',
                'icon': '❌',
                'color': 'error',
                'row': 2, 'col': 0
            }
        ]

        for config in stats_config:
            card = self._create_stat_card(config)
            self.cards[config['key']] = card

    def _create_stat_card(self, config: Dict[str, Any]) -> ttk.Frame:
        """Crea una tarjeta de estadística individual"""
        # Frame de la tarjeta
        card_frame = ttk.Frame(self.stats_grid, style='TFrame', padding=8)
        card_frame.grid(row=config['row'], column=config['col'],
                       padx=5, pady=5, sticky='ew')

        # Configurar peso de columnas
        self.stats_grid.columnconfigure(config['col'], weight=1)

        # Icono y título
        header_frame = ttk.Frame(card_frame)
        header_frame.pack(fill=tk.X)

        icon_label = ttk.Label(header_frame, text=config['icon'],
                              font=theme_manager.get_font('large'))
        icon_label.pack(side=tk.LEFT)

        title_label = ttk.Label(header_frame, text=config['title'],
                               font=theme_manager.get_font('small'))
        title_label.pack(side=tk.LEFT, padx=(5, 0))

        # Valor
        value_label = ttk.Label(card_frame, text="0",
                               font=theme_manager.get_font('heading'))
        value_label.pack(anchor=tk.W, pady=(2, 0))

        # Guardar referencias
        card_frame.value_label = value_label
        card_frame.config = config

        return card_frame

    def _setup_animations(self):
        """Configura las animaciones"""
        self.animation_queue = []
        self.animating = False

    def update_stats(self, stats: Dict[str, Any]):
        """Actualiza las estadísticas con animación"""
        self.stats_data = stats

        for key, card in self.cards.items():
            if key in stats:
                new_value = stats[key]
                self._animate_value_change(card, new_value)

    def _animate_value_change(self, card: ttk.Frame, new_value: Any):
        """Anima el cambio de valor en una tarjeta"""
        config = card.config

        # Formatear valor
        if config.get('format') == 'currency':
            display_value = format_currency(new_value)
        else:
            display_value = str(new_value)

        # Actualizar valor (sin animación por ahora, se puede mejorar)
        card.value_label.config(text=display_value)

        # Cambiar color según el tipo
        color_name = config.get('color', 'fg')
        try:
            color = theme_manager.get_color(color_name)
            card.value_label.config(foreground=color)
        except:
            pass


class EnhancedCuentaTable(ttk.Frame, ThemedWidget):
    """Tabla de cuentas mejorada con colores y funcionalidades"""

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        ThemedWidget.__init__(self, theme_manager)

        self.cuentas = []
        self.selected_cuenta = None
        self.sort_column = None
        self.sort_reverse = False

        self._create_widgets()
        self._setup_events()

    def _create_widgets(self):
        """Crea los widgets de la tabla"""
        # Frame contenedor
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        # Crear Treeview con estilo mejorado y selección múltiple
        columns = ('tipo', 'descripcion', 'monto', 'emision', 'vencimiento', 'corte', 'lectura', 'estado', 'dias', 'observaciones')
        self.tree = ttk.Treeview(container, columns=columns, show='headings', height=15, selectmode='extended')

        # Configurar columnas con mejor formato
        column_config = {
            'tipo': {'text': 'Tipo', 'width': 80, 'anchor': 'center'},
            'descripcion': {'text': 'Descripción', 'width': 200, 'anchor': 'w'},
            'monto': {'text': 'Monto (CLP)', 'width': 100, 'anchor': 'e'},
            'emision': {'text': 'Emisión', 'width': 90, 'anchor': 'center'},
            'vencimiento': {'text': 'Vencimiento', 'width': 90, 'anchor': 'center'},
            'corte': {'text': 'Corte', 'width': 90, 'anchor': 'center'},
            'lectura': {'text': 'Próx. Lectura', 'width': 90, 'anchor': 'center'},
            'estado': {'text': 'Estado', 'width': 100, 'anchor': 'center'},
            'dias': {'text': 'Días p/vencer', 'width': 80, 'anchor': 'center'},
            'observaciones': {'text': 'Observaciones', 'width': 200, 'anchor': 'w'}
        }

        for col, config in column_config.items():
            self.tree.heading(col, text=config['text'],
                             command=lambda c=col: self._sort_by_column(c))
            self.tree.column(col, width=config['width'], anchor=config['anchor'])

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack elementos
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _setup_events(self):
        """Configura los eventos de la tabla"""
        self.tree.bind('<ButtonRelease-1>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)
        self.tree.bind('<Key>', self._on_key_press)

    def _sort_by_column(self, column: str):
        """Ordena la tabla por columna"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self._update_display()

        # Actualizar indicador de ordenamiento en header
        for col in self.tree['columns']:
            if col == column:
                direction = '↓' if self.sort_reverse else '↑'
                text = self.tree.heading(col)['text']
                if '↑' in text or '↓' in text:
                    text = text[:-2]
                self.tree.heading(col, text=f"{text} {direction}")
            else:
                text = self.tree.heading(col)['text']
                if '↑' in text or '↓' in text:
                    text = text[:-2]
                self.tree.heading(col, text=text)

    def _on_select(self, event):
        """Maneja selección de fila"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Encontrar cuenta correspondiente
            values = self.tree.item(item, 'values')
            self.selected_cuenta = self._find_cuenta_by_values(values)

    def _on_double_click(self, event):
        """Maneja doble click"""
        if hasattr(self, 'on_double_click') and self.selected_cuenta:
            self.on_double_click(self.selected_cuenta)

    def _on_right_click(self, event):
        """Maneja click derecho"""
        if hasattr(self, 'on_right_click'):
            self.on_right_click(event, self.selected_cuenta)

    def _on_key_press(self, event):
        """Maneja teclas presionadas"""
        if event.keysym == 'Delete' and self.selected_cuenta:
            if hasattr(self, 'on_delete'):
                self.on_delete(self.selected_cuenta)
        elif event.keysym == 'Return' and self.selected_cuenta:
            if hasattr(self, 'on_edit'):
                self.on_edit(self.selected_cuenta)

    def update_cuentas(self, cuentas: List[CuentaServicio]):
        """Actualiza las cuentas mostradas"""
        self.cuentas = cuentas
        self._update_display()

    def _update_display(self):
        """Actualiza la visualización de la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ordenar cuentas si es necesario
        cuentas_ordenadas = self._sort_cuentas()

        # Agregar cuentas
        for cuenta in cuentas_ordenadas:
            self._add_cuenta_to_tree(cuenta)

    def _sort_cuentas(self) -> List[CuentaServicio]:
        """Ordena las cuentas según la configuración actual"""
        if not self.sort_column:
            return self.cuentas

        def get_sort_key(cuenta: CuentaServicio):
            if self.sort_column == 'tipo':
                return cuenta.tipo_servicio.value
            elif self.sort_column == 'descripcion':
                return cuenta.descripcion.lower()
            elif self.sort_column == 'monto':
                return cuenta.monto
            elif self.sort_column == 'emision':
                return cuenta.fecha_emision
            elif self.sort_column == 'vencimiento':
                return cuenta.fecha_vencimiento
            elif self.sort_column == 'estado':
                return cuenta.get_estado().value
            elif self.sort_column == 'dias':
                return cuenta.dias_para_vencer()
            return 0

        return sorted(self.cuentas, key=get_sort_key, reverse=self.sort_reverse)

    def _add_cuenta_to_tree(self, cuenta: CuentaServicio):
        """Agrega una cuenta al árbol"""
        estado = cuenta.get_estado()
        dias_vencer = cuenta.dias_para_vencer() if not cuenta.pagado else 0

        # Formatear fechas opcionales
        fecha_corte = format_date(cuenta.fecha_corte) if cuenta.fecha_corte else "-"
        fecha_lectura = format_date(getattr(cuenta, 'fecha_lectura_proxima', None)) if hasattr(cuenta, 'fecha_lectura_proxima') and cuenta.fecha_lectura_proxima else "-"

        # Truncar observaciones para la tabla
        observaciones_truncadas = self._truncate_text(cuenta.observaciones, 30) if cuenta.observaciones else "-"

        values = (
            cuenta.tipo_servicio.value,
            self._truncate_text(cuenta.descripcion, 30),
            format_currency(cuenta.monto),
            format_date(cuenta.fecha_emision),
            format_date(cuenta.fecha_vencimiento),
            fecha_corte,
            fecha_lectura,
            estado.value,
            str(dias_vencer) if dias_vencer > 0 else "-",
            observaciones_truncadas
        )

        item = self.tree.insert('', tk.END, values=values)

        # Aplicar colores según estado
        self._apply_row_colors(item, estado.value)

    def _apply_row_colors(self, item: str, estado: str):
        """Aplica colores a una fila según su estado"""
        try:
            # Configurar tags por estado
            if estado == 'Pagado':
                self.tree.item(item, tags=('pagado',))
            elif estado == 'Vencido':
                self.tree.item(item, tags=('vencido',))
            elif estado == 'En Riesgo de Corte':
                self.tree.item(item, tags=('por_vencer',))
            else:  # Pendiente
                self.tree.item(item, tags=('pendiente',))

            # Configurar colores de tags
            self._configure_row_tags()
        except Exception as e:
            print(f"Error aplicando colores: {e}")

    def _configure_row_tags(self):
        """Configura los tags de colores para las filas"""
        try:
            # Obtener colores del tema actual
            theme = theme_manager.get_theme()
            colors = theme['colors']

            # Configurar tags con colores
            self.tree.tag_configure('pagado',
                                   foreground=colors.get('pagado', '#16c60c'))

            self.tree.tag_configure('vencido',
                                   foreground=colors.get('vencido', '#e74856'))

            self.tree.tag_configure('por_vencer',
                                   foreground=colors.get('por_vencer', '#ff8c00'))

            self.tree.tag_configure('pendiente',
                                   foreground=colors.get('pendiente', '#ffb900'))
        except Exception as e:
            print(f"Error configurando tags: {e}")

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Trunca texto si es muy largo"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

    def _find_cuenta_by_values(self, values: tuple) -> Optional[CuentaServicio]:
        """Encuentra una cuenta por sus valores mostrados"""
        descripcion_mostrada = values[1]
        monto_str = values[2].replace("$", "").replace(".", "").replace(",", "")

        try:
            monto = float(monto_str)
            for cuenta in self.cuentas:
                if (cuenta.descripcion.startswith(descripcion_mostrada.replace("...", "")) and
                    cuenta.monto == monto):
                    return cuenta
        except ValueError:
            pass

        return None


class ProgressDialog:
    """Diálogo de progreso para operaciones largas"""

    def __init__(self, parent, title: str, message: str):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Centrar diálogo
        self._center_dialog()

        # Variables
        self.cancelled = False
        self.progress_var = tk.DoubleVar()
        self.message_var = tk.StringVar(value=message)

        self._create_widgets()

    def _center_dialog(self):
        """Centra el diálogo en la ventana padre"""
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 200
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 75
        self.dialog.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Crea los widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Mensaje
        message_label = ttk.Label(main_frame, textvariable=self.message_var,
                                 font=theme_manager.get_font('default'))
        message_label.pack(pady=(0, 15))

        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame,
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=300)
        self.progress_bar.pack(pady=(0, 15))

        # Botón cancelar
        cancel_button = ttk.Button(main_frame, text="Cancelar",
                                  command=self._cancel)
        cancel_button.pack()

    def update_progress(self, value: float, message: str = None):
        """Actualiza el progreso"""
        self.progress_var.set(value)
        if message:
            self.message_var.set(message)
        self.dialog.update()

    def _cancel(self):
        """Cancela la operación"""
        self.cancelled = True
        self.close()

    def close(self):
        """Cierra el diálogo"""
        if self.dialog:
            self.dialog.destroy()


class SearchBox(ttk.Frame, ThemedWidget):
    """Caja de búsqueda mejorada con sugerencias"""

    def __init__(self, parent, on_search: Callable[[str], None]):
        ttk.Frame.__init__(self, parent)
        ThemedWidget.__init__(self, theme_manager)

        self.on_search = on_search
        self.search_var = tk.StringVar()
        self.suggestions = []

        self._create_widgets()
        self._setup_events()

    def _create_widgets(self):
        """Crea los widgets de búsqueda"""
        # Icono de búsqueda
        search_icon = ttk.Label(self, text="🔍",
                               font=theme_manager.get_font('default'))
        search_icon.pack(side=tk.LEFT, padx=(0, 5))

        # Campo de búsqueda
        self.search_entry = ttk.Entry(self, textvariable=self.search_var,
                                     font=theme_manager.get_font('default'),
                                     width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botón limpiar
        clear_button = ttk.Button(self, text="✕", width=3,
                                 command=self._clear_search)
        clear_button.pack(side=tk.LEFT, padx=(5, 0))

        # Placeholder
        self._set_placeholder("Buscar cuentas...")

    def _setup_events(self):
        """Configura los eventos"""
        self.search_var.trace('w', self._on_search_change)
        self.search_entry.bind('<FocusIn>', self._on_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_focus_out)
        self.search_entry.bind('<Return>', self._on_enter)

    def _set_placeholder(self, text: str):
        """Establece texto placeholder"""
        self.placeholder_text = text
        if not self.search_var.get():
            self.search_entry.config(foreground='gray')
            self.search_var.set(text)

    def _on_focus_in(self, event):
        """Maneja focus in"""
        if self.search_var.get() == self.placeholder_text:
            self.search_var.set("")
            self.search_entry.config(foreground=theme_manager.get_color('entry_fg'))

    def _on_focus_out(self, event):
        """Maneja focus out"""
        if not self.search_var.get():
            self._set_placeholder(self.placeholder_text)

    def _on_search_change(self, *args):
        """Maneja cambios en la búsqueda"""
        text = self.search_var.get()
        if text != self.placeholder_text:
            self.on_search(text)

    def _on_enter(self, event):
        """Maneja tecla Enter"""
        text = self.search_var.get()
        if text != self.placeholder_text:
            self.on_search(text)

    def _clear_search(self):
        """Limpia la búsqueda"""
        self.search_var.set("")
        self.search_entry.focus()
        self.on_search("")

    def set_suggestions(self, suggestions: List[str]):
        """Establece sugerencias de búsqueda"""
        self.suggestions = suggestions