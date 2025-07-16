"""
Componente para mostrar gráficos y estadísticas de gastos
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import List, Dict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

from ...domain.entities import CuentaServicio, TipoServicio
from ...infrastructure.utils import formatear_moneda_clp_simple


class GraficosPanel:
    """Componente para mostrar gráficos y estadísticas"""

    def __init__(self, parent, gestionar_cuenta):
        self.parent = parent
        self.gestionar_cuenta = gestionar_cuenta

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del componente"""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        title_label = ttk.Label(self.main_frame, text="Gráficos y Estadísticas",
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))

        # Frame para controles
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        # Selector de tipo de gráfico
        ttk.Label(controls_frame, text="Tipo de Gráfico:").pack(side=tk.LEFT, padx=(0, 5))
        self.tipo_grafico_var = tk.StringVar(value="Gastos por Servicio")
        tipo_combo = ttk.Combobox(controls_frame, textvariable=self.tipo_grafico_var,
                                 values=["Gastos por Servicio", "Gastos por Mes", "Evolución Anual"],
                                 state="readonly", width=20)
        tipo_combo.pack(side=tk.LEFT, padx=(0, 10))
        tipo_combo.bind('<<ComboboxSelected>>', self.actualizar_grafico)

        # Botón actualizar
        ttk.Button(controls_frame, text="Actualizar",
                  command=self.actualizar_grafico).pack(side=tk.LEFT)

        # Frame para el gráfico
        self.grafico_frame = ttk.Frame(self.main_frame)
        self.grafico_frame.pack(fill=tk.BOTH, expand=True)

        # Crear figura de matplotlib
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, self.grafico_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Cargar gráfico inicial
        self.actualizar_grafico()

    def actualizar_grafico(self, event=None):
        """Actualiza el gráfico según el tipo seleccionado"""
        self.fig.clear()

        tipo = self.tipo_grafico_var.get()

        if tipo == "Gastos por Servicio":
            self.grafico_gastos_por_servicio()
        elif tipo == "Gastos por Mes":
            self.grafico_gastos_por_mes()
        elif tipo == "Evolución Anual":
            self.grafico_evolucion_anual()

        self.canvas.draw()

    def grafico_gastos_por_servicio(self):
        """Gráfico de gastos por tipo de servicio"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        # Calcular totales por servicio
        totales = {}
        for cuenta in cuentas:
            servicio = cuenta.tipo_servicio.value
            if servicio not in totales:
                totales[servicio] = 0
            totales[servicio] += cuenta.monto

        if not totales:
            self.mostrar_mensaje_sin_datos()
            return

        # Crear gráfico de torta
        ax = self.fig.add_subplot(111)
        servicios = list(totales.keys())
        montos = list(totales.values())
        colores = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']

        wedges, texts, autotexts = ax.pie(montos, labels=servicios, autopct='%1.1f%%',
                                         colors=colores, startangle=90)

        # Formatear etiquetas de porcentaje
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title('Distribución de Gastos por Servicio', fontsize=14, fontweight='bold')

        # Agregar leyenda con montos
        total_general = sum(montos)
        leyenda_textos = [f"{servicio}: {formatear_moneda_clp_simple(monto)}"
                         for servicio, monto in zip(servicios, montos)]
        leyenda_textos.append(f"Total: {formatear_moneda_clp_simple(total_general)}")

        ax.legend(wedges, leyenda_textos, title="Detalle", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    def grafico_gastos_por_mes(self):
        """Gráfico de gastos por mes"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        # Agrupar por mes
        gastos_por_mes = {}
        for cuenta in cuentas:
            mes_key = f"{cuenta.fecha_emision.year}-{cuenta.fecha_emision.month:02d}"
            if mes_key not in gastos_por_mes:
                gastos_por_mes[mes_key] = 0
            gastos_por_mes[mes_key] += cuenta.monto

        if not gastos_por_mes:
            self.mostrar_mensaje_sin_datos()
            return

        # Ordenar por fecha
        meses_ordenados = sorted(gastos_por_mes.keys())
        montos = [gastos_por_mes[mes] for mes in meses_ordenados]

        # Formatear etiquetas de meses
        etiquetas_meses = []
        for mes_key in meses_ordenados:
            año, mes = mes_key.split('-')
            etiquetas_meses.append(f"{mes}/{año}")

        # Crear gráfico de barras
        ax = self.fig.add_subplot(111)
        bars = ax.bar(etiquetas_meses, montos, color='skyblue', edgecolor='navy', alpha=0.7)

        # Agregar valores en las barras
        for bar, monto in zip(bars, montos):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(montos)*0.01,
                   formatear_moneda_clp_simple(monto), ha='center', va='bottom', fontsize=8)

        ax.set_title('Gastos por Mes', fontsize=14, fontweight='bold')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Monto (CLP)')
        ax.tick_params(axis='x', rotation=45)

        # Ajustar layout
        self.fig.tight_layout()

    def grafico_evolucion_anual(self):
        """Gráfico de evolución anual de gastos"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        # Agrupar por año y servicio
        gastos_por_año_servicio = {}
        for cuenta in cuentas:
            año = cuenta.fecha_emision.year
            servicio = cuenta.tipo_servicio.value

            if año not in gastos_por_año_servicio:
                gastos_por_año_servicio[año] = {}
            if servicio not in gastos_por_año_servicio[año]:
                gastos_por_año_servicio[año][servicio] = 0
            gastos_por_año_servicio[año][servicio] += cuenta.monto

        if not gastos_por_año_servicio:
            self.mostrar_mensaje_sin_datos()
            return

        # Crear gráfico de líneas
        ax = self.fig.add_subplot(111)

        años = sorted(gastos_por_año_servicio.keys())
        servicios = list(set([servicio for año_data in gastos_por_año_servicio.values()
                             for servicio in año_data.keys()]))

        colores = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc']

        for i, servicio in enumerate(servicios):
            montos = []
            for año in años:
                monto = gastos_por_año_servicio[año].get(servicio, 0)
                montos.append(monto)

            ax.plot(años, montos, marker='o', linewidth=2, markersize=6,
                   label=servicio, color=colores[i % len(colores)])

        ax.set_title('Evolución Anual de Gastos por Servicio', fontsize=14, fontweight='bold')
        ax.set_xlabel('Año')
        ax.set_ylabel('Monto (CLP)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Formatear eje Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: formatear_moneda_clp_simple(x)))

        # Ajustar layout
        self.fig.tight_layout()

    def mostrar_mensaje_sin_datos(self):
        """Muestra un mensaje cuando no hay datos para graficar"""
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No hay datos disponibles\npara generar el gráfico',
                ha='center', va='center', transform=ax.transAxes,
                fontsize=12, style='italic')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales de los gastos"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        if not cuentas:
            return {}

        total_general = sum(c.monto for c in cuentas)
        total_pagado = sum(c.monto for c in cuentas if c.pagado)
        total_pendiente = total_general - total_pagado

        # Promedio por cuenta
        promedio_por_cuenta = total_general / len(cuentas)

        # Cuenta más cara
        cuenta_mas_cara = max(cuentas, key=lambda x: x.monto)

        # Servicio más costoso
        gastos_por_servicio = {}
        for cuenta in cuentas:
            servicio = cuenta.tipo_servicio.value
            if servicio not in gastos_por_servicio:
                gastos_por_servicio[servicio] = 0
            gastos_por_servicio[servicio] += cuenta.monto

        servicio_mas_costoso = max(gastos_por_servicio.items(), key=lambda x: x[1])

        return {
            'total_general': total_general,
            'total_pagado': total_pagado,
            'total_pendiente': total_pendiente,
            'promedio_por_cuenta': promedio_por_cuenta,
            'cuenta_mas_cara': cuenta_mas_cara,
            'servicio_mas_costoso': servicio_mas_costoso,
            'total_cuentas': len(cuentas),
            'cuentas_pagadas': len([c for c in cuentas if c.pagado]),
            'cuentas_pendientes': len([c for c in cuentas if not c.pagado])
        }