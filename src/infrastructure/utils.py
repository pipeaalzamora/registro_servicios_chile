"""
Utilidades para la aplicación de registro de servicios
"""

def formatear_moneda_clp(monto: float) -> str:
    """
    Formatea un monto en pesos chilenos con separadores de miles

    Args:
        monto: Monto en pesos chilenos

    Returns:
        String formateado con símbolo de peso chileno y separadores de miles
    """
    return f"${monto:,.0f} CLP"

def formatear_moneda_clp_simple(monto: float) -> str:
    """
    Formatea un monto en pesos chilenos sin el sufijo CLP

    Args:
        monto: Monto en pesos chilenos

    Returns:
        String formateado con símbolo de peso chileno y separadores de miles
    """
    return f"${monto:,.0f}"

def parsear_moneda_clp(texto: str) -> float:
    """
    Parsea un texto con formato de moneda chilena a float

    Args:
        texto: Texto con formato de moneda (ej: "$1,234" o "1234")

    Returns:
        Float con el valor numérico

    Raises:
        ValueError: Si el formato no es válido
    """
    # Remover símbolos de moneda y espacios
    texto_limpio = texto.replace('$', '').replace('CLP', '').replace(' ', '').replace(',', '')

    try:
        return float(texto_limpio)
    except ValueError:
        raise ValueError("Formato de moneda inválido")

def parse_datetime(date_string: str):
    """Parsea una fecha desde string, manejando diferentes formatos y permitiendo None"""
    from datetime import datetime
    if date_string is None or date_string == "None":
        return None
    try:
        # Intentar con fromisoformat primero
        return datetime.fromisoformat(date_string)
    except ValueError:
        try:
            # Si falla, intentar parsear manualmente eliminando microsegundos
            if '.' in date_string:
                # Remover microsegundos si existen
                date_string = date_string.split('.')[0]
            return datetime.fromisoformat(date_string)
        except ValueError:
            # Si aún falla, usar strptime como último recurso
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            raise ValueError(f"No se pudo parsear la fecha: {date_string}")