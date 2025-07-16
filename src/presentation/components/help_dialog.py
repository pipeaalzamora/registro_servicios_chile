"""
Diálogo de ayuda contextual para nuevos usuarios.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List
from ..themes import theme_manager

class HelpDialog:
    """Diálogo de ayuda contextual con tutorial interactivo."""

    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.current_step = 0
        self.tutorial_steps = [
            {
                "title": "¡Bienvenido a Registro de Servicios Chile!",
                "content": "Esta aplicación te ayudará a gestionar todas tus cuentas de servicios de manera organizada y eficiente.",
                "highlight": None
            },
            {
                "title": "Crear tu primera cuenta",
                "content": "Haz clic en el botón 'Nuevo Registro' para crear tu primera cuenta de servicio. Podrás seleccionar el tipo de servicio, ingresar montos y fechas importantes.",
                "highlight": "new_button"
            },
            {
                "title": "Búsqueda rápida",
                "content": "Usa el campo de búsqueda para encontrar cuentas rápidamente. Puedes buscar por nombre, descripción o monto.",
                "highlight": "search_entry"
            },
            {
                "title": "Ordenar y filtrar",
                "content": "Haz clic en los encabezados de la tabla para ordenar por cualquier columna. Los colores te ayudarán a identificar el estado de cada cuenta.",
                "highlight": "table"
            },
            {
                "title": "Estados de las cuentas",
                "content": "Las cuentas se muestran con colores según su estado:\n• Verde: Pagado\n• Rojo: Vencido\n• Amarillo: En riesgo de corte\n• Gris: Pendiente",
                "highlight": "status_colors"
            },
            {
                "title": "Calendario integrado",
                "content": "Al crear o editar cuentas, usa el calendario para seleccionar fechas de manera visual y rápida.",
                "highlight": "calendar"
            },
            {
                "title": "Reportes y estadísticas",
                "content": "Genera reportes PDF y visualiza estadísticas de tus gastos. Los gráficos te ayudarán a entender tus patrones de consumo.",
                "highlight": "reports"
            },
            {
                "title": "Modo oscuro",
                "content": "Cambia entre modo claro y oscuro según tu preferencia. El botón de tema está en la barra superior.",
                "highlight": "theme_toggle"
            },
            {
                "title": "¡Listo para empezar!",
                "content": "Ya conoces las funciones principales. Recuerda que puedes acceder a esta ayuda en cualquier momento desde el menú.",
                "highlight": None
            }
        ]

        self.create_dialog()

    def create_dialog(self):
        """Crea el diálogo de ayuda."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Ayuda - Registro de Servicios Chile")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Centrar el diálogo
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")

        # Aplicar tema
        theme_manager.apply_theme_to_widget(self.dialog)

        self.create_widgets()
        self.show_step(0)

    def create_widgets(self):
        """Crea los widgets del diálogo."""
        # Frame principal
        main_frame = tk.Frame(self.dialog)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

        # Título
        title_label = tk.Label(
            main_frame,
            text="Tutorial Interactivo",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky="w")

        # Frame del contenido
        content_frame = tk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Título del paso
        self.step_title = tk.Label(
            content_frame,
            text="",
            font=("Arial", 14, "bold"),
            wraplength=550
        )
        self.step_title.grid(row=0, column=0, pady=(0, 15), sticky="w")

        # Contenido del paso
        self.step_content = tk.Text(
            content_frame,
            height=8,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=1
        )
        self.step_content.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        content_frame.rowconfigure(1, weight=1)
        content_frame.columnconfigure(0, weight=1)

        # Frame de botones
        button_frame = tk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=(20, 0), sticky="ew")
        main_frame.rowconfigure(2, weight=0)

        # Botón anterior
        self.prev_button = tk.Button(
            button_frame,
            text="← Anterior",
            command=self.previous_step,
            width=12
        )
        self.prev_button.grid(row=0, column=0, padx=(0, 10))

        # Indicador de progreso
        self.progress_label = tk.Label(
            button_frame,
            text="",
            font=("Arial", 10)
        )
        self.progress_label.grid(row=0, column=1, padx=20)

        # Botón siguiente
        self.next_button = tk.Button(
            button_frame,
            text="Siguiente →",
            command=self.next_step,
            width=12
        )
        self.next_button.grid(row=0, column=2, padx=(10, 0))

        # Botón cerrar
        close_button = tk.Button(
            button_frame,
            text="Cerrar",
            command=self.dialog.destroy,
            width=12
        )
        close_button.grid(row=0, column=3, padx=(10, 0))

        # Aplicar tema a todos los widgets
        theme_manager.apply_theme_to_all_widgets(self.dialog)

    def show_step(self, step_index: int):
        """Muestra un paso específico del tutorial."""
        if 0 <= step_index < len(self.tutorial_steps):
            self.current_step = step_index
            step = self.tutorial_steps[step_index]

            # Actualizar título
            self.step_title.config(text=step["title"])

            # Actualizar contenido
            self.step_content.config(state=tk.NORMAL)
            self.step_content.delete(1.0, tk.END)
            self.step_content.insert(1.0, step["content"])
            self.step_content.config(state=tk.DISABLED)

            # Actualizar botones
            self.prev_button.config(state=tk.NORMAL if step_index > 0 else tk.DISABLED)

            if step_index == len(self.tutorial_steps) - 1:
                self.next_button.config(text="Finalizar")
            else:
                self.next_button.config(text="Siguiente →")

            # Actualizar progreso
            progress_text = f"Paso {step_index + 1} de {len(self.tutorial_steps)}"
            self.progress_label.config(text=progress_text)

            # Resaltar elemento si es necesario
            if step["highlight"]:
                self.highlight_element(step["highlight"])

    def next_step(self):
        """Avanza al siguiente paso."""
        if self.current_step < len(self.tutorial_steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            # Finalizar tutorial
            messagebox.showinfo(
                "Tutorial Completado",
                "¡Felicidades! Has completado el tutorial.\n\nYa estás listo para usar la aplicación de manera eficiente."
            )
            self.dialog.destroy()

    def previous_step(self):
        """Retrocede al paso anterior."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def highlight_element(self, element_name: str):
        """Resalta un elemento en la aplicación principal."""
        # Esta función se puede expandir para resaltar elementos específicos
        # Por ahora solo mostramos un mensaje
        pass

class QuickHelpDialog:
    """Diálogo de ayuda rápida con información específica."""

    def __init__(self, parent: tk.Tk, topic: str = "general"):
        self.parent = parent
        self.topic = topic

        self.help_topics = {
            "general": {
                "title": "Ayuda General",
                "content": """
Funciones Principales:
• Crear, editar y eliminar cuentas de servicios
• Búsqueda y filtrado en tiempo real
• Ordenamiento por columnas
• Estados visuales con colores
• Calendario integrado para fechas
• Reportes PDF profesionales
• Gráficos y estadísticas
• Modo oscuro/claro
• Notificaciones por email
• Backups automáticos

Atajos de Teclado:
• Ctrl+N: Nuevo registro
• Ctrl+F: Buscar
• Ctrl+R: Generar reporte
• Ctrl+T: Cambiar tema
• F1: Mostrar ayuda
                """
            },
            "accounts": {
                "title": "Gestión de Cuentas",
                "content": """
Crear Nueva Cuenta:
1. Haz clic en "Nuevo Registro"
2. Selecciona el tipo de servicio
3. Completa los campos obligatorios
4. Usa el calendario para las fechas
5. Haz clic en "Guardar"

Editar Cuenta:
1. Selecciona la cuenta en la tabla
2. Haz clic en "Editar"
3. Modifica los campos necesarios
4. Guarda los cambios

Eliminar Cuenta:
1. Selecciona la cuenta
2. Haz clic en "Eliminar"
3. Confirma la acción

Estados de Cuentas:
• Verde: Pagado
• Rojo: Vencido
• Amarillo: En riesgo de corte
• Gris: Pendiente
                """
            },
            "search": {
                "title": "Búsqueda y Filtrado",
                "content": """
Búsqueda Rápida:
• Escribe en el campo de búsqueda
• Filtra por nombre, descripción o monto
• La búsqueda es en tiempo real

Ordenamiento:
• Haz clic en los encabezados de columna
• Los indicadores muestran la dirección
• Puedes ordenar por cualquier campo

Filtros Avanzados:
• Por estado de pago
• Por tipo de servicio
• Por rango de fechas
• Por rango de montos
                """
            },
            "reports": {
                "title": "Reportes y Estadísticas",
                "content": """
Generar Reporte PDF:
1. Haz clic en "Generar Reporte"
2. Selecciona el tipo de reporte
3. Elige el rango de fechas
4. El reporte se guarda en la carpeta 'reports'

Tipos de Reporte:
• Resumen general
• Por servicio específico
• Por período de tiempo
• Cuentas vencidas
• Cuentas en riesgo

Gráficos Disponibles:
• Gastos por servicio
• Evolución mensual
• Comparación anual
• Distribución de pagos
                """
            },
            "settings": {
                "title": "Configuración",
                "content": """
Notificaciones por Email:
1. Edita config/notifications.json
2. Configura tu servidor SMTP
3. Establece las fechas de recordatorio
4. Activa las notificaciones

Backups Automáticos:
• Se crean automáticamente
• Ubicación: data/backups/
• Frecuencia configurable
• Máximo 10 backups

Modo Oscuro:
• Cambia el tema visual
• Se recuerda tu preferencia
• Aplica a toda la interfaz
                """
            }
        }

        self.create_dialog()

    def create_dialog(self):
        """Crea el diálogo de ayuda rápida."""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Ayuda Rápida")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # Centrar el diálogo
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")

        # Aplicar tema
        theme_manager.apply_theme_to_widget(self.dialog)

        self.create_widgets()

    def create_widgets(self):
        """Crea los widgets del diálogo de ayuda rápida."""
        # Frame principal
        main_frame = tk.Frame(self.dialog)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)

        # Título
        topic_info = self.help_topics.get(self.topic, self.help_topics["general"])
        title_label = tk.Label(
            main_frame,
            text=topic_info["title"],
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 15), sticky="w")

        # Contenido
        content_text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=1
        )
        content_text.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Insertar contenido
        content_text.config(state=tk.NORMAL)
        content_text.delete(1.0, tk.END)
        content_text.insert(1.0, topic_info["content"])
        content_text.config(state=tk.DISABLED)

        # Botón cerrar
        close_button = tk.Button(
            main_frame,
            text="Cerrar",
            command=self.dialog.destroy,
            width=12
        )
        close_button.grid(row=2, column=0, pady=(10, 0))

        # Aplicar tema
        theme_manager.apply_theme_to_all_widgets(self.dialog)