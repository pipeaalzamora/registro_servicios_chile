"""
Clase base para generación de reportes PDF
"""

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from pathlib import Path
from typing import List
from datetime import datetime

from models import CuentaServicio


class BaseReportGenerator:
    """Clase base para generación de reportes PDF"""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configura estilos personalizados"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))

        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        ))

    def _crear_resumen_estadistico(self, cuentas: List[CuentaServicio]) -> List:
        """Crea resumen estadístico"""
        elements = []

        if not cuentas:
            elements.append(Paragraph("No hay cuentas para mostrar", self.styles['Normal']))
            return elements

        total_gastos = sum(cuenta.monto for cuenta in cuentas)
        cuentas_pagadas = [c for c in cuentas if c.pagado]
        cuentas_pendientes = [c for c in cuentas if not c.pagado]
        cuentas_vencidas = [c for c in cuentas if c.get_estado().value == "Vencido"]

        total_pagado = sum(cuenta.monto for cuenta in cuentas_pagadas)
        total_pendiente = sum(cuenta.monto for cuenta in cuentas_pendientes)

        # Crear tabla de resumen
        data = [
            ['Concepto', 'Cantidad', 'Monto (CLP)'],
            ['Total de Cuentas', str(len(cuentas)), f"${total_gastos:,.0f}"],
            ['Cuentas Pagadas', str(len(cuentas_pagadas)), f"${total_pagado:,.0f}"],
            ['Cuentas Pendientes', str(len(cuentas_pendientes)), f"${total_pendiente:,.0f}"],
            ['Cuentas Vencidas', str(len(cuentas_vencidas)), '-']
        ]

        table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
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

        elements.append(Paragraph("Resumen Estadístico", self.styles['CustomHeading']))
        elements.append(table)

        return elements

    def _crear_tabla_cuentas(self, cuentas: List[CuentaServicio]) -> List:
        """Crea tabla con detalles de cuentas"""
        elements = []

        if not cuentas:
            elements.append(Paragraph("No hay cuentas para mostrar", self.styles['Normal']))
            return elements

        # Encabezados expandidos
        data = [['Tipo', 'Descripción', 'Monto', 'Emisión', 'Vencimiento', 'Corte', 'Próx. Lectura', 'Estado', 'Días p/Vencer', 'Observaciones']]

        # Datos de cuentas
        for cuenta in cuentas:
            estado = cuenta.get_estado().value
            dias_vencer = cuenta.dias_para_vencer() if not cuenta.pagado else 0

            # Formatear fechas
            fecha_emision = cuenta.fecha_emision.strftime('%d/%m/%Y') if cuenta.fecha_emision else "-"
            fecha_venc = cuenta.fecha_vencimiento.strftime('%d/%m/%Y') if cuenta.fecha_vencimiento else "-"
            fecha_corte = cuenta.fecha_corte.strftime('%d/%m/%Y') if cuenta.fecha_corte else "-"
            fecha_lectura = getattr(cuenta, 'fecha_lectura_proxima', None)
            fecha_lectura = fecha_lectura.strftime('%d/%m/%Y') if fecha_lectura else "-"

            # Truncar textos largos
            descripcion = cuenta.descripcion[:25] + "..." if len(cuenta.descripcion) > 25 else cuenta.descripcion
            observaciones = cuenta.observaciones[:20] + "..." if len(cuenta.observaciones) > 20 else cuenta.observaciones if cuenta.observaciones else "-"

            data.append([
                cuenta.tipo_servicio.value,
                descripcion,
                f"${cuenta.monto:,.0f}".replace(",", "."),
                fecha_emision,
                fecha_venc,
                fecha_corte,
                fecha_lectura,
                estado,
                str(dias_vencer) if dias_vencer > 0 else "-",
                observaciones
            ])

        # Ajustar anchos de columna para orientación horizontal (landscape A4 = ~11 pulgadas útiles)
        table = Table(data, colWidths=[0.8*inch, 1.8*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.7*inch, 1.5*inch])

        # Estilo de tabla
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]

        # Colorear filas según estado
        for i, cuenta in enumerate(cuentas, 1):
            estado = cuenta.get_estado()
            if estado.value == "Vencido":
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightcoral))
            elif estado.value == "En Riesgo de Corte":
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.orange))
            elif estado.value == "Pagado":
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightgreen))

        table.setStyle(TableStyle(table_style))

        elements.append(Paragraph("Detalle de Cuentas", self.styles['CustomHeading']))
        elements.append(table)

        return elements