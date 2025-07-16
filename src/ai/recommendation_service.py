"""
Servicio de recomendaciones inteligentes para optimizar gastos
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import json
from pathlib import Path

from ..domain.entities import CuentaServicio, TipoServicio


@dataclass
class Recommendation:
    """Estructura para recomendaciones"""
    tipo: str  # 'ahorro', 'optimizacion', 'alerta', 'tendencia'
    titulo: str
    descripcion: str
    impacto: float  # 0-100, qué tan importante es
    accion: str
    prioridad: str  # 'alta', 'media', 'baja'


class RecommendationService:
    """Servicio de recomendaciones inteligentes"""

    def __init__(self):
        # Umbrales para análisis
        self.umbrales = {
            'incremento_significativo': 0.15,  # 15% de incremento
            'decremento_significativo': -0.10,  # 10% de decremento
            'consumo_alto': 0.8,  # Percentil 80
            'consumo_bajo': 0.2,  # Percentil 20
            'vencimiento_critico': 3,  # Días antes del vencimiento
            'riesgo_corte': 5,  # Días antes del corte
        }

    def analyze_spending_patterns(self, cuentas: List[CuentaServicio]) -> Dict[str, Any]:
        """Analiza patrones de gasto para generar recomendaciones"""
        if not cuentas:
            return {'error': 'No hay datos para analizar'}

        # Agrupar por tipo de servicio
        cuentas_por_tipo = {}
        for cuenta in cuentas:
            tipo = cuenta.tipo_servicio.value
            if tipo not in cuentas_por_tipo:
                cuentas_por_tipo[tipo] = []
            cuentas_por_tipo[tipo].append(cuenta)

        # Análisis por tipo de servicio
        analisis_por_tipo = {}
        for tipo, cuentas_tipo in cuentas_por_tipo.items():
            if len(cuentas_tipo) < 3:
                continue

            # Ordenar por fecha
            cuentas_tipo.sort(key=lambda x: x.fecha_emision)

            # Calcular estadísticas
            montos = [c.monto for c in cuentas_tipo]
            fechas = [c.fecha_emision for c in cuentas_tipo]

            # Análisis de tendencia
            x = np.arange(len(montos))
            if len(montos) > 1:
                z = np.polyfit(x, montos, 1)
                tendencia = z[0]
                porcentaje_cambio = ((montos[-1] - montos[0]) / montos[0] * 100) if montos[0] > 0 else 0
            else:
                tendencia = 0
                porcentaje_cambio = 0

            # Análisis de volatilidad
            if len(montos) > 1:
                returns = np.diff(montos) / montos[:-1]
                volatilidad = np.std(returns)
            else:
                volatilidad = 0

            # Análisis de estacionalidad
            montos_por_mes = {}
            for cuenta in cuentas_tipo:
                mes = cuenta.fecha_emision.month
                if mes not in montos_por_mes:
                    montos_por_mes[mes] = []
                montos_por_mes[mes].append(cuenta.monto)

            # Meses con mayor y menor consumo
            meses_consumo = {mes: np.mean(montos) for mes, montos in montos_por_mes.items()}
            mes_max_consumo = max(meses_consumo.items(), key=lambda x: x[1]) if meses_consumo else None
            mes_min_consumo = min(meses_consumo.items(), key=lambda x: x[1]) if meses_consumo else None

            analisis_por_tipo[tipo] = {
                'total_cuentas': len(cuentas_tipo),
                'promedio_actual': np.mean(montos),
                'mediana': np.median(montos),
                'tendencia': tendencia,
                'porcentaje_cambio': porcentaje_cambio,
                'volatilidad': volatilidad,
                'mes_max_consumo': mes_max_consumo,
                'mes_min_consumo': mes_min_consumo,
                'ultimo_monto': montos[-1] if montos else 0,
                'primer_monto': montos[0] if montos else 0
            }

        return {
            'analisis_por_tipo': analisis_por_tipo,
            'total_cuentas': len(cuentas),
            'tipos_servicios': list(analisis_por_tipo.keys())
        }

    def generate_recommendations(self, cuentas: List[CuentaServicio]) -> List[Recommendation]:
        """Genera recomendaciones inteligentes basadas en el análisis"""
        recomendaciones = []

        # Análisis de patrones
        analisis = self.analyze_spending_patterns(cuentas)
        if 'error' in analisis:
            return recomendaciones

        # 1. Análisis de tendencias por servicio
        for tipo, datos in analisis['analisis_por_tipo'].items():
            # Detectar incrementos significativos
            if datos['porcentaje_cambio'] > (self.umbrales['incremento_significativo'] * 100):
                recomendaciones.append(Recommendation(
                    tipo='alerta',
                    titulo=f'⚠️ Incremento significativo en {tipo}',
                    descripcion=f'El {tipo} ha aumentado un {datos["porcentaje_cambio"]:.1f}% en el período analizado. '
                               f'Considera revisar tu consumo o buscar alternativas.',
                    impacto=min(100, datos['porcentaje_cambio'] * 2),
                    accion='Revisar consumo y buscar optimizaciones',
                    prioridad='alta' if datos['porcentaje_cambio'] > 25 else 'media'
                ))

            # Detectar decrementos significativos
            elif datos['porcentaje_cambio'] < (self.umbrales['decremento_significativo'] * 100):
                recomendaciones.append(Recommendation(
                    tipo='ahorro',
                    titulo=f'✅ Ahorro detectado en {tipo}',
                    descripcion=f'¡Excelente! El {tipo} ha disminuido un {abs(datos["porcentaje_cambio"]):.1f}%. '
                               f'Mantén estas buenas prácticas.',
                    impacto=50,
                    accion='Mantener hábitos de consumo eficiente',
                    prioridad='baja'
                ))

            # Análisis de estacionalidad
            if datos['mes_max_consumo'] and datos['mes_min_consumo']:
                mes_max, monto_max = datos['mes_max_consumo']
                mes_min, monto_min = datos['mes_min_consumo']
                variacion_estacional = ((monto_max - monto_min) / monto_min * 100) if monto_min > 0 else 0

                if variacion_estacional > 30:
                    recomendaciones.append(Recommendation(
                        tipo='optimizacion',
                        titulo=f'📅 Patrón estacional detectado en {tipo}',
                        descripcion=f'El consumo varía significativamente entre meses. '
                                   f'Mayor consumo en mes {mes_max} (${monto_max:,.0f}) vs mes {mes_min} (${monto_min:,.0f}).',
                        impacto=60,
                        accion='Planificar consumo según estacionalidad',
                        prioridad='media'
                    ))

        # 2. Análisis de cuentas por vencer
        cuentas_por_vencer = self._get_cuentas_por_vencer(cuentas)
        if cuentas_por_vencer:
            total_por_vencer = sum(c.monto for c in cuentas_por_vencer)
            recomendaciones.append(Recommendation(
                tipo='alerta',
                titulo=f'📅 {len(cuentas_por_vencer)} cuenta(s) por vencer',
                descripcion=f'Tienes {len(cuentas_por_vencer)} cuenta(s) que vencen pronto por un total de ${total_por_vencer:,.0f}.',
                impacto=80,
                accion='Revisar y pagar cuentas pendientes',
                prioridad='alta'
            ))

        # 3. Análisis de cuentas en riesgo de corte
        cuentas_riesgo = self._get_cuentas_riesgo_corte(cuentas)
        if cuentas_riesgo:
            recomendaciones.append(Recommendation(
                tipo='alerta',
                titulo=f'🚨 {len(cuentas_riesgo)} cuenta(s) en riesgo de corte',
                descripcion=f'Las siguientes cuentas están próximas al corte: {", ".join([c.tipo_servicio.value for c in cuentas_riesgo])}.',
                impacto=100,
                accion='Pagar inmediatamente para evitar corte',
                prioridad='alta'
            ))

        # 4. Análisis de optimización de gastos
        optimizacion = self._analyze_optimization_opportunities(cuentas)
        if optimizacion:
            recomendaciones.append(Recommendation(
                tipo='optimizacion',
                titulo='💡 Oportunidades de optimización',
                descripcion=optimizacion['descripcion'],
                impacto=optimizacion['impacto'],
                accion=optimizacion['accion'],
                prioridad='media'
            ))

        # 5. Análisis de consistencia en pagos
        consistencia = self._analyze_payment_consistency(cuentas)
        if consistencia:
            recomendaciones.append(Recommendation(
                tipo='optimizacion',
                titulo='📊 Análisis de consistencia en pagos',
                descripcion=consistencia['descripcion'],
                impacto=consistencia['impacto'],
                accion=consistencia['accion'],
                prioridad='baja'
            ))

        # Ordenar por impacto y prioridad
        recomendaciones.sort(key=lambda r: (r.impacto, {'alta': 3, 'media': 2, 'baja': 1}[r.prioridad]), reverse=True)

        return recomendaciones

    def _get_cuentas_por_vencer(self, cuentas: List[CuentaServicio]) -> List[CuentaServicio]:
        """Obtiene cuentas que vencen pronto"""
        hoy = datetime.now()
        return [
            c for c in cuentas
            if not c.pagado and
            (c.fecha_vencimiento - hoy).days <= self.umbrales['vencimiento_critico'] and
            (c.fecha_vencimiento - hoy).days > 0
        ]

    def _get_cuentas_riesgo_corte(self, cuentas: List[CuentaServicio]) -> List[CuentaServicio]:
        """Obtiene cuentas en riesgo de corte"""
        hoy = datetime.now()
        return [
            c for c in cuentas
            if not c.pagado and
            c.fecha_corte and
            (c.fecha_corte - hoy).days <= self.umbrales['riesgo_corte'] and
            (c.fecha_corte - hoy).days > 0
        ]

    def _analyze_optimization_opportunities(self, cuentas: List[CuentaServicio]) -> Optional[Dict[str, Any]]:
        """Analiza oportunidades de optimización"""
        if not cuentas:
            return None

        # Agrupar por tipo de servicio
        cuentas_por_tipo = {}
        for cuenta in cuentas:
            tipo = cuenta.tipo_servicio.value
            if tipo not in cuentas_por_tipo:
                cuentas_por_tipo[tipo] = []
            cuentas_por_tipo[tipo].append(cuenta)

        oportunidades = []
        impacto_total = 0

        for tipo, cuentas_tipo in cuentas_por_tipo.items():
            if len(cuentas_tipo) < 3:
                continue

            montos = [c.monto for c in cuentas_tipo]
            promedio = np.mean(montos)
            ultimo_monto = montos[-1] if montos else 0

            # Detectar si el último monto es significativamente mayor al promedio
            if ultimo_monto > promedio * 1.2:  # 20% más que el promedio
                diferencia = ultimo_monto - promedio
                oportunidades.append(f"{tipo}: ${diferencia:,.0f} sobre el promedio")
                impacto_total += diferencia

        if oportunidades:
            return {
                'descripcion': f'Posibles optimizaciones detectadas: {"; ".join(oportunidades)}. '
                              f'Potencial ahorro: ${impacto_total:,.0f}.',
                'impacto': min(100.0, float(impacto_total / 1000)),  # Normalizar impacto
                'accion': 'Revisar consumo reciente vs histórico'
            }

        return None

    def _analyze_payment_consistency(self, cuentas: List[CuentaServicio]) -> Optional[Dict[str, Any]]:
        """Analiza la consistencia en los pagos"""
        cuentas_pagadas = [c for c in cuentas if c.pagado and c.fecha_pago]

        if len(cuentas_pagadas) < 5:
            return None

        # Calcular días promedio de pago después del vencimiento
        dias_retraso = []
        for cuenta in cuentas_pagadas:
            if cuenta.fecha_pago and cuenta.fecha_vencimiento:
                dias = (cuenta.fecha_pago - cuenta.fecha_vencimiento).days
                dias_retraso.append(dias)

        if not dias_retraso:
            return None

        promedio_retraso = np.mean(dias_retraso)
        pagos_a_tiempo = sum(1 for dias in dias_retraso if dias <= 0)
        porcentaje_a_tiempo = (pagos_a_tiempo / len(dias_retraso)) * 100

        if promedio_retraso > 5:
            return {
                'descripcion': f'Promedio de retraso en pagos: {promedio_retraso:.1f} días. '
                              f'Solo {porcentaje_a_tiempo:.1f}% de pagos a tiempo.',
                'impacto': min(100.0, float(promedio_retraso * 5)),
                'accion': 'Configurar recordatorios automáticos y pagos programados'
            }
        elif porcentaje_a_tiempo < 70:
            return {
                'descripcion': f'Consistencia en pagos: {porcentaje_a_tiempo:.1f}% a tiempo. '
                              f'Promedio de retraso: {promedio_retraso:.1f} días.',
                'impacto': 40,
                'accion': 'Mejorar consistencia en fechas de pago'
            }

        return None

    def get_savings_forecast(self, cuentas: List[CuentaServicio], meses: int = 6) -> Dict[str, Any]:
        """Predice ahorros potenciales basado en patrones históricos"""
        if not cuentas:
            return {'error': 'No hay datos para predicción'}

        analisis = self.analyze_spending_patterns(cuentas)
        if 'error' in analisis:
            return analisis

        ahorros_proyectados = {}
        total_ahorro = 0

        for tipo, datos in analisis['analisis_por_tipo'].items():
            # Si hay tendencia de incremento, proyectar ahorro potencial
            if datos['tendencia'] > 0:
                # Proyectar el incremento para los próximos meses
                incremento_proyectado = datos['tendencia'] * meses
                ahorro_potencial = incremento_proyectado * 0.5  # Asumir 50% de optimización posible

                ahorros_proyectados[tipo] = {
                    'incremento_proyectado': incremento_proyectado,
                    'ahorro_potencial': ahorro_potencial,
                    'impacto': 'alto' if incremento_proyectado > datos['promedio_actual'] * 0.2 else 'medio'
                }
                total_ahorro += ahorro_potencial

        return {
            'ahorros_proyectados': ahorros_proyectados,
            'total_ahorro_potencial': total_ahorro,
            'periodo_meses': meses,
            'recomendacion': 'Implementar medidas de optimización para capturar ahorros proyectados'
        }

    def get_priority_actions(self, cuentas: List[CuentaServicio]) -> List[Dict[str, Any]]:
        """Obtiene acciones prioritarias basadas en el análisis"""
        recomendaciones = self.generate_recommendations(cuentas)

        # Filtrar solo recomendaciones de alta prioridad
        acciones_prioritarias = [
            {
                'titulo': rec.titulo,
                'descripcion': rec.descripcion,
                'accion': rec.accion,
                'impacto': rec.impacto,
                'tipo': rec.tipo
            }
            for rec in recomendaciones
            if rec.prioridad == 'alta'
        ]

        return acciones_prioritarias[:5]  # Top 5 acciones


# Instancia global del servicio de recomendaciones
recommendation_service = RecommendationService()