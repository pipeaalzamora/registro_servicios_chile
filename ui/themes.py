"""
Sistema de tema oscuro para la aplicación
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class ThemeManager:
    """Gestor de tema oscuro"""

    def __init__(self):
        self.current_theme = 'dark'
        self.theme = self._load_dark_theme()

    def _load_dark_theme(self) -> Dict[str, Any]:
        """Carga la definición del tema oscuro"""
        return {
            'name': 'Oscuro',
            'colors': {
                'bg': '#1e1e1e',
                'fg': '#ffffff',
                'select_bg': '#0078d4',
                'select_fg': '#ffffff',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'entry_bg': '#2d2d2d',
                'entry_fg': '#ffffff',
                'frame_bg': '#252526',
                'label_bg': '#1e1e1e',
                'label_fg': '#ffffff',
                'accent': '#0078d4',
                'success': '#16c60c',
                'warning': '#ffb900',
                'error': '#e74856',
                'border': '#3e3e3e',
                'pagado': '#16c60c',
                'pendiente': '#ffb900',
                'vencido': '#e74856',
                'por_vencer': '#ff8c00'
            },
            'fonts': {
                'default': ('Segoe UI', 9),
                'heading': ('Segoe UI', 12, 'bold'),
                'small': ('Segoe UI', 8),
                'large': ('Segoe UI', 14),
                'mono': ('Consolas', 9)
            },
            'styles': {
                'padding': 8,
                'border_width': 1,
                'relief': 'flat'
            }
        }

    def get_theme(self) -> Dict[str, Any]:
        """Obtiene el tema oscuro"""
        return self.theme

    def apply_theme_to_widget(self, widget: tk.Widget):
        """Aplica tema oscuro a un widget específico"""
        colors = self.theme['colors']

        try:
            # Aplicar colores básicos
            if hasattr(widget, 'configure'):
                widget.configure(
                    bg=colors.get('bg', '#1e1e1e'),
                    fg=colors.get('fg', '#ffffff')
                )
        except tk.TclError:
            pass  # Algunos widgets no soportan todos los colores

    def configure_ttk_styles(self):
        """Configura estilos TTK para el tema oscuro"""
        colors = self.theme['colors']
        fonts = self.theme['fonts']

        style = ttk.Style()

        # Usar tema base clam para mejor personalización en oscuro
        try:
            style.theme_use('clam')
        except:
            pass

        # Configurar estilos básicos
        style.configure('TLabel',
                       background=colors.get('label_bg'),
                       foreground=colors.get('label_fg'),
                       font=fonts.get('default'))

        # Configuración de botones base
        button_config = {
            'background': colors.get('button_bg'),
            'foreground': colors.get('button_fg'),
            'font': fonts.get('default'),
            'borderwidth': 2,
            'relief': 'raised',
            'padding': (12, 8),
            'focuscolor': 'none',
            'bordercolor': colors.get('border'),
            'lightcolor': '#505050',
            'darkcolor': '#2a2a2a'
        }

        style.configure('TButton', **button_config)

        # Estados del botón
        style.map('TButton',
                 background=[
                     ('active', colors.get('select_bg')),
                     ('pressed', '#005a9e'),
                     ('focus', colors.get('button_bg')),
                     ('disabled', colors.get('bg'))
                 ],
                 foreground=[
                     ('active', colors.get('select_fg')),
                     ('pressed', colors.get('select_fg')),
                     ('focus', colors.get('button_fg')),
                     ('disabled', '#666666')
                 ],
                 relief=[
                     ('pressed', 'sunken'),
                     ('active', 'raised'),
                     ('focus', 'solid')
                 ],
                 bordercolor=[
                     ('active', colors.get('select_bg')),
                     ('pressed', '#005a9e'),
                     ('focus', colors.get('accent'))
                 ],
                 lightcolor=[
                     ('active', '#4a9eff'),
                     ('pressed', '#005a9e')
                 ])

        # Entry
        style.configure('TEntry',
                       fieldbackground=colors.get('entry_bg'),
                       foreground=colors.get('entry_fg'),
                       font=fonts.get('default'),
                       borderwidth=1,
                       insertcolor=colors.get('fg'))

        # Combobox
        style.configure('TCombobox',
                       fieldbackground=colors.get('entry_bg'),
                       background=colors.get('button_bg'),
                       foreground=colors.get('entry_fg'),
                       font=fonts.get('default'),
                       borderwidth=1,
                       arrowcolor=colors.get('fg'))

        style.map('TCombobox',
                 fieldbackground=[('readonly', colors.get('entry_bg'))],
                 selectbackground=[('readonly', colors.get('select_bg'))],
                 selectforeground=[('readonly', colors.get('select_fg'))])

        # Frame
        style.configure('TFrame',
                       background=colors.get('frame_bg'),
                       borderwidth=0)

        # LabelFrame
        style.configure('TLabelFrame',
                       background=colors.get('frame_bg'),
                       foreground=colors.get('label_fg'),
                       font=fonts.get('default'),
                       borderwidth=1)

        # Treeview
        style.configure('Treeview',
                       background=colors.get('entry_bg'),
                       foreground=colors.get('entry_fg'),
                       font=fonts.get('default'),
                       fieldbackground=colors.get('entry_bg'))

        style.configure('Treeview.Heading',
                       background=colors.get('button_bg'),
                       foreground=colors.get('button_fg'),
                       font=fonts.get('heading'))

        # Estilos personalizados
        self._configure_custom_styles(style)

    def _configure_custom_styles(self, style: ttk.Style):
        """Configura estilos personalizados para tema oscuro"""
        colors = self.theme['colors']
        fonts = self.theme['fonts']

        # Estilo para títulos
        style.configure('Title.TLabel',
                       background=colors.get('label_bg'),
                       foreground=colors.get('accent'),
                       font=fonts.get('large'))

        # Estilo para subtítulos
        style.configure('Heading.TLabel',
                       background=colors.get('label_bg'),
                       foreground=colors.get('fg'),
                       font=fonts.get('heading'))

        # Estilo para texto pequeño
        style.configure('Small.TLabel',
                       background=colors.get('label_bg'),
                       foreground=colors.get('fg'),
                       font=fonts.get('small'))

        # Configuración base para botones especiales
        special_button_base = {
            'font': (fonts.get('default')[0], fonts.get('default')[1], 'bold'),
            'borderwidth': 2,
            'relief': 'raised',
            'padding': (12, 8),
            'focuscolor': 'none'
        }

        # Botón de acción (azul)
        action_config = special_button_base.copy()
        action_config.update({
            'background': colors.get('accent'),
            'foreground': 'white',
            'bordercolor': colors.get('accent'),
            'lightcolor': '#4a9eff',
            'darkcolor': '#005a9e'
        })

        style.configure('Action.TButton', **action_config)
        style.map('Action.TButton',
                 background=[('active', '#106ebe'),
                           ('pressed', '#005a9e'),
                           ('focus', colors.get('accent')),
                           ('disabled', '#666666')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('focus', 'white'),
                           ('disabled', '#cccccc')],
                 relief=[('pressed', 'sunken'),
                        ('active', 'raised'),
                        ('focus', 'solid')])

        # Botón de éxito (verde)
        success_config = special_button_base.copy()
        success_config.update({
            'background': colors.get('success'),
            'foreground': 'white',
            'bordercolor': colors.get('success'),
            'lightcolor': '#4dd637',
            'darkcolor': '#0f7a09'
        })

        style.configure('Success.TButton', **success_config)
        style.map('Success.TButton',
                 background=[('active', '#14a10c'),
                           ('pressed', '#0f7a09'),
                           ('focus', colors.get('success')),
                           ('disabled', '#666666')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('focus', 'white'),
                           ('disabled', '#cccccc')],
                 relief=[('pressed', 'sunken'),
                        ('active', 'raised'),
                        ('focus', 'solid')])

        # Botón de advertencia (amarillo)
        warning_config = special_button_base.copy()
        warning_config.update({
            'background': colors.get('warning'),
            'foreground': 'white',
            'bordercolor': colors.get('warning'),
            'lightcolor': '#ffd633',
            'darkcolor': '#cc9400'
        })

        style.configure('Warning.TButton', **warning_config)
        style.map('Warning.TButton',
                 background=[('active', '#e6a600'),
                           ('pressed', '#cc9400'),
                           ('focus', colors.get('warning')),
                           ('disabled', '#666666')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('focus', 'white'),
                           ('disabled', '#cccccc')],
                 relief=[('pressed', 'sunken'),
                        ('active', 'raised'),
                        ('focus', 'solid')])

        # Botón de error (rojo)
        error_config = special_button_base.copy()
        error_config.update({
            'background': colors.get('error'),
            'foreground': 'white',
            'bordercolor': colors.get('error'),
            'lightcolor': '#ff6b7a',
            'darkcolor': '#b02332'
        })

        style.configure('Error.TButton', **error_config)
        style.map('Error.TButton',
                 background=[('active', '#d13544'),
                           ('pressed', '#b02332'),
                           ('focus', colors.get('error')),
                           ('disabled', '#666666')],
                 foreground=[('active', 'white'),
                           ('pressed', 'white'),
                           ('focus', 'white'),
                           ('disabled', '#cccccc')],
                 relief=[('pressed', 'sunken'),
                        ('active', 'raised'),
                        ('focus', 'solid')])

        # Frame de estadísticas
        try:
            style.configure('Stats.TLabelFrame',
                           background=colors.get('frame_bg'),
                           foreground=colors.get('accent'),
                           font=fonts.get('heading'))
        except tk.TclError:
            pass

    def get_color(self, color_name: str) -> str:
        """Obtiene un color específico del tema oscuro"""
        return self.theme['colors'].get(color_name, '#ffffff')

    def get_font(self, font_name: str) -> tuple:
        """Obtiene una fuente específica del tema oscuro"""
        return self.theme['fonts'].get(font_name, ('Segoe UI', 9))


class ThemedWidget:
    """Mixin para widgets con soporte de tema oscuro"""

    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager

    def apply_theme(self, widget: tk.Widget = None):
        """Aplica el tema oscuro al widget"""
        if widget is None:
            widget = self
        self.theme_manager.apply_theme_to_widget(widget)

    def get_themed_color(self, color_name: str) -> str:
        """Obtiene un color del tema oscuro"""
        return self.theme_manager.get_color(color_name)

    def get_themed_font(self, font_name: str) -> tuple:
        """Obtiene una fuente del tema oscuro"""
        return self.theme_manager.get_font(font_name)


# Instancia global del gestor de tema oscuro
theme_manager = ThemeManager()