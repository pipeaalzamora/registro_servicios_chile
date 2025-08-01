"""
Generador de reportes anuales
"""

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4, landscape
from pathlib import Path
from typing import List

from models import ResumenMensual
from .base_report import BaseReportGenerator


class AnnualReportGenerator(BaseReportGenerator):
    """Generador de reportes anuales"""

    def generar_reporte_anual(self, resumenes_mensuales: List[ResumenMensual],
                             año: int, custom_path: str = None) -> str:
        """Genera reporte anual"""
        if custom_path:
            filepath = Path(custom_path)
        else:
            filename = f"reporte_anual_{año}.pdf"
            filepath = self.reports_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=landscape(A4))
        story = []

        # Título
        title = f"Reporte Anual de Servicios - {año}"
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))

        # Resumen anual
        story.extend(self._crear_resumen_anual(resumenes_mensuales, año))

        # Tabla mensual
        story.extend(self._crear_tabla_mensual(resumenes_mensuales))

        doc.build(story)
        return str(filepath)

    def _crear_resumen_anual(self, resumenes: List[ResumenMensual], año: int) -> List:
        """Crea resumen anual"""
        elements = []

        total_anual = sum(r.total_gastos for r in resumenes)
        total_pagado_anual = sum(r.total_pagado for r in resumenes)
        total_pendiente_anual = sum(r.total_pendiente for r in resumenes)

        data = [
            ['Concepto', 'Monto (CLP)'],
            ['Total Gastos del Año', f"${total_anual:,.0f}"],
            ['Total Pagado', f"${total_pagado_anual:,.0f}"],
            ['Total Pendiente', f"${total_pendiente_anual:,.0f}"],
            ['Promedio Mensual', f"${total_anual/12:,.0f}"]
        ]

        table = Table(data, colWidths=[2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(Paragraph(f"Resumen Anual {año}", self.styles['CustomHeading']))
        elements.append(table)

        return elements

    def _crear_tabla_mensual(self, resumenes: List[ResumenMensual]) -> List:
        """Crea tabla con resumen mensual"""
        elements = []

        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        data = [['Mes', 'Total Gastos', 'Pagado', 'Pendiente', 'Cuentas']]

        for resumen in resumenes:
            if resumen.total_gastos > 0:  # Solo mostrar meses con gastos
                data.append([
                    meses[resumen.mes - 1],
                    f"${resumen.total_gastos:,.0f}",
                    f"${resumen.total_pagado:,.0f}",
                    f"${resumen.total_pendiente:,.0f}",
                    str(resumen.cuentas_pagadas + resumen.cuentas_pendientes)
                ])

        if len(data) > 1:  # Si hay datos además del encabezado
            table = Table(data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))

            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Resumen por Mes", self.styles['CustomHeading']))
            elements.append(table)

        return elements