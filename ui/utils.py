"""
Utilidades para la interfaz de usuario
"""

from datetime import datetime
from typing import Optional


def format_currency(amount: float) -> str:
    """Formatea un monto como moneda chilena"""
    # Formatear con separador de miles punto (estilo chileno)
    formatted = f"{amount:,.0f}".replace(",", ".")
    return f"${formatted}"


def format_date(date: datetime) -> str:
    """Formatea una fecha en formato DD/MM/YYYY"""
    if date is None:
        return ""
    return date.strftime("%d/%m/%Y")


def get_estado_color(estado: str) -> Optional[str]:
    """Retorna el color asociado a un estado"""
    colors = {
        'Pagado': '#90EE90',      # Verde claro
        'Pendiente': '#FFE4B5',   # Amarillo claro
        'Vencido': '#FFB6C1',     # Rojo claro
        'En Riesgo de Corte': '#FFA500'  # Naranja
    }
    return colors.get(estado)


def center_window(window, width: int, height: int):
    """Centra una ventana en la pantalla"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def validate_number(value: str) -> bool:
    """Valida que un string sea un número válido"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_date_parts(day: str, month: str, year: str) -> bool:
    """Valida que las partes de una fecha sean válidas"""
    try:
        day_int = int(day) if day else 0
        month_int = int(month) if month else 0
        year_int = int(year) if year else 0

        if not (1 <= day_int <= 31):
            return False
        if not (1 <= month_int <= 12):
            return False
        if not (1900 <= year_int <= 2100):
            return False

        # Validar fecha real
        datetime(year_int, month_int, day_int)
        return True

    except (ValueError, TypeError):
        return False


def truncate_text(text: str, max_length: int) -> str:
    """Trunca un texto si es muy largo"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def parse_currency_input(value: str) -> float:
    """Parsea entrada de moneda removiendo formato"""
    if not value:
        return 0.0

    # Remover símbolos de moneda y espacios
    clean_value = value.replace("$", "").replace(" ", "").strip()

    # Si contiene punto como separador de miles (formato chileno)
    if "." in clean_value and "," not in clean_value:
        # Verificar si es separador de miles o decimal
        parts = clean_value.split(".")
        if len(parts) == 2 and len(parts[1]) == 3:
            # Es separador de miles (ej: 32.000)
            clean_value = clean_value.replace(".", "")
        # Si tiene más de un punto, remover todos (separadores de miles)
        elif len(parts) > 2:
            clean_value = clean_value.replace(".", "")

    # Si contiene coma como decimal
    if "," in clean_value:
        clean_value = clean_value.replace(",", ".")

    return float(clean_value) if clean_value else 0.0