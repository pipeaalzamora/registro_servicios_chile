from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .entities import CuentaServicio, ResumenMensual, TipoServicio

class CuentaServicioRepository(ABC):
    """Interfaz del repositorio para cuentas de servicio"""

    @abstractmethod
    def guardar(self, cuenta: CuentaServicio) -> None:
        """Guarda una cuenta de servicio"""
        pass

    @abstractmethod
    def obtener_por_id(self, id: str) -> Optional[CuentaServicio]:
        """Obtiene una cuenta por su ID"""
        pass

    @abstractmethod
    def obtener_todas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas"""
        pass

    @abstractmethod
    def obtener_por_tipo(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo de servicio"""
        pass

    @abstractmethod
    def obtener_por_fecha(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[CuentaServicio]:
        """Obtiene cuentas por rango de fechas"""
        pass

    @abstractmethod
    def obtener_vencidas(self) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        pass

    @abstractmethod
    def obtener_pendientes(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes de pago"""
        pass

    @abstractmethod
    def eliminar(self, id: str) -> bool:
        """Elimina una cuenta por su ID"""
        pass

    @abstractmethod
    def actualizar(self, cuenta: CuentaServicio) -> bool:
        """Actualiza una cuenta existente"""
        pass

class ResumenRepository(ABC):
    """Interfaz del repositorio para resúmenes"""

    @abstractmethod
    def generar_resumen_mensual(self, mes: int, año: int) -> ResumenMensual:
        """Genera un resumen mensual"""
        pass

    @abstractmethod
    def obtener_resumenes_por_año(self, año: int) -> List[ResumenMensual]:
        """Obtiene todos los resúmenes de un año"""
        pass