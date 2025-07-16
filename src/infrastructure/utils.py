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