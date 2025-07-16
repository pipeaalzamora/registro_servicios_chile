"""
Módulo para manejar temas de la interfaz (claro y oscuro).
"""

from typing import Dict, Any, Union
import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Gestor de temas para la aplicación."""

    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg_primary": "#ffffff",
                "bg_secondary": "#f8f9fa",
                "bg_tertiary": "#e9ecef",
                "fg_primary": "#212529",
                "fg_secondary": "#6c757d",
                "accent": "#007bff",
                "accent_hover": "#0056b3",
                "success": "#28a745",
                "warning": "#ffc107",
                "danger": "#dc3545",
                "info": "#17a2b8",
                "border": "#dee2e6",
                "border_focus": "#007bff",
                "table_bg": "#ffffff",
                "table_alt_bg": "#f8f9fa",
                "table_header_bg": "#e9ecef",
                "table_header_fg": "#495057",
                "button_bg": "#007bff",
                "button_fg": "#ffffff",
                "button_disabled_bg": "#6c757d",
                "entry_bg": "#ffffff",
                "entry_fg": "#212529",
                "entry_border": "#ced4da",
                "calendar_bg": "#ffffff",
                "calendar_fg": "#212529",
                "calendar_selected_bg": "#007bff",
                "calendar_selected_fg": "#ffffff",
                "calendar_today_bg": "#e3f2fd",
                "calendar_today_fg": "#1976d2"
            },
            "dark": {
                "bg_primary": "#1a1a1a",
                "bg_secondary": "#2d2d2d",
                "bg_tertiary": "#404040",
                "fg_primary": "#ffffff",
                "fg_secondary": "#b0b0b0",
                "accent": "#4dabf7",
                "accent_hover": "#74c0fc",
                "success": "#51cf66",
                "warning": "#ffd43b",
                "danger": "#ff6b6b",
                "info": "#74c0fc",
                "border": "#404040",
                "border_focus": "#4dabf7",
                "table_bg": "#2d2d2d",
                "table_alt_bg": "#404040",
                "table_header_bg": "#1a1a1a",
                "table_header_fg": "#ffffff",
                "button_bg": "#4dabf7",
                "button_fg": "#ffffff",
                "button_disabled_bg": "#6c757d",
                "entry_bg": "#404040",
                "entry_fg": "#ffffff",
                "entry_border": "#6c757d",
                "calendar_bg": "#2d2d2d",
                "calendar_fg": "#ffffff",
                "calendar_selected_bg": "#4dabf7",
                "calendar_selected_fg": "#ffffff",
                "calendar_today_bg": "#1e3a5f",
                "calendar_today_fg": "#74c0fc"
            }
        }

    def get_theme(self, theme_name: str | None = None) -> Dict[str, str]:
        """Obtiene el tema especificado o el actual."""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes["light"])

    def set_theme(self, theme_name: str) -> None:
        """Establece el tema actual."""
        if theme_name in self.themes:
            self.current_theme = theme_name

    def toggle_theme(self) -> str:
        """Alterna entre tema claro y oscuro."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.set_theme(new_theme)
        return new_theme

    def apply_theme_to_widget(self, widget: Union[tk.Widget, tk.Tk, tk.Toplevel], theme_name: str | None = None) -> None:
        """Aplica el tema a un widget específico."""
        theme = self.get_theme(theme_name)

        try:
            if isinstance(widget, tk.Tk) or isinstance(widget, tk.Toplevel):
                widget.configure(bg=theme["bg_primary"])
            elif isinstance(widget, tk.Frame) or isinstance(widget, tk.LabelFrame):
                widget.configure(
                    bg=theme["bg_primary"],
                    highlightbackground=theme["border"],
                    highlightcolor=theme["border_focus"]
                )
            elif isinstance(widget, tk.Label):
                widget.configure(
                    bg=theme["bg_primary"],
                    fg=theme["fg_primary"]
                )
            elif isinstance(widget, tk.Button):
                widget.configure(
                    bg=theme["button_bg"],
                    fg=theme["button_fg"],
                    activebackground=theme["accent_hover"],
                    activeforeground=theme["button_fg"],
                    relief="flat",
                    borderwidth=1,
                    highlightthickness=0
                )
            elif isinstance(widget, tk.Entry):
                widget.configure(
                    bg=theme["entry_bg"],
                    fg=theme["entry_fg"],
                    insertbackground=theme["fg_primary"],
                    relief="flat",
                    borderwidth=1,
                    highlightthickness=1,
                    highlightbackground=theme["entry_border"],
                    highlightcolor=theme["border_focus"]
                )
            elif isinstance(widget, ttk.Treeview):
                style = ttk.Style()
                style.theme_use('default')

                # Configurar estilo del Treeview
                style.configure(
                    "Treeview",
                    background=theme["table_bg"],
                    foreground=theme["fg_primary"],
                    fieldbackground=theme["table_bg"],
                    borderwidth=0,
                    relief="flat"
                )

                style.configure(
                    "Treeview.Heading",
                    background=theme["table_header_bg"],
                    foreground=theme["table_header_fg"],
                    relief="flat",
                    borderwidth=0
                )

                # Configurar colores alternados
                style.map(
                    "Treeview",
                    background=[("alternate", theme["table_alt_bg"])]
                )
        except Exception:
            # Ignorar errores de configuración
            pass

    def apply_theme_to_all_widgets(self, root: Union[tk.Widget, tk.Tk, tk.Toplevel], theme_name: str | None = None) -> None:
        """Aplica el tema a todos los widgets recursivamente."""
        theme = self.get_theme(theme_name)

        def apply_recursive(widget):
            try:
                self.apply_theme_to_widget(widget, theme_name)
            except:
                pass  # Ignorar widgets que no soporten el tema

            # Aplicar a todos los hijos
            for child in widget.winfo_children():
                apply_recursive(child)

        apply_recursive(root)

# Instancia global del gestor de temas
theme_manager = ThemeManager()