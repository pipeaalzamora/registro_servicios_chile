"""
Generador de reportes por tipo de servicio
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from models import CuentaServicio
from .base_report import BaseReportGenerator


class TypeReportGenerator(BaseReportGenerator):
    """Generador de reportes por tipo de servicio"""

    def generar_reporte_por_tipo(self, cuentas_por_tipo: Dict[str, List[CuentaServicio]],
                                custom_path: str = None) -> str:
        """Genera reporte agrupado por tipo de servicio"""
        if custom_path:
            filepath = Path(custom_path)
        else:
            filename = f"reporte_por_tipo_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = self.reports_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4))
        story = []

        # Título
        title = "Reporte por Tipo de Servicio"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        for tipo, cuentas in cuentas_por_tipo.items():
            if cuentas:  # Solo mostrar tipos con cuentas
                story.append(Paragraph(f"Servicio: {tipo}", self.styles['CustomHeading']))
                story.extend(self._crear_tabla_cuentas(cuentas))
                story.append(Spacer(1, 15))

        doc.build(story)
        return str(filepath)