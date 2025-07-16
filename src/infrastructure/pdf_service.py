from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import List
from pathlib import Path

from ..domain.entities import CuentaServicio, ResumenMensual, TipoServicio

class PDFService:
    """Servicio para generar reportes en PDF"""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()

    def generar_reporte_cuentas(self, cuentas: List[CuentaServicio],
                              titulo: str = "Reporte de Cuentas") -> str:
        """Genera un reporte PDF con las cuentas especificadas"""
        filename = f"reporte_cuentas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = self.reports_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(titulo, title_style))
        story.append(Spacer(1, 20))

        # Tabla de cuentas
        if cuentas:
            data = [['Servicio', 'Emisión', 'Vencimiento', 'Próxima Lectura', 'Fecha Corte', 'Monto', 'Estado', 'Descripción']]

            for cuenta in cuentas:
                estado = "Pagado" if cuenta.pagado else "Pendiente"
                if cuenta.esta_vencida():
                    estado = "Vencido"
                elif cuenta.esta_en_riesgo_corte():
                    estado = "En Riesgo de Corte"

                # Formatear fechas opcionales
                proxima_lectura = cuenta.fecha_proxima_lectura.strftime('%d/%m/%Y') if cuenta.fecha_proxima_lectura else "-"
                fecha_corte = cuenta.fecha_corte.strftime('%d/%m/%Y') if cuenta.fecha_corte else "-"

                data.append([
                    cuenta.tipo_servicio.value,
                    cuenta.fecha_emision.strftime('%d/%m/%Y'),
                    cuenta.fecha_vencimiento.strftime('%d/%m/%Y'),
                    proxima_lectura,
                    fecha_corte,
                    f"${cuenta.monto:,.0f}",
                    estado,
                    cuenta.descripcion[:30] + "..." if len(cuenta.descripcion) > 30 else cuenta.descripcion
                ])

            table = Table(data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.7*inch, 0.7*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (5, 1), (5, -1), 'RIGHT'),  # Alinear montos a la derecha
                ('FONTSIZE', (0, 1), (-1, -1), 8),  # Texto más pequeño para las filas
            ]))

            story.append(table)
        else:
            story.append(Paragraph("No hay cuentas para mostrar", self.styles['Normal']))

        # Resumen
        story.append(Spacer(1, 20))
        total_pendiente = sum(c.monto for c in cuentas if not c.pagado)
        total_pagado = sum(c.monto for c in cuentas if c.pagado)
        cuentas_vencidas = len([c for c in cuentas if c.esta_vencida()])
        cuentas_riesgo = len([c for c in cuentas if c.esta_en_riesgo_corte()])

        resumen_data = [
            ['Resumen', ''],
            ['Total Pendiente', f"${total_pendiente:,.0f}"],
            ['Total Pagado', f"${total_pagado:,.0f}"],
            ['Total General', f"${total_pendiente + total_pagado:,.0f}"],
            ['Cuentas Vencidas', f"{cuentas_vencidas}"],
            ['En Riesgo de Corte', f"{cuentas_riesgo}"]
        ]

        resumen_table = Table(resumen_data, colWidths=[2*inch, 1*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Alinear montos a la derecha
        ]))

        story.append(resumen_table)

        # Pie de página
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", footer_style))

        doc.build(story)
        return str(filepath)

    def generar_reporte_resumen_mensual(self, resumen: ResumenMensual) -> str:
        """Genera un reporte PDF del resumen mensual"""
        filename = f"resumen_mensual_{resumen.año}_{resumen.mes:02d}.pdf"
        filepath = self.reports_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        mes_nombre = datetime(resumen.año, resumen.mes, 1).strftime('%B %Y')
        story.append(Paragraph(f"Resumen Mensual - {mes_nombre}", title_style))
        story.append(Spacer(1, 20))

        # Tabla de resumen por servicio
        data = [
            ['Servicio', 'Monto'],
            ['Luz', f"${resumen.total_luz:,.0f}"],
            ['Agua', f"${resumen.total_agua:,.0f}"],
            ['Gas', f"${resumen.total_gas:,.0f}"],
            ['Internet', f"${resumen.total_internet:,.0f}"],
            ['Gastos Comunes', f"${resumen.total_gastos_comunes:,.0f}"],
            ['', ''],
            ['TOTAL GENERAL', f"${resumen.total_general:,.0f}"]
        ]

        table = Table(data, colWidths=[3*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),  # Total general
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
            ('BACKGROUND', (0, -2), (-1, -1), colors.lightblue),  # Total general
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Alinear montos a la derecha
        ]))

        story.append(table)

        # Pie de página
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", footer_style))

        doc.build(story)
        return str(filepath)

    def generar_reporte_anual(self, resumenes: List[ResumenMensual], año: int) -> str:
        """Genera un reporte PDF anual con todos los meses"""
        filename = f"reporte_anual_{año}.pdf"
        filepath = self.reports_dir / filename

        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        story = []

        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph(f"Reporte Anual {año}", title_style))
        story.append(Spacer(1, 20))

        # Tabla anual
        data = [['Mes', 'Luz', 'Agua', 'Gas', 'Internet', 'Gastos Comunes', 'Total']]

        total_anual = {
            'luz': 0.0, 'agua': 0.0, 'gas': 0.0, 'internet': 0.0,
            'gastos_comunes': 0.0, 'total': 0.0
        }

        for resumen in resumenes:
            mes_nombre = datetime(resumen.año, resumen.mes, 1).strftime('%B')
            data.append([
                mes_nombre,
                f"${resumen.total_luz:,.0f}",
                f"${resumen.total_agua:,.0f}",
                f"${resumen.total_gas:,.0f}",
                f"${resumen.total_internet:,.0f}",
                f"${resumen.total_gastos_comunes:,.0f}",
                f"${resumen.total_general:,.0f}"
            ])

            total_anual['luz'] += resumen.total_luz
            total_anual['agua'] += resumen.total_agua
            total_anual['gas'] += resumen.total_gas
            total_anual['internet'] += resumen.total_internet
            total_anual['gastos_comunes'] += resumen.total_gastos_comunes
            total_anual['total'] += resumen.total_general

        # Agregar totales anuales
        data.append(['', '', '', '', '', '', ''])
        data.append([
            'TOTAL ANUAL',
            f"${total_anual['luz']:,.0f}",
            f"${total_anual['agua']:,.0f}",
            f"${total_anual['gas']:,.0f}",
            f"${total_anual['internet']:,.0f}",
            f"${total_anual['gastos_comunes']:,.0f}",
            f"${total_anual['total']:,.0f}"
        ])

        table = Table(data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),  # Total anual
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),  # Total anual
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(table)

        # Pie de página
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        story.append(Paragraph(f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}", footer_style))

        doc.build(story)
        return str(filepath)