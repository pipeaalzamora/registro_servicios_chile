"""
Panel de estadísticas mejorado
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from .themes import theme_manager, ThemedWidget
from .utils import format_currency


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