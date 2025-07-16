"""
Componente de calendario personalizado para selección de fechas
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
from typing import Optional, Callable


class CalendarWidget:
    """Widget de calendario para selección de fechas"""

    def __init__(self, parent, title: str = "Seleccionar Fecha",
                 initial_date: Optional[datetime] = None,
                 min_date: Optional[datetime] = None,
                 max_date: Optional[datetime] = None,
                 on_date_selected: Optional[Callable] = None):

        self.parent = parent
        self.title = title
        self.initial_date = initial_date or datetime.now()
        self.min_date = min_date
        self.max_date = max_date
        self.on_date_selected = on_date_selected

        self.selected_date = self.initial_date
        self.current_month = self.initial_date.month
        self.current_year = self.initial_date.year

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)

        self.setup_ui()
        self.update_calendar()

    def setup_ui(self):
        """Configura la interfaz del calendario"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame superior con navegación
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))

        # Botones de navegación
        ttk.Button(nav_frame, text="◀", width=3,
                  command=self.previous_month).pack(side=tk.LEFT)

        self.month_year_label = ttk.Label(nav_frame, text="", font=('Arial', 12, 'bold'))
        self.month_year_label.pack(side=tk.LEFT, expand=True)

        ttk.Button(nav_frame, text="▶", width=3,
                  command=self.next_month).pack(side=tk.RIGHT)

        # Frame del calendario
        calendar_frame = ttk.Frame(main_frame)
        calendar_frame.pack(fill=tk.BOTH, expand=True)

        # Días de la semana
        days_frame = ttk.Frame(calendar_frame)
        days_frame.pack(fill=tk.X)

        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        for i, day in enumerate(days):
            label = ttk.Label(days_frame, text=day, width=8,
                            font=('Arial', 9, 'bold'), anchor='center')
            label.grid(row=0, column=i, padx=1, pady=1)

        # Frame para los días del mes
        self.days_frame = ttk.Frame(calendar_frame)
        self.days_frame.pack(fill=tk.BOTH, expand=True)

        # Frame inferior con botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(button_frame, text="Hoy",
                  command=self.select_today).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Aceptar",
                  command=self.accept_date).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancelar",
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def update_calendar(self):
        """Actualiza la vista del calendario"""
        # Limpiar días anteriores
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        # Actualizar etiqueta de mes/año
        month_name = calendar.month_name[self.current_month]
        self.month_year_label.config(text=f"{month_name} {self.current_year}")

        # Obtener calendario del mes
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        # Crear botones para cada día
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    # Crear botón para el día
                    btn = tk.Button(self.days_frame, text=str(day), width=8, height=2,
                                   font=('Arial', 9), relief=tk.RAISED)
                    btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")

                    # Configurar evento de clic
                    btn.config(command=lambda d=day: self.select_date(d))

                    # Marcar fecha actual
                    current_date = datetime(self.current_year, self.current_month, day)
                    if current_date.date() == datetime.now().date():
                        btn.config(bg='lightblue', relief=tk.SUNKEN)

                    # Marcar fecha seleccionada
                    if (self.current_year == self.selected_date.year and
                        self.current_month == self.selected_date.month and
                        day == self.selected_date.day):
                        btn.config(bg='yellow', relief=tk.SUNKEN)

                    # Deshabilitar fechas fuera del rango permitido
                    if self.min_date and current_date < self.min_date:
                        btn.config(state=tk.DISABLED, bg='lightgray')
                    elif self.max_date and current_date > self.max_date:
                        btn.config(state=tk.DISABLED, bg='lightgray')

        # Configurar grid para que los botones se expandan
        for i in range(7):
            self.days_frame.columnconfigure(i, weight=1)
        for i in range(6):
            self.days_frame.rowconfigure(i, weight=1)

    def select_date(self, day: int):
        """Selecciona una fecha"""
        self.selected_date = datetime(self.current_year, self.current_month, day)
        self.update_calendar()

    def select_today(self):
        """Selecciona la fecha actual"""
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today
        self.update_calendar()

    def previous_month(self):
        """Navega al mes anterior"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.update_calendar()

    def next_month(self):
        """Navega al mes siguiente"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.update_calendar()

    def accept_date(self):
        """Acepta la fecha seleccionada"""
        if self.on_date_selected:
            self.on_date_selected(self.selected_date)
        self.dialog.destroy()

    def show(self):
        """Muestra el calendario y retorna la fecha seleccionada"""
        self.dialog.wait_window()
        return self.selected_date


class DateEntryWithCalendar:
    """Campo de entrada con botón de calendario"""

    def __init__(self, parent, label_text: str, initial_date: Optional[datetime] = None,
                 min_date: Optional[datetime] = None, max_date: Optional[datetime] = None,
                 row: int = 0, column: int = 0, **kwargs):

        self.parent = parent
        self.initial_date = initial_date
        self.min_date = min_date
        self.max_date = max_date

        # Frame contenedor
        self.frame = ttk.Frame(parent)
        self.frame.grid(row=row, column=column, **kwargs)

        # Label
        ttk.Label(self.frame, text=label_text).grid(row=0, column=0, sticky="w", pady=5)

        # Frame para entrada y botón
        input_frame = ttk.Frame(self.frame)
        input_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)

        # Variable para la fecha
        self.date_var = tk.StringVar()
        if initial_date:
            self.date_var.set(initial_date.strftime('%Y-%m-%d'))

        # Campo de entrada
        self.entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botón de calendario
        self.calendar_btn = ttk.Button(input_frame, text="📅", width=3,
                                      command=self.show_calendar)
        self.calendar_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Configurar grid
        self.frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(0, weight=1)

    def show_calendar(self):
        """Muestra el calendario para seleccionar fecha"""
        def on_date_selected(date):
            self.date_var.set(date.strftime('%Y-%m-%d'))

        CalendarWidget(
            parent=self.parent,
            title="Seleccionar Fecha",
            initial_date=self.get_date() or datetime.now(),
            min_date=self.min_date,
            max_date=self.max_date,
            on_date_selected=on_date_selected
        )

    def get_date(self) -> Optional[datetime]:
        """Obtiene la fecha del campo"""
        try:
            date_str = self.date_var.get().strip()
            if date_str:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            pass
        return None

    def set_date(self, date: datetime):
        """Establece la fecha en el campo"""
        self.date_var.set(date.strftime('%Y-%m-%d'))

    def get(self) -> str:
        """Obtiene el valor del campo como string"""
        return self.date_var.get()

    def set(self, value: str):
        """Establece el valor del campo"""
        self.date_var.set(value)