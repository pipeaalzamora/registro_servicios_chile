"""
Gestor de estadísticas y reportes
"""

from typing import Dict
from models import ResumenMensual


class StatisticsManager:
    """Maneja estadísticas y resúmenes de datos"""

    def __init__(self, crud_operations, query_operations):
        self.crud_operations = crud_operations
        self.query_operations = query_operations

    def obtener_resumen_mensual(self, mes: int, año: int) -> ResumenMensual:
        """Genera resumen mensual"""
        cuentas_mes = self.query_operations.obtener_cuentas_por_mes(mes, año)

        total_cuentas = len(cuentas_mes)
        total_gastos = sum(cuenta.monto for cuenta in cuentas_mes)

        cuentas_pagadas = [cuenta for cuenta in cuentas_mes if cuenta.pagado]
        total_pagado = sum(cuenta.monto for cuenta in cuentas_pagadas)

        cuentas_pendientes = [cuenta for cuenta in cuentas_mes if not cuenta.pagado]
        total_pendiente = sum(cuenta.monto for cuenta in cuentas_pendientes)

        # Crear resumen
        resumen = ResumenMensual(
            mes=mes,
            año=año,
            total_cuentas=total_cuentas,
            total_gastos=total_gastos,
            cuentas_pagadas=len(cuentas_pagadas),
            total_pagado=total_pagado,
            cuentas_pendientes=len(cuentas_pendientes),
            total_pendiente=total_pendiente,
            cuentas_vencidas=0  # Se calculará después
        )

        return resumen

    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales"""
        todas_las_cuentas = self.crud_operations.obtener_todas_las_cuentas()

        total_cuentas = len(todas_las_cuentas)
        total_gastos = sum(cuenta.monto for cuenta in todas_las_cuentas)

        cuentas_pagadas = [cuenta for cuenta in todas_las_cuentas if cuenta.pagado]
        total_pagado = sum(cuenta.monto for cuenta in cuentas_pagadas)

        cuentas_pendientes = [cuenta for cuenta in todas_las_cuentas if not cuenta.pagado]
        total_pendiente = sum(cuenta.monto for cuenta in cuentas_pendientes)

        cuentas_vencidas = self.query_operations.obtener_cuentas_vencidas(self.crud_operations)

        return {
            'total_cuentas': total_cuentas,
            'total_gastos': total_gastos,
            'cuentas_pagadas': len(cuentas_pagadas),
            'total_pagado': total_pagado,
            'cuentas_pendientes': len(cuentas_pendientes),
            'total_pendiente': total_pendiente,
            'cuentas_vencidas': len(cuentas_vencidas)
        }

    def obtener_estadisticas_por_tipo(self) -> Dict[str, Dict]:
        """Obtiene estadísticas detalladas por tipo de servicio"""
        todas_las_cuentas = self.crud_operations.obtener_todas_las_cuentas()
        estadisticas = {}

        # Agrupar por tipo
        for cuenta in todas_las_cuentas:
            tipo = cuenta.tipo_servicio.value
            if tipo not in estadisticas:
                estadisticas[tipo] = {
                    'total_cuentas': 0,
                    'total_monto': 0,
                    'cuentas_pagadas': 0,
                    'monto_pagado': 0,
                    'cuentas_pendientes': 0,
                    'monto_pendiente': 0
                }

            stats = estadisticas[tipo]
            stats['total_cuentas'] += 1
            stats['total_monto'] += cuenta.monto

            if cuenta.pagado:
                stats['cuentas_pagadas'] += 1
                stats['monto_pagado'] += cuenta.monto
            else:
                stats['cuentas_pendientes'] += 1
                stats['monto_pendiente'] += cuenta.monto

        return estadisticas

    def obtener_tendencias_mensuales(self, año: int) -> Dict[int, Dict]:
        """Obtiene tendencias mensuales para un año específico"""
        tendencias = {}

        for mes in range(1, 13):
            cuentas_mes = self.query_operations.obtener_cuentas_por_mes(mes, año)

            tendencias[mes] = {
                'total_cuentas': len(cuentas_mes),
                'total_gastos': sum(cuenta.monto for cuenta in cuentas_mes),
                'cuentas_pagadas': len([c for c in cuentas_mes if c.pagado]),
                'cuentas_pendientes': len([c for c in cuentas_mes if not c.pagado])
            }

        return tendencias