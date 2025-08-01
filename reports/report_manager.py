"""
Gestor unificado de reportes - Reemplaza reports.py
"""

from typing import List, Dict
from pathlib import Path

from models import CuentaServicio, ResumenMensual
from .monthly_report import MonthlyReportGenerator
from .annual_report import AnnualReportGenerator
from .type_report import TypeReportGenerator
from .chart_generator import ChartGenerator


class ReportManager:
    """Gestor unificado de reportes refactorizado"""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)

        # Inicializar generadores especializados
        self.monthly_generator = MonthlyReportGenerator(reports_dir)
        self.annual_generator = AnnualReportGenerator(reports_dir)
        self.type_generator = TypeReportGenerator(reports_dir)
        self.chart_generator = ChartGenerator(reports_dir)

    def generar_reporte_mensual(self, cuentas: List[CuentaServicio],
                               mes: int, año: int, custom_path: str = None) -> str:
        """Genera reporte mensual de cuentas"""
        return self.monthly_generator.generar_reporte_mensual(cuentas, mes, año, custom_path)

    def generar_reporte_anual(self, resumenes_mensuales: List[ResumenMensual],
                             año: int, custom_path: str = None) -> str:
        """Genera reporte anual"""
        return self.annual_generator.generar_reporte_anual(resumenes_mensuales, año, custom_path)

    def generar_reporte_por_tipo(self, cuentas_por_tipo: Dict[str, List[CuentaServicio]],
                                custom_path: str = None) -> str:
        """Genera reporte agrupado por tipo de servicio"""
        return self.type_generator.generar_reporte_por_tipo(cuentas_por_tipo, custom_path)

    def crear_grafico_gastos_mensuales(self, resumenes: List[ResumenMensual],
                                     año: int, custom_path: str = None) -> str:
        """Crea gráfico de gastos mensuales"""
        return self.chart_generator.crear_grafico_gastos_mensuales(resumenes, año, custom_path)

    def crear_grafico_por_tipo(self, totales_por_tipo: Dict[str, float], custom_path: str = None) -> str:
        """Crea gráfico de gastos por tipo de servicio"""
        return self.chart_generator.crear_grafico_por_tipo(totales_por_tipo, custom_path)


# Mantener compatibilidad con código existente
ReportGenerator = ReportManager