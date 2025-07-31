"""
Modelos de datos simplificados para la aplicación
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List


class TipoServicio(Enum):
    """Tipos de servicios disponibles"""
    LUZ = "Luz"
    AGUA = "Agua"
    GAS = "Gas"
    INTERNET = "Internet"
    TELEFONO = "Teléfono"
    GASTOS_COMUNES = "Gastos Comunes"
    OTRO = "Otro"


class EstadoCuenta(Enum):
    """Estados posibles de una cuenta"""
    PENDIENTE = "Pendiente"
    PAGADO = "Pagado"
    VENCIDO = "Vencido"
    EN_RIESGO_CORTE = "En Riesgo de Corte"


@dataclass
class CuentaServicio:
    """Modelo principal para las cuentas de servicio"""
    id: Optional[str] = None
    tipo_servicio: TipoServicio = TipoServicio.LUZ
    descripcion: str = ""
    monto: float = 0.0
    fecha_emision: datetime = None
    fecha_vencimiento: datetime = None
    fecha_corte: Optional[datetime] = None
    fecha_lectura_proxima: Optional[datetime] = None
    pagado: bool = False
    fecha_pago: Optional[datetime] = None
    observaciones: str = ""
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        """Inicialización posterior"""
        if self.fecha_emision is None:
            self.fecha_emision = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def get_estado(self) -> EstadoCuenta:
        """Calcula el estado actual de la cuenta"""
        if self.pagado:
            return EstadoCuenta.PAGADO

        now = datetime.now()

        # Verificar si está vencida
        if now > self.fecha_vencimiento:
            return EstadoCuenta.VENCIDO

        # Verificar si está en riesgo de corte
        if self.fecha_corte and now >= self.fecha_corte:
            return EstadoCuenta.EN_RIESGO_CORTE

        return EstadoCuenta.PENDIENTE

    def dias_para_vencer(self) -> int:
        """Calcula los días restantes para el vencimiento"""
        if self.pagado:
            return 0

        delta = self.fecha_vencimiento - datetime.now()
        return max(0, delta.days)

    def marcar_como_pagado(self, fecha_pago: Optional[datetime] = None):
        """Marca la cuenta como pagada"""
        self.pagado = True
        self.fecha_pago = fecha_pago or datetime.now()
        self.updated_at = datetime.now()

    def esta_vencida(self) -> bool:
        """Verifica si la cuenta está vencida"""
        return not self.pagado and datetime.now() > self.fecha_vencimiento

    def esta_en_riesgo_corte(self) -> bool:
        """Verifica si la cuenta está en riesgo de corte"""
        if self.pagado or not self.fecha_corte:
            return False
        return datetime.now() >= self.fecha_corte

    def to_dict(self) -> dict:
        """Convierte la cuenta a diccionario para almacenamiento"""
        return {
            'id': self.id,
            'tipo_servicio': self.tipo_servicio.value,
            'descripcion': self.descripcion,
            'monto': self.monto,
            'fecha_emision': self.fecha_emision.isoformat() if self.fecha_emision else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'fecha_corte': self.fecha_corte.isoformat() if self.fecha_corte else None,
            'pagado': self.pagado,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'observaciones': self.observaciones,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CuentaServicio':
        """Crea una cuenta desde un diccionario"""
        cuenta = cls()
        cuenta.id = data.get('id')
        cuenta.tipo_servicio = TipoServicio(data.get('tipo_servicio', 'Luz'))
        cuenta.descripcion = data.get('descripcion', '')
        cuenta.monto = float(data.get('monto', 0))

        # Parsear fechas
        if data.get('fecha_emision'):
            cuenta.fecha_emision = datetime.fromisoformat(data['fecha_emision'])
        if data.get('fecha_vencimiento'):
            cuenta.fecha_vencimiento = datetime.fromisoformat(data['fecha_vencimiento'])
        if data.get('fecha_corte'):
            cuenta.fecha_corte = datetime.fromisoformat(data['fecha_corte'])
        if data.get('fecha_pago'):
            cuenta.fecha_pago = datetime.fromisoformat(data['fecha_pago'])
        if data.get('created_at'):
            cuenta.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            cuenta.updated_at = datetime.fromisoformat(data['updated_at'])

        cuenta.pagado = data.get('pagado', False)
        cuenta.observaciones = data.get('observaciones', '')

        return cuenta


@dataclass
class ResumenMensual:
    """Modelo para resúmenes mensuales"""
    mes: int
    año: int
    total_gastos: float = 0.0
    total_pagado: float = 0.0
    total_pendiente: float = 0.0
    cuentas_pagadas: int = 0
    cuentas_pendientes: int = 0
    cuentas_vencidas: int = 0
    cuentas_por_tipo: dict = None

    def __post_init__(self):
        if self.cuentas_por_tipo is None:
            self.cuentas_por_tipo = {}


def validar_cuenta(cuenta: CuentaServicio) -> List[str]:
    """Valida los datos de una cuenta y retorna lista de errores"""
    errores = []

    if not cuenta.descripcion.strip():
        errores.append("La descripción es obligatoria")

    if cuenta.monto <= 0:
        errores.append("El monto debe ser mayor a 0")

    if not cuenta.fecha_vencimiento:
        errores.append("La fecha de vencimiento es obligatoria")

    if cuenta.fecha_emision and cuenta.fecha_vencimiento:
        if cuenta.fecha_vencimiento <= cuenta.fecha_emision:
            errores.append("La fecha de vencimiento debe ser posterior a la fecha de emisión")

    if cuenta.fecha_corte and cuenta.fecha_vencimiento:
        if cuenta.fecha_corte <= cuenta.fecha_vencimiento:
            errores.append("La fecha de corte debe ser posterior a la fecha de vencimiento")

    return errores