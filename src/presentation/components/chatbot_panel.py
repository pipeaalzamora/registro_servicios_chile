"""
Componente de Chatbot para la aplicación
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from typing import Callable, Optional

from ...ai.chatbot_service import ChatbotService, ChatMessage, ChatSuggestion
from ..utils import error_handler, handle_ui_errors, centrar_ventana
from ..themes import theme_manager


class ChatbotPanel:
    """Panel de chatbot inteligente"""

    def __init__(self, parent, chatbot_service: ChatbotService,
                 on_action_callback: Optional[Callable] = None):
        self.parent = parent
        self.chatbot_service = chatbot_service
        self.on_action_callback = on_action_callback

        self.setup_ui()
        self.load_conversation_history()

        # Mensaje de bienvenida
        self.send_welcome_message()

    def setup_ui(self):
        """Configura la interfaz del chatbot"""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Header del chatbot
        self.create_header()

        # Área de chat
        self.create_chat_area()

        # Área de sugerencias
        self.create_suggestions_area()

        # Área de entrada
        self.create_input_area()

    def create_header(self):
        """Crea el header del chatbot"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)

        # Avatar del bot
        avatar_label = tk.Label(
            header_frame,
            text="🤖",
            font=("Arial", 24),
            bg="#f0f0f0",
            relief="flat",
            width=3,
            height=1
        )
        avatar_label.grid(row=0, column=0, padx=(0, 10))

        # Información del bot
        info_frame = ttk.Frame(header_frame)
        info_frame.grid(row=0, column=1, sticky="w")

        title_label = tk.Label(
            info_frame,
            text="Asistente Virtual",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w")

        status_label = tk.Label(
            info_frame,
            text="En línea • Listo para ayudarte",
            font=("Arial", 9),
            fg="green"
        )
        status_label.grid(row=1, column=0, sticky="w")

        # Botones de control
        control_frame = ttk.Frame(header_frame)
        control_frame.grid(row=0, column=2, sticky="e")

        clear_button = tk.Button(
            control_frame,
            text="🗑️ Limpiar",
            command=self.clear_chat,
            relief="flat",
            borderwidth=1,
            padx=8,
            pady=2,
            cursor="hand2",
            font=("Arial", 9)
        )
        clear_button.grid(row=0, column=0, padx=(0, 5))

        help_button = tk.Button(
            control_frame,
            text="❓ Ayuda",
            command=self.show_help,
            relief="flat",
            borderwidth=1,
            padx=8,
            pady=2,
            cursor="hand2",
            font=("Arial", 9)
        )
        help_button.grid(row=0, column=1)

        # Aplicar tema
        theme_manager.apply_theme_to_widget(avatar_label)
        theme_manager.apply_theme_to_widget(title_label)
        theme_manager.apply_theme_to_widget(status_label)
        theme_manager.apply_theme_to_widget(clear_button)
        theme_manager.apply_theme_to_widget(help_button)

    def create_chat_area(self):
        """Crea el área de chat"""
        # Frame para el chat
        chat_frame = ttk.LabelFrame(self.main_frame, text="Conversación", padding="5")
        chat_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)

        # Área de texto con scroll
        self.chat_text = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            height=15,
            font=("Arial", 10),
            state=tk.DISABLED,
            bg="#fafafa",
            relief="flat",
            borderwidth=1
        )
        self.chat_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Configurar tags para estilos
        self.chat_text.tag_configure("user", foreground="#2c3e50", font=("Arial", 10, "bold"))
        self.chat_text.tag_configure("bot", foreground="#27ae60", font=("Arial", 10))
        self.chat_text.tag_configure("timestamp", foreground="#7f8c8d", font=("Arial", 8))
        self.chat_text.tag_configure("suggestion", foreground="#3498db", font=("Arial", 9, "italic"))

    def create_suggestions_area(self):
        """Crea el área de sugerencias"""
        self.suggestions_frame = ttk.LabelFrame(self.main_frame, text="Sugerencias", padding="5")
        self.suggestions_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.suggestions_frame.columnconfigure(0, weight=1)

    def create_input_area(self):
        """Crea el área de entrada"""
        input_frame = ttk.Frame(self.main_frame)
        input_frame.grid(row=3, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        # Campo de entrada
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Arial", 10)
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Configurar placeholder manualmente
        self.input_entry.insert(0, "Escribe tu mensaje aquí...")
        self.input_entry.config(foreground="gray")

        def on_focus_in(event):
            if self.input_var.get() == "Escribe tu mensaje aquí...":
                self.input_entry.delete(0, tk.END)
                self.input_entry.config(foreground="black")

        def on_focus_out(event):
            if not self.input_var.get():
                self.input_entry.insert(0, "Escribe tu mensaje aquí...")
                self.input_entry.config(foreground="gray")

        self.input_entry.bind('<FocusIn>', on_focus_in)
        self.input_entry.bind('<FocusOut>', on_focus_out)

        # Botón de enviar
        send_button = tk.Button(
            input_frame,
            text="📤 Enviar",
            command=self.send_message,
            relief="flat",
            borderwidth=1,
            padx=15,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white"
        )
        send_button.grid(row=0, column=1)

        # Vincular Enter para enviar
        self.input_entry.bind('<Return>', lambda e: self.send_message())
        self.input_entry.bind('<KeyRelease>', self.on_input_change)

        # Aplicar tema
        theme_manager.apply_theme_to_widget(send_button)

    def send_welcome_message(self):
        """Envía mensaje de bienvenida"""
        welcome_msg = "¡Hola! 👋 Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
        self.add_bot_message(welcome_msg)
        self.update_suggestions()

    def send_message(self):
        """Envía un mensaje al chatbot"""
        message = self.input_var.get().strip()
        if not message:
            return

        # Agregar mensaje del usuario
        self.add_user_message(message)
        self.input_var.set("")

        # Procesar con el chatbot
        try:
            response, suggestions = self.chatbot_service.process_message(message)
            self.add_bot_message(response)
            self.update_suggestions(suggestions)
        except Exception as e:
            error_msg = f"Lo siento, hubo un error procesando tu mensaje: {str(e)}"
            self.add_bot_message(error_msg)

        # Auto-scroll al final
        self.chat_text.see(tk.END)

    def add_user_message(self, message: str):
        """Agrega un mensaje del usuario al chat"""
        self.chat_text.config(state=tk.NORMAL)

        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")

        # Mensaje del usuario
        self.chat_text.insert(tk.END, f"Tú: {message}\n", "user")

        self.chat_text.config(state=tk.DISABLED)

    def add_bot_message(self, message: str):
        """Agrega un mensaje del bot al chat"""
        self.chat_text.config(state=tk.NORMAL)

        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_text.insert(tk.END, f"[{timestamp}] ", "timestamp")

        # Mensaje del bot
        self.chat_text.insert(tk.END, f"🤖 Asistente: {message}\n\n", "bot")

        self.chat_text.config(state=tk.DISABLED)

    def update_suggestions(self, suggestions: Optional[list] = None):
        """Actualiza las sugerencias mostradas"""
        # Limpiar sugerencias anteriores
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()

        if not suggestions:
            # Sugerencias por defecto
            default_suggestions = [
                ("Hola", "saludo"),
                ("¿Cómo crear una cuenta?", "ayuda"),
                ("¿Qué puedo hacer?", "ayuda"),
                ("Ver gráficos", "graficos")
            ]
        else:
            default_suggestions = [(s.text, s.action) for s in suggestions]

        # Crear botones de sugerencias
        for i, (text, action) in enumerate(default_suggestions):
            suggestion_button = tk.Button(
                self.suggestions_frame,
                text=text,
                command=lambda a=action: self.handle_suggestion(a),
                relief="flat",
                borderwidth=1,
                padx=10,
                pady=3,
                cursor="hand2",
                font=("Arial", 9),
                bg="#ecf0f1",
                fg="#2c3e50"
            )
            suggestion_button.grid(row=0, column=i, padx=2, pady=2)
            theme_manager.apply_theme_to_widget(suggestion_button)

    def handle_suggestion(self, action: str):
        """Maneja una sugerencia seleccionada"""
        if self.on_action_callback:
            self.on_action_callback(action)
        else:
            # Procesar como mensaje normal
            self.input_var.set(action)
            self.send_message()

    def clear_chat(self):
        """Limpia el historial del chat"""
        self.chatbot_service.clear_history()
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.delete(1.0, tk.END)
        self.chat_text.config(state=tk.DISABLED)
        self.send_welcome_message()

    def show_help(self):
        """Muestra ayuda del chatbot"""
        help_text = """💡 Cómo usar el asistente:

• Saludos: "Hola", "Buenos días"
• Crear cuenta: "Crear nueva cuenta", "Agregar servicio"
• Editar: "Editar cuenta", "Modificar servicio"
• Eliminar: "Eliminar cuenta", "Borrar servicio"
• Buscar: "Buscar cuentas", "Encontrar servicio"
• Reportes: "Generar reporte", "Crear PDF"
• Gráficos: "Ver gráficos", "Estadísticas"
• IA: "Usar IA", "Predicciones", "OCR"
• Pagos: "Cuentas vencidas", "Marcar pagado"
• Montos: "Total gastos", "Resumen"

¡Puedes escribir de forma natural! 🤖"""

        self.add_bot_message(help_text)

    def on_input_change(self, event):
        """Maneja cambios en el campo de entrada"""
        # Aquí se pueden agregar funcionalidades como autocompletado
        pass

    def load_conversation_history(self):
        """Carga el historial de conversación"""
        history = self.chatbot_service.get_conversation_history()
        for message in history:
            if message.is_user:
                self.add_user_message(message.text)
            else:
                self.add_bot_message(message.text)

    def get_widget(self):
        """Retorna el widget principal"""
        return self.main_frame


class ChatbotWindow:
    """Ventana independiente para el chatbot"""

    def __init__(self, parent, chatbot_service: ChatbotService,
                 on_action_callback: Optional[Callable] = None):
        self.parent = parent
        self.chatbot_service = chatbot_service
        self.on_action_callback = on_action_callback

        self.window = tk.Toplevel(parent)
        self.window.title("🤖 Asistente Virtual - Registro de Servicios")
        self.window.geometry("600x700")
        self.window.minsize(500, 600)
        self.window.transient(parent)

        # Centrar ventana
        centrar_ventana(self.window, parent, 600, 700)

        # Aplicar tema
        theme_manager.apply_theme_to_widget(self.window)

        # Configurar grid
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)

        # Crear panel de chatbot
        self.chatbot_panel = ChatbotPanel(self.window, chatbot_service, on_action_callback)

        # Configurar evento de cierre
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Maneja el cierre de la ventana"""
        self.window.destroy()

    def show(self):
        """Muestra la ventana"""
        self.window.lift()
        self.window.focus()
        self.window.wait_window()