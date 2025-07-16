"""
Entidades del dominio de la aplicación
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
import re

from .validators import CuentaServicioValidator


class TipoServicio(Enum):
    """Tipos de servicios disponibles"""
    LUZ = "Luz"
    AGUA = "Agua"
    GAS = "Gas"
    INTERNET = "Internet"
    TELEFONO = "Teléfono"
    BASURA = "Basura"
    OTRO = "Otro"


class TipoCambio(Enum):
    """Tipos de cambios en el historial"""
    PAGO = "Pago"
    EDICION = "Edición"
    VENCIMIENTO = "Vencimiento"
    RIESGO_CORTE = "Riesgo de Corte"


@dataclass
class HistorialCambio:
    """Entidad para registrar cambios en las cuentas"""
    id: str
    cuenta_id: str
    tipo_cambio: TipoCambio
    fecha_cambio: datetime
    descripcion: str
    datos_anteriores: Optional[dict] = None
    datos_nuevos: Optional[dict] = None


@dataclass
class ResumenMensual:
    """Entidad para resúmenes mensuales"""
    mes: int
    año: int
    total_gastos: float = 0.0
    total_pagado: float = 0.0
    total_pendiente: float = 0.0
    cuentas_pagadas: int = 0
    cuentas_pendientes: int = 0
    cuentas_vencidas: int = 0

    def agregar_cuenta(self, cuenta):
        """Agrega una cuenta al resumen"""
        self.total_gastos += cuenta.monto
        if cuenta.pagado:
            self.total_pagado += cuenta.monto
            self.cuentas_pagadas += 1
        else:
            self.total_pendiente += cuenta.monto
            self.cuentas_pendientes += 1
            if cuenta.esta_vencida():
                self.cuentas_vencidas += 1


@dataclass
class CuentaServicio:
    """Entidad principal para representar una cuenta de servicio"""
    id: str
    tipo_servicio: TipoServicio
    fecha_emision: datetime
    fecha_vencimiento: datetime
    monto: float
    descripcion: str
    pagado: bool = False
    fecha_pago: Optional[datetime] = None
    observaciones: str = ""
    fecha_proxima_lectura: Optional[datetime] = None
    fecha_corte: Optional[datetime] = None
    historial: Optional[List[HistorialCambio]] = None

    def __post_init__(self):
        """Validaciones usando el validador centralizado"""
        # Usar el validador centralizado
        errores = CuentaServicioValidator.validar_cuenta_completa(
            tipo_servicio=self.tipo_servicio,
            fecha_emision=self.fecha_emision,
            fecha_vencimiento=self.fecha_vencimiento,
            monto=self.monto,
            descripcion=self.descripcion,
            observaciones=self.observaciones,
            fecha_proxima_lectura=self.fecha_proxima_lectura,
            fecha_corte=self.fecha_corte
        )

        if errores:
            raise ValueError("; ".join(errores))

        if self.historial is None:
            self.historial = []

    def marcar_como_pagado(self, fecha_pago: Optional[datetime] = None):
        """Marca la cuenta como pagada"""
        if not self.pagado:
            self.pagado = True
            self.fecha_pago = fecha_pago or datetime.now()

            # Agregar al historial
            cambio = HistorialCambio(
                id=f"hist_{self.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                cuenta_id=self.id,
                tipo_cambio=TipoCambio.PAGO,
                fecha_cambio=datetime.now(),
                descripcion=f"Cuenta marcada como pagada - Monto: ${self.monto:,.0f}",
                datos_anteriores={"pagado": False, "fecha_pago": None},
                datos_nuevos={"pagado": True, "fecha_pago": self.fecha_pago.isoformat()}
            )
            if self.historial is not None:
                self.historial.append(cambio)

    def esta_vencida(self) -> bool:
        """Verifica si la cuenta está vencida"""
        return not self.pagado and datetime.now() > self.fecha_vencimiento

    def dias_para_vencer(self) -> int:
        """Calcula los días restantes para el vencimiento"""
        if self.pagado:
            return 0
        delta = self.fecha_vencimiento - datetime.now()
        return max(0, delta.days)

    def esta_en_riesgo_corte(self) -> bool:
        """Verifica si la cuenta está en riesgo de corte"""
        if self.pagado or not self.fecha_corte:
            return False
        return datetime.now() >= self.fecha_corte

    def get_estado(self) -> str:
        """Devuelve el estado textual de la cuenta"""
        if self.pagado:
            return "Pagado"
        elif self.esta_vencida():
            return "Vencido"
        elif self.esta_en_riesgo_corte():
            return "En Riesgo de Corte"
        else:
            return "Pendiente"

    def agregar_cambio_historial(self, tipo_cambio: TipoCambio, descripcion: str,
                               datos_anteriores: Optional[dict] = None,
                               datos_nuevos: Optional[dict] = None):
        """Agrega un cambio al historial"""
        cambio = HistorialCambio(
            id=f"hist_{self.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            cuenta_id=self.id,
            tipo_cambio=tipo_cambio,
            fecha_cambio=datetime.now(),
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
        if self.historial is not None:
            self.historial.append(cambio)