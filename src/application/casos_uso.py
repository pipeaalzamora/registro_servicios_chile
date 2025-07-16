from typing import List, Optional
from datetime import datetime
from ..domain.entities import CuentaServicio, ResumenMensual, TipoServicio
from ..domain.repositories import CuentaServicioRepository, ResumenRepository

class GestionarCuentaServicio:
    """Caso de uso para gestionar cuentas de servicio"""

    def __init__(self, cuenta_repository: CuentaServicioRepository):
        self.cuenta_repository = cuenta_repository

    def crear_cuenta(self, tipo_servicio: TipoServicio, fecha_emision: datetime,
                    fecha_vencimiento: datetime, monto: float, descripcion: str,
                    observaciones: str = "") -> CuentaServicio:
        """Crea una nueva cuenta de servicio"""
        cuenta_id = f"{tipo_servicio.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        cuenta = CuentaServicio(
            id=cuenta_id,
            tipo_servicio=tipo_servicio,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            monto=monto,
            descripcion=descripcion,
            observaciones=observaciones
        )
        self.cuenta_repository.guardar(cuenta)
        return cuenta

    def obtener_cuenta(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene una cuenta por su ID"""
        return self.cuenta_repository.obtener_por_id(cuenta_id)

    def obtener_todas_las_cuentas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas"""
        return self.cuenta_repository.obtener_todas()

    def obtener_cuentas_por_tipo(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo de servicio"""
        return self.cuenta_repository.obtener_por_tipo(tipo)

    def obtener_cuentas_vencidas(self) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        return self.cuenta_repository.obtener_vencidas()

    def obtener_cuentas_pendientes(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes de pago"""
        return self.cuenta_repository.obtener_pendientes()

    def marcar_como_pagada(self, cuenta_id: str, fecha_pago: Optional[datetime] = None) -> bool:
        """Marca una cuenta como pagada"""
        cuenta = self.cuenta_repository.obtener_por_id(cuenta_id)
        if cuenta:
            cuenta.marcar_como_pagado(fecha_pago)
            return self.cuenta_repository.actualizar(cuenta)
        return False

    def actualizar_cuenta(self, cuenta: CuentaServicio) -> bool:
        """Actualiza una cuenta existente"""
        return self.cuenta_repository.actualizar(cuenta)

    def eliminar_cuenta(self, cuenta_id: str) -> bool:
        """Elimina una cuenta"""
        return self.cuenta_repository.eliminar(cuenta_id)

class GenerarReportes:
    """Caso de uso para generar reportes"""

    def __init__(self, cuenta_repository: CuentaServicioRepository,
                 resumen_repository: ResumenRepository):
        self.cuenta_repository = cuenta_repository
        self.resumen_repository = resumen_repository

    def generar_resumen_mensual(self, mes: int, año: int) -> ResumenMensual:
        """Genera un resumen mensual"""
        return self.resumen_repository.generar_resumen_mensual(mes, año)

    def obtener_resumenes_anuales(self, año: int) -> List[ResumenMensual]:
        """Obtiene resúmenes de un año completo"""
        return self.resumen_repository.obtener_resumenes_por_año(año)

    def obtener_cuentas_por_periodo(self, fecha_inicio: datetime,
                                  fecha_fin: datetime) -> List[CuentaServicio]:
        """Obtiene cuentas por período de tiempo"""
        return self.cuenta_repository.obtener_por_fecha(fecha_inicio, fecha_fin)

    def calcular_total_pendiente(self) -> float:
        """Calcula el total pendiente de pago"""
        cuentas_pendientes = self.cuenta_repository.obtener_pendientes()
        return sum(cuenta.monto for cuenta in cuentas_pendientes)

    def calcular_total_por_tipo(self, tipo: TipoServicio) -> float:
        """Calcula el total por tipo de servicio"""
        cuentas = self.cuenta_repository.obtener_por_tipo(tipo)
        return sum(cuenta.monto for cuenta in cuentas)

class Notificaciones:
    """Caso de uso para notificaciones"""

    def __init__(self, cuenta_repository: CuentaServicioRepository):
        self.cuenta_repository = cuenta_repository

    def obtener_cuentas_por_vencer(self, dias_limite: int = 7) -> List[CuentaServicio]:
        """Obtiene cuentas que vencen en los próximos días"""
        cuentas_pendientes = self.cuenta_repository.obtener_pendientes()
        return [cuenta for cuenta in cuentas_pendientes
                if cuenta.dias_para_vencer() <= dias_limite and cuenta.dias_para_vencer() > 0]

    def obtener_cuentas_vencidas_hoy(self) -> List[CuentaServicio]:
        """Obtiene cuentas que vencen hoy"""
        cuentas_pendientes = self.cuenta_repository.obtener_pendientes()
        return [cuenta for cuenta in cuentas_pendientes
                if cuenta.dias_para_vencer() == 0]