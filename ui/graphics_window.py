"""
Ventana de gráficos para visualización de datos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import List, Dict

from models import CuentaServicio, TipoServicio
from database_manager import DatabaseManager
from .themes import theme_manager


class GraphicsWindow:
    """Ventana de gráficos y visualizaciones"""

    def __init__(self, parent, db_manager: DatabaseManager):
        self.parent = parent
        self.db_manager = db_manager

        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Gráficos y Estadísticas")
        self.window.geometry("1000x700")
        self.window.transient(parent)

        # Centrar ventana
        x = parent.winfo_x() + 50
        y = parent.winfo_y() + 50
        self.window.geometry(f"+{x}+{y}")

        # Configurar tema
        theme_manager.apply_theme_to_widget(self.window)

        self._setup_ui()
        self._load_initial_data()

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Panel de control
        self._create_control_panel(main_frame)

        # Notebook para diferentes gráficos
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Crear pestañas
        self._create_monthly_tab()
        self._create_type_tab()
        self._create_status_tab()
        self._create_trends_tab()

    def _create_control_panel(self, parent):
        """Crea el panel de controles"""
        control_frame = ttk.LabelFrame(parent, text="🎛️ Controles", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Frame para controles
        controls = ttk.Frame(control_frame)
        controls.pack(fill=tk.X)

        # Selector de año
        ttk.Label(controls, text="Año:").pack(side=tk.LEFT, padx=(0, 5))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_combo = ttk.Combobox(controls, textvariable=self.year_var, width=10, state="readonly")
        year_combo['values'] = [str(year) for year in range(2020, datetime.now().year + 2)]
        year_combo.pack(side=tk.LEFT, padx=(0, 20))
        year_combo.bind('<<ComboboxSelected>>', self._on_year_change)

        # Botón actualizar
        ttk.Button(controls, text="🔄 Actualizar", style='Action.TButton',
                  command=self._refresh_all_graphs).pack(side=tk.LEFT, padx=(0, 10))

        # Botón exportar
        ttk.Button(controls, text="💾 Exportar",
                  command=self._export_graphs).pack(side=tk.LEFT)

    def _create_monthly_tab(self):
        """Crea la pestaña de gráfico mensual"""
        self.monthly_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monthly_frame, text="📅 Gastos Mensuales")

        # Crear figura de matplotlib
        self.monthly_fig = Figure(figsize=(10, 6), dpi=100)
        self.monthly_fig.patch.set_facecolor(theme_manager.get_color('bg'))

        self.monthly_canvas = FigureCanvasTkAgg(self.monthly_fig, self.monthly_frame)
        self.monthly_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_type_tab(self):
        """Crea la pestaña de gráfico por tipo"""
        self.type_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.type_frame, text="🏷️ Por Tipo de Servicio")

        # Crear figura de matplotlib
        self.type_fig = Figure(figsize=(10, 6), dpi=100)
        self.type_fig.patch.set_facecolor(theme_manager.get_color('bg'))

        self.type_canvas = FigureCanvasTkAgg(self.type_fig, self.type_frame)
        self.type_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_status_tab(self):
        """Crea la pestaña de gráfico por estado"""
        self.status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.status_frame, text="📊 Por Estado")

        # Crear figura de matplotlib
        self.status_fig = Figure(figsize=(10, 6), dpi=100)
        self.status_fig.patch.set_facecolor(theme_manager.get_color('bg'))

        self.status_canvas = FigureCanvasTkAgg(self.status_fig, self.status_frame)
        self.status_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _create_trends_tab(self):
        """Crea la pestaña de tendencias"""
        self.trends_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trends_frame, text="📈 Tendencias")

        # Crear figura de matplotlib
        self.trends_fig = Figure(figsize=(10, 6), dpi=100)
        self.trends_fig.patch.set_facecolor(theme_manager.get_color('bg'))

        self.trends_canvas = FigureCanvasTkAgg(self.trends_fig, self.trends_frame)
        self.trends_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _load_initial_data(self):
        """Carga los datos iniciales"""
        self._refresh_all_graphs()

    def _on_year_change(self, event=None):
        """Maneja cambio de año"""
        self._refresh_all_graphs()

    def _refresh_all_graphs(self):
        """Actualiza todos los gráficos"""
        try:
            year = int(self.year_var.get())

            # Obtener datos
            all_accounts = self.db_manager.obtener_todas_las_cuentas()
            year_accounts = [acc for acc in all_accounts
                           if acc.fecha_emision.year == year]

            # Actualizar cada gráfico
            self._update_monthly_graph(year_accounts, year)
            self._update_type_graph(year_accounts)
            self._update_status_graph(all_accounts)
            self._update_trends_graph(all_accounts)

        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando gráficos: {e}")

    def _update_monthly_graph(self, accounts: List[CuentaServicio], year: int):
        """Actualiza el gráfico mensual"""
        self.monthly_fig.clear()
        ax = self.monthly_fig.add_subplot(111)

        # Configurar colores del tema
        theme = theme_manager.get_theme()
        colors = theme['colors']

        ax.set_facecolor(colors.get('bg'))
        self.monthly_fig.patch.set_facecolor(colors.get('bg'))

        # Datos por mes
        monthly_data = {}
        for month in range(1, 13):
            monthly_data[month] = {
                'total': 0,
                'pagado': 0,
                'pendiente': 0
            }

        for account in accounts:
            month = account.fecha_emision.month
            monthly_data[month]['total'] += account.monto
            if account.pagado:
                monthly_data[month]['pagado'] += account.monto
            else:
                monthly_data[month]['pendiente'] += account.monto

        # Crear gráfico de barras
        months = list(range(1, 13))
        month_names = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                      'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        totals = [monthly_data[m]['total'] for m in months]
        pagados = [monthly_data[m]['pagado'] for m in months]
        pendientes = [monthly_data[m]['pendiente'] for m in months]

        width = 0.35
        x = np.arange(len(months))

        bars1 = ax.bar(x - width/2, pagados, width, label='Pagado',
                      color=colors.get('pagado', '#16c60c'), alpha=0.8)
        bars2 = ax.bar(x + width/2, pendientes, width, label='Pendiente',
                      color=colors.get('pendiente', '#ffb900'), alpha=0.8)

        ax.set_xlabel('Mes', color=colors.get('fg'))
        ax.set_ylabel('Monto (CLP)', color=colors.get('fg'))
        ax.set_title(f'Gastos Mensuales {year}', color=colors.get('fg'), fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(month_names)
        ax.legend()

        # Configurar colores de ejes
        ax.tick_params(colors=colors.get('fg'))
        ax.spines['bottom'].set_color(colors.get('fg'))
        ax.spines['top'].set_color(colors.get('fg'))
        ax.spines['right'].set_color(colors.get('fg'))
        ax.spines['left'].set_color(colors.get('fg'))

        # Formatear eje Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        self.monthly_canvas.draw()

    def _update_type_graph(self, accounts: List[CuentaServicio]):
        """Actualiza el gráfico por tipo"""
        self.type_fig.clear()
        ax = self.type_fig.add_subplot(111)

        # Configurar colores del tema
        theme = theme_manager.get_theme()
        colors = theme['colors']

        ax.set_facecolor(colors.get('bg'))
        self.type_fig.patch.set_facecolor(colors.get('bg'))

        # Datos por tipo
        type_data = {}
        for account in accounts:
            tipo = account.tipo_servicio.value
            if tipo not in type_data:
                type_data[tipo] = 0
            type_data[tipo] += account.monto

        if not type_data:
            ax.text(0.5, 0.5, 'No hay datos para mostrar',
                   ha='center', va='center', transform=ax.transAxes,
                   color=colors.get('fg'), fontsize=12)
        else:
            # Crear gráfico de pastel
            labels = list(type_data.keys())
            sizes = list(type_data.values())

            # Colores para el gráfico
            pie_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']

            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            startangle=90, colors=pie_colors[:len(labels)])

            # Configurar colores de texto
            for text in texts:
                text.set_color(colors.get('fg'))
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')

        ax.set_title('Distribución por Tipo de Servicio', color=colors.get('fg'),
                    fontsize=14, fontweight='bold')

        self.type_canvas.draw()

    def _update_status_graph(self, accounts: List[CuentaServicio]):
        """Actualiza el gráfico por estado"""
        self.status_fig.clear()
        ax = self.status_fig.add_subplot(111)

        # Configurar colores del tema
        theme = theme_manager.get_theme()
        colors = theme['colors']

        ax.set_facecolor(colors.get('bg'))
        self.status_fig.patch.set_facecolor(colors.get('bg'))

        # Datos por estado
        status_data = {
            'Pagado': 0,
            'Pendiente': 0,
            'Vencido': 0,
            'En Riesgo de Corte': 0
        }

        status_count = {
            'Pagado': 0,
            'Pendiente': 0,
            'Vencido': 0,
            'En Riesgo de Corte': 0
        }

        for account in accounts:
            estado = account.get_estado().value
            status_data[estado] += account.monto
            status_count[estado] += 1

        # Crear gráfico de barras horizontales
        states = list(status_data.keys())
        amounts = list(status_data.values())
        counts = list(status_count.values())

        # Colores por estado
        bar_colors = [
            colors.get('pagado', '#16c60c'),
            colors.get('pendiente', '#ffb900'),
            colors.get('vencido', '#e74856'),
            colors.get('por_vencer', '#ff8c00')
        ]

        bars = ax.barh(states, amounts, color=bar_colors, alpha=0.8)

        # Agregar etiquetas con cantidad
        for i, (bar, count) in enumerate(zip(bars, counts)):
            width = bar.get_width()
            if width > 0:
                ax.text(width + max(amounts) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'{count} cuenta(s)', ha='left', va='center',
                       color=colors.get('fg'), fontsize=10)

        ax.set_xlabel('Monto (CLP)', color=colors.get('fg'))
        ax.set_title('Cuentas por Estado', color=colors.get('fg'),
                    fontsize=14, fontweight='bold')

        # Configurar colores de ejes
        ax.tick_params(colors=colors.get('fg'))
        ax.spines['bottom'].set_color(colors.get('fg'))
        ax.spines['top'].set_color(colors.get('fg'))
        ax.spines['right'].set_color(colors.get('fg'))
        ax.spines['left'].set_color(colors.get('fg'))

        # Formatear eje X
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        self.status_canvas.draw()

    def _update_trends_graph(self, accounts: List[CuentaServicio]):
        """Actualiza el gráfico de tendencias"""
        self.trends_fig.clear()
        ax = self.trends_fig.add_subplot(111)

        # Configurar colores del tema
        theme = theme_manager.get_theme()
        colors = theme['colors']

        ax.set_facecolor(colors.get('bg'))
        self.trends_fig.patch.set_facecolor(colors.get('bg'))

        # Datos de tendencia por mes (últimos 12 meses)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)

        monthly_trends = {}
        for i in range(12):
            date = start_date + timedelta(days=30*i)
            key = f"{date.year}-{date.month:02d}"
            monthly_trends[key] = {'total': 0, 'count': 0}

        for account in accounts:
            if start_date <= account.fecha_emision <= end_date:
                key = f"{account.fecha_emision.year}-{account.fecha_emision.month:02d}"
                if key in monthly_trends:
                    monthly_trends[key]['total'] += account.monto
                    monthly_trends[key]['count'] += 1

        # Crear línea de tendencia
        dates = sorted(monthly_trends.keys())
        totals = [monthly_trends[date]['total'] for date in dates]
        counts = [monthly_trends[date]['count'] for date in dates]

        if any(totals):
            # Gráfico de línea para montos
            ax2 = ax.twinx()

            line1 = ax.plot(dates, totals, 'o-', color=colors.get('accent', '#0078d4'),
                           linewidth=2, markersize=6, label='Monto Total')
            line2 = ax2.plot(dates, counts, 's-', color=colors.get('warning', '#ffb900'),
                            linewidth=2, markersize=6, label='Cantidad de Cuentas')

            ax.set_xlabel('Período', color=colors.get('fg'))
            ax.set_ylabel('Monto (CLP)', color=colors.get('fg'))
            ax2.set_ylabel('Cantidad de Cuentas', color=colors.get('fg'))
            ax.set_title('Tendencia de Gastos (Últimos 12 Meses)',
                        color=colors.get('fg'), fontsize=14, fontweight='bold')

            # Configurar colores de ejes
            ax.tick_params(colors=colors.get('fg'))
            ax2.tick_params(colors=colors.get('fg'))

            for spine in ax.spines.values():
                spine.set_color(colors.get('fg'))
            for spine in ax2.spines.values():
                spine.set_color(colors.get('fg'))

            # Rotar etiquetas del eje X
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            # Leyenda combinada
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        else:
            ax.text(0.5, 0.5, 'No hay datos suficientes para mostrar tendencias',
                   ha='center', va='center', transform=ax.transAxes,
                   color=colors.get('fg'), fontsize=12)

        self.trends_canvas.draw()

    def _export_graphs(self):
        """Exporta los gráficos"""
        try:
            from tkinter import filedialog
            import os

            # Seleccionar directorio
            directory = filedialog.askdirectory(title="Seleccionar directorio para exportar gráficos")
            if not directory:
                return

            year = self.year_var.get()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Exportar cada gráfico
            graphs = [
                (self.monthly_fig, f"gastos_mensuales_{year}_{timestamp}.png"),
                (self.type_fig, f"por_tipo_servicio_{timestamp}.png"),
                (self.status_fig, f"por_estado_{timestamp}.png"),
                (self.trends_fig, f"tendencias_{timestamp}.png")
            ]

            exported = 0
            for fig, filename in graphs:
                try:
                    filepath = os.path.join(directory, filename)
                    fig.savefig(filepath, dpi=300, bbox_inches='tight',
                               facecolor=theme_manager.get_color('bg'))
                    exported += 1
                except Exception as e:
                    print(f"Error exportando {filename}: {e}")

            messagebox.showinfo("Exportación Completa",
                              f"Se exportaron {exported} gráficos a:\n{directory}")

        except Exception as e:
            messagebox.showerror("Error", f"Error exportando gráficos: {e}")

    def show(self):
        """Muestra la ventana"""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()