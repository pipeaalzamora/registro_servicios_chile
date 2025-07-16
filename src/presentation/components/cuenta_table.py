"""
Componente de tabla de cuentas con filtros y estadísticas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import List, Callable, Optional

from ...domain.entities import TipoServicio, CuentaServicio
from ...infrastructure.utils import formatear_moneda_clp_simple


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

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del componente"""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Configurar grid
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.setup_filters()
        self.setup_table()

    def setup_filters(self):
        """Configura el panel de filtros y estadísticas"""
        # Frame de filtros
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filtros", padding="5")
        filter_frame.grid(row=0, column=0, sticky="nw", padx=(0, 10))

        # Búsqueda rápida
        ttk.Label(filter_frame, text="Búsqueda:").grid(row=0, column=0, sticky="w")
        self.busqueda_var = tk.StringVar()
        busqueda_entry = ttk.Entry(filter_frame, textvariable=self.busqueda_var, width=20)
        busqueda_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        busqueda_entry.bind('<KeyRelease>', self.aplicar_filtros)
        ttk.Label(filter_frame, text="(nombre, descripción, monto)").grid(row=0, column=2, sticky="w", padx=(5, 0))

        # Filtro por tipo
        ttk.Label(filter_frame, text="Tipo de Servicio:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tipo_combo = ttk.Combobox(filter_frame, textvariable=self.tipo_var,
                                 values=["Todos"] + [t.value for t in TipoServicio])
        tipo_combo.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(10, 0))
        tipo_combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)

        # Filtro por estado
        ttk.Label(filter_frame, text="Estado:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        estado_combo = ttk.Combobox(filter_frame, textvariable=self.estado_var,
                                   values=["Todos", "Pendiente", "Pagado", "Vencido", "En Riesgo de Corte"])
        estado_combo.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=(10, 0))
        estado_combo.bind('<<ComboboxSelected>>', self.aplicar_filtros)

        # Botón limpiar filtros
        ttk.Button(filter_frame, text="Limpiar Filtros",
                  command=self.limpiar_filtros).grid(row=3, column=0, columnspan=2, pady=(10, 0))

        # Frame de estadísticas
        stats_frame = ttk.LabelFrame(filter_frame, text="Estadísticas", padding="5")
        stats_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0), sticky="ew")

        ttk.Label(stats_frame, textvariable=self.total_pendiente_var).grid(row=0, column=0, sticky="w")
        ttk.Label(stats_frame, textvariable=self.total_pagado_var).grid(row=1, column=0, sticky="w")
        ttk.Label(stats_frame, textvariable=self.cuentas_vencidas_var).grid(row=2, column=0, sticky="w")
        ttk.Label(stats_frame, textvariable=self.cuentas_riesgo_var).grid(row=3, column=0, sticky="w")

    def setup_table(self):
        """Configura la tabla de cuentas"""
        # Frame de tabla
        table_frame = ttk.Frame(self.main_frame)
        table_frame.grid(row=0, column=1, sticky="nsew")

        # Crear Treeview
        columns = ('Servicio', 'Emisión', 'Vencimiento', 'Próxima Lectura', 'Fecha Corte', 'Monto', 'Estado', 'Descripción')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.ordenar_por_columna(c))
            self.tree.column(col, width=120)

        # Variables para ordenamiento
        self.orden_actual = None
        self.columna_orden = None

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Eventos
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_change)

        # Menú contextual
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="Editar", command=self.on_edit_requested)
        self.context_menu.add_command(label="Marcar como Pagada", command=self.on_mark_paid_requested)
        self.context_menu.add_command(label="Ver Historial", command=self.on_ver_historial_requested)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Eliminar", command=self.on_delete_requested)

        self.tree.bind('<Button-3>', self.mostrar_menu_contextual)

        # Configurar estilos de colores
        self._configurar_estilos()

    def cargar_cuentas(self):
        """Carga todas las cuentas en la tabla"""
        self.limpiar_tabla()
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
        self.mostrar_cuentas(cuentas)
        self.actualizar_estadisticas()

    def mostrar_cuentas(self, cuentas: List[CuentaServicio]):
        """Muestra las cuentas en la tabla"""
        for cuenta in cuentas:
            estado = "Pagado" if cuenta.pagado else "Pendiente"
            if cuenta.esta_vencida():
                estado = "Vencido"
            elif cuenta.esta_en_riesgo_corte():
                estado = "En Riesgo de Corte"

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
            if estado_filtro == "Pendiente":
                cuentas = [c for c in cuentas if not c.pagado and not c.esta_vencida() and not c.esta_en_riesgo_corte()]
            elif estado_filtro == "Pagado":
                cuentas = [c for c in cuentas if c.pagado]
            elif estado_filtro == "Vencido":
                cuentas = [c for c in cuentas if c.esta_vencida()]
            elif estado_filtro == "En Riesgo de Corte":
                cuentas = [c for c in cuentas if c.esta_en_riesgo_corte()]

        self.mostrar_cuentas(cuentas)

    def limpiar_filtros(self):
        """Limpia todos los filtros"""
        self.busqueda_var.set("")
        self.tipo_var.set("Todos")
        self.estado_var.set("Todos")
        self.cargar_cuentas()

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

        item = self.tree.item(selection[0])
        cuenta_id = item['tags'][0] if item['tags'] else None
        if cuenta_id:
            return self.gestionar_cuenta.obtener_cuenta(cuenta_id)
        return None

    def on_double_click(self, event):
        """Maneja el doble clic en la tabla"""
        if self.on_cuenta_selected:
            self.on_cuenta_selected()

    def on_selection_change(self, event):
        """Maneja el cambio de selección"""
        pass  # Para futuras implementaciones

    def on_edit_requested(self):
        """Callback para editar cuenta"""
        if self.on_cuenta_selected:
            self.on_cuenta_selected()

    def on_mark_paid_requested(self):
        """Callback para marcar como pagada"""
        cuenta = self.obtener_cuenta_seleccionada()
        if cuenta:
            if self.gestionar_cuenta.marcar_como_pagada(cuenta.id):
                messagebox.showinfo("Éxito", "Cuenta marcada como pagada")
                self.cargar_cuentas()
            else:
                messagebox.showerror("Error", "No se pudo marcar la cuenta como pagada")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta")

    def on_ver_historial_requested(self):
        """Callback para ver historial de cuenta"""
        cuenta = self.obtener_cuenta_seleccionada()
        if cuenta:
            from .historial_dialog import HistorialDialog
            dialog = HistorialDialog(self.parent, cuenta)
            dialog.show()
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta")

    def on_delete_requested(self):
        """Callback para eliminar cuenta"""
        cuenta = self.obtener_cuenta_seleccionada()
        if cuenta:
            if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar esta cuenta?"):
                if self.gestionar_cuenta.eliminar_cuenta(cuenta.id):
                    messagebox.showinfo("Éxito", "Cuenta eliminada")
                    self.cargar_cuentas()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la cuenta")
        else:
            messagebox.showwarning("Advertencia", "Por favor seleccione una cuenta")

    def ordenar_por_columna(self, columna):
        """Ordena la tabla por la columna especificada"""
        # Cambiar orden si es la misma columna
        if self.columna_orden == columna:
            self.orden_actual = not self.orden_actual if self.orden_actual is not None else False
        else:
            self.columna_orden = columna
            self.orden_actual = False  # Ascendente por defecto

        # Obtener datos actuales
        items = self.tree.get_children()
        if not items:
            return

        # Obtener datos de las filas
        datos = []
        for item in items:
            valores = self.tree.item(item)['values']
            datos.append((valores, item))

        # Ordenar datos
        datos_ordenados = self._ordenar_datos(datos, columna, self.orden_actual)

        # Reinsertar datos ordenados
        self.limpiar_tabla()
        for valores, _ in datos_ordenados:
            self.tree.insert('', 'end', values=valores, tags=valores[-1])  # El último valor es el ID

        # Actualizar encabezado con indicador de orden
        self._actualizar_encabezado_orden(columna)

    def _configurar_estilos(self):
        """Configura los estilos de colores para la tabla"""
        # Configurar colores para diferentes estados
        self.tree.tag_configure('pagado', background='#d4edda', foreground='#155724')  # Verde claro
        self.tree.tag_configure('vencido', background='#f8d7da', foreground='#721c24')  # Rojo claro
        self.tree.tag_configure('riesgo', background='#fff3cd', foreground='#856404')  # Amarillo claro
        self.tree.tag_configure('pendiente', background='#d1ecf1', foreground='#0c5460')  # Azul claro

    def _ordenar_datos(self, datos, columna, ascendente):
        """Ordena los datos según la columna especificada"""
        columna_index = {
            'Servicio': 0,
            'Emisión': 1,
            'Vencimiento': 2,
            'Próxima Lectura': 3,
            'Fecha Corte': 4,
            'Monto': 5,
            'Estado': 6,
            'Descripción': 7
        }

        index = columna_index.get(columna, 0)

        def key_func(item):
            valor = item[0][index]

            # Manejar casos especiales
            if columna in ['Emisión', 'Vencimiento', 'Próxima Lectura', 'Fecha Corte']:
                if valor == '-':
                    return datetime.min
                try:
                    return datetime.strptime(valor, '%d/%m/%Y')
                except:
                    return datetime.min
            elif columna == 'Monto':
                # Extraer número del formato de moneda
                try:
                    return float(valor.replace('$', '').replace(',', ''))
                except:
                    return 0.0
            else:
                return str(valor).lower()

        return sorted(datos, key=key_func, reverse=not ascendente)

    def _actualizar_encabezado_orden(self, columna):
        """Actualiza el encabezado para mostrar el orden actual"""
        # Limpiar todos los encabezados
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)

        # Agregar indicador de orden
        indicador = " ▲" if self.orden_actual else " ▼"
        self.tree.heading(columna, text=columna + indicador)

    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def refresh(self):
        """Actualiza la tabla"""
        self.cargar_cuentas()