"""
Generador de reportes mensuales
"""

from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from pathlib import Path
from typing import List

from models import CuentaServicio
from .base_report import BaseReportGenerator


class MonthlyReportGenerator(BaseReportGenerator):
    """Generador de reportes mensuales"""

    def generar_reporte_mensual(self, cuentas: List[CuentaServicio],
                               mes: int, año: int, custom_path: str = None) -> str:
        """Genera reporte mensual de cuentas"""
        if custom_path:
            filepath = Path(custom_path)
        else:
            filename = f"reporte_mensual_{año}_{mes:02d}.pdf"
            filepath = self.reports_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4))
        story = []

        # Título
        title = f"Reporte Mensual de Servicios - {mes}/{año}"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        # Resumen estadístico
        story.extend(self._crear_resumen_estadistico(cuentas))
        story.append(Spacer(1, 20))

        # Tabla de cuentas
        story.extend(self._crear_tabla_cuentas(cuentas))

        # Construir PDF
        doc.build(story)
        return str(filepath)