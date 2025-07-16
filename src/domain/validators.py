"""
Validadores centralizados para las entidades del dominio
"""

import re
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .entities import TipoServicio


class CuentaServicioValidator:
    """Validador centralizado para cuentas de servicio"""

    # Constantes de validación
    MONTO_MAXIMO = 10_000_000  # 10 millones de pesos
    MONTO_MINIMO = 0
    DESCRIPCION_MAX_LENGTH = 500
    OBSERVACIONES_MAX_LENGTH = 1000
    DIAS_MAX_FUTURO = 365
    DIAS_MAX_PASADO = 3650
    DIAS_MAX_CORTE_DESPUES_VENCIMIENTO = 30

    @classmethod
    def validar_monto(cls, monto: float) -> Tuple[bool, Optional[str]]:
        """Valida el monto de una cuenta"""
        if monto <= cls.MONTO_MINIMO:
            return False, "El monto debe ser mayor a 0"

        if monto > cls.MONTO_MAXIMO:
            return False, f"El monto no puede exceder ${cls.MONTO_MAXIMO:,}"

        return True, None

    @classmethod
    def validar_fechas(cls, fecha_emision: datetime, fecha_vencimiento: datetime) -> Tuple[bool, Optional[str]]:
        """Valida las fechas de emisión y vencimiento"""
        if fecha_vencimiento <= fecha_emision:
            return False, "La fecha de vencimiento debe ser posterior a la fecha de emisión"

        ahora = datetime.now()
        if fecha_emision > ahora + timedelta(days=cls.DIAS_MAX_FUTURO):
            return False, f"La fecha de emisión no puede ser más de {cls.DIAS_MAX_FUTURO} días en el futuro"

        if fecha_emision < ahora - timedelta(days=cls.DIAS_MAX_PASADO):
            return False, f"La fecha de emisión no puede ser más antigua de {cls.DIAS_MAX_PASADO} días"

        return True, None

    @classmethod
    def validar_fecha_proxima_lectura(cls, fecha_proxima_lectura: Optional[datetime],
                                    fecha_emision: datetime) -> Tuple[bool, Optional[str]]:
        """Valida la fecha de próxima lectura"""
        if fecha_proxima_lectura and fecha_proxima_lectura < fecha_emision:
            return False, "La fecha de próxima lectura no puede ser anterior a la fecha de emisión"

        return True, None

    @classmethod
    def validar_fecha_corte(cls, fecha_corte: Optional[datetime],
                          fecha_emision: datetime,
                          fecha_vencimiento: datetime) -> Tuple[bool, Optional[str]]:
        """Valida la fecha de corte"""
        if fecha_corte:
            if fecha_corte < fecha_emision:
                return False, "La fecha de corte no puede ser anterior a la fecha de emisión"

            if fecha_corte > fecha_vencimiento + timedelta(days=cls.DIAS_MAX_CORTE_DESPUES_VENCIMIENTO):
                return False, f"La fecha de corte no puede ser más de {cls.DIAS_MAX_CORTE_DESPUES_VENCIMIENTO} días después del vencimiento"

        return True, None

    @classmethod
    def validar_descripcion(cls, descripcion: str) -> Tuple[bool, Optional[str]]:
        """Valida la descripción de la cuenta"""
        if not descripcion or not descripcion.strip():
            return False, "La descripción no puede estar vacía"

        if len(descripcion.strip()) > cls.DESCRIPCION_MAX_LENGTH:
            return False, f"La descripción no puede exceder {cls.DESCRIPCION_MAX_LENGTH} caracteres"

        if re.search(r'[<>"\']', descripcion):
            return False, "La descripción no puede contener caracteres especiales como <, >, \", '"

        return True, None

    @classmethod
    def validar_observaciones(cls, observaciones: str) -> Tuple[bool, Optional[str]]:
        """Valida las observaciones de la cuenta"""
        if len(observaciones) > cls.OBSERVACIONES_MAX_LENGTH:
            return False, f"Las observaciones no pueden exceder {cls.OBSERVACIONES_MAX_LENGTH} caracteres"

        if re.search(r'[<>"\']', observaciones):
            return False, "Las observaciones no pueden contener caracteres especiales como <, >, \", '"

        return True, None

    @classmethod
    def validar_cuenta_completa(cls, tipo_servicio: 'TipoServicio', fecha_emision: datetime,
                               fecha_vencimiento: datetime, monto: float, descripcion: str,
                               observaciones: str = "", fecha_proxima_lectura: Optional[datetime] = None,
                               fecha_corte: Optional[datetime] = None) -> List[str]:
        """Valida todos los campos de una cuenta y retorna lista de errores"""
        errores = []

        # Validar monto
        monto_valido, error_monto = cls.validar_monto(monto)
        if not monto_valido:
            errores.append(error_monto)

        # Validar fechas principales
        fechas_validas, error_fechas = cls.validar_fechas(fecha_emision, fecha_vencimiento)
        if not fechas_validas:
            errores.append(error_fechas)

        # Validar fecha próxima lectura
        prox_lectura_valida, error_prox = cls.validar_fecha_proxima_lectura(fecha_proxima_lectura, fecha_emision)
        if not prox_lectura_valida:
            errores.append(error_prox)

        # Validar fecha corte
        corte_valido, error_corte = cls.validar_fecha_corte(fecha_corte, fecha_emision, fecha_vencimiento)
        if not corte_valido:
            errores.append(error_corte)

        # Validar descripción
        desc_valida, error_desc = cls.validar_descripcion(descripcion)
        if not desc_valida:
            errores.append(error_desc)

        # Validar observaciones
        obs_valida, error_obs = cls.validar_observaciones(observaciones)
        if not obs_valida:
            errores.append(error_obs)

        return errores


from ..infrastructure.security import security_manager


class TextValidator:
    """Validador para textos y sanitización"""

    @staticmethod
    def sanitizar_texto(texto: str, max_length: Optional[int] = None) -> str:
        """Sanitiza texto removiendo caracteres peligrosos usando SecurityManager"""
        texto_sanitizado = security_manager.sanitizar_texto(texto)

        # Limitar longitud si se especifica
        if max_length:
            texto_sanitizado = texto_sanitizado[:max_length]

        return texto_sanitizado

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email usando SecurityManager"""
        return security_manager.validar_email(email)