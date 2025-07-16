"""
Entidades del dominio de la aplicación
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List
import re


class TipoServicio(Enum):
    """Tipos de servicios disponibles"""
    LUZ = "Luz"
    AGUA = "Agua"
    GAS = "Gas"
    INTERNET = "Internet"
    GASTOS_COMUNES = "Gastos Comunes"


class TipoCambio(Enum):
    """Tipos de cambios en el historial"""
    CREACION = "Creación"
    PAGO = "Pago"
    EDICION = "Edición"
    ELIMINACION = "Eliminación"
    VENCIMIENTO = "Vencimiento"
    RIESGO_CORTE = "Riesgo de Corte"


@dataclass
class HistorialCambio:
    """Entidad para rastrear cambios en las cuentas"""
    id: str
    cuenta_id: str
    tipo_cambio: TipoCambio
    fecha_cambio: datetime
    descripcion: str
    datos_anteriores: Optional[dict] = None
    datos_nuevos: Optional[dict] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        if not self.descripcion:
            raise ValueError("La descripción no puede estar vacía")


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
        """Validaciones avanzadas después de la inicialización"""
        # Validar monto
        if self.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")

        if self.monto > 10000000:  # 10 millones de pesos
            raise ValueError("El monto no puede exceder $10,000,000")

        # Validar fechas
        if self.fecha_vencimiento <= self.fecha_emision:
            raise ValueError("La fecha de vencimiento debe ser posterior a la fecha de emisión")

        if self.fecha_emision > datetime.now() + timedelta(days=365):
            raise ValueError("La fecha de emisión no puede ser más de 1 año en el futuro")

        if self.fecha_emision < datetime.now() - timedelta(days=3650):
            raise ValueError("La fecha de emisión no puede ser más antigua de 10 años")

        # Validar fechas opcionales
        if self.fecha_proxima_lectura and self.fecha_proxima_lectura < self.fecha_emision:
            raise ValueError("La fecha de próxima lectura no puede ser anterior a la fecha de emisión")

        if self.fecha_corte and self.fecha_corte < self.fecha_emision:
            raise ValueError("La fecha de corte no puede ser anterior a la fecha de emisión")

        if self.fecha_corte and self.fecha_corte > self.fecha_vencimiento + timedelta(days=30):
            raise ValueError("La fecha de corte no puede ser más de 30 días después del vencimiento")

        # Validar descripción
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("La descripción no puede estar vacía")

        if len(self.descripcion.strip()) > 500:
            raise ValueError("La descripción no puede exceder 500 caracteres")

        # Validar que no contenga caracteres peligrosos
        if re.search(r'[<>"\']', self.descripcion):
            raise ValueError("La descripción no puede contener caracteres especiales como <, >, \", '")

        # Validar observaciones
        if len(self.observaciones) > 1000:
            raise ValueError("Las observaciones no pueden exceder 1000 caracteres")

        if re.search(r'[<>"\']', self.observaciones):
            raise ValueError("Las observaciones no pueden contener caracteres especiales como <, >, \", '")

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


@dataclass
class ResumenMensual:
    """Entidad para resumen mensual de gastos"""
    mes: int
    año: int
    total_luz: float = 0.0
    total_agua: float = 0.0
    total_gas: float = 0.0
    total_internet: float = 0.0
    total_gastos_comunes: float = 0.0

    @property
    def total_general(self) -> float:
        """Calcula el total general de todos los servicios"""
        return (self.total_luz + self.total_agua + self.total_gas +
                self.total_internet + self.total_gastos_comunes)

    def agregar_cuenta(self, cuenta: CuentaServicio):
        """Agrega una cuenta al resumen mensual"""
        if cuenta.fecha_emision.month == self.mes and cuenta.fecha_emision.year == self.año:
            if cuenta.tipo_servicio == TipoServicio.LUZ:
                self.total_luz += cuenta.monto
            elif cuenta.tipo_servicio == TipoServicio.AGUA:
                self.total_agua += cuenta.monto
            elif cuenta.tipo_servicio == TipoServicio.GAS:
                self.total_gas += cuenta.monto
            elif cuenta.tipo_servicio == TipoServicio.INTERNET:
                self.total_internet += cuenta.monto
            elif cuenta.tipo_servicio == TipoServicio.GASTOS_COMUNES:
                self.total_gastos_comunes += cuenta.monto