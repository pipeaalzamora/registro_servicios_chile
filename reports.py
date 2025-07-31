"""
Generador de reportes PDF simplificado
"""

from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.graphics.shapes import Drawing
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import io
import base64

from models import CuentaServicio, ResumenMensual


class ReportGenerator:
    """Generador de reportes PDF"""

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

    def generar_reporte_por_tipo(self, cuentas_por_tipo: Dict[str, List[CuentaServicio]], custom_path: str = None) -> str:
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

    def crear_grafico_gastos_mensuales(self, resumenes: List[ResumenMensual],
                                     año: int, custom_path: str = None) -> str:
        """Crea gráfico de gastos mensuales usando matplotlib"""
        meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        gastos_mensuales = [r.total_gastos for r in resumenes]

        plt.figure(figsize=(12, 6))
        plt.bar(meses, gastos_mensuales, color='steelblue', alpha=0.7)
        plt.title(f'Gastos Mensuales {año}', fontsize=16, fontweight='bold')
        plt.xlabel('Mes', fontsize=12)
        plt.ylabel('Monto (CLP)', fontsize=12)
        plt.xticks(rotation=45)

        # Formatear eje Y con separadores de miles
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        plt.tight_layout()

        # Guardar gráfico
        if custom_path:
            filepath = Path(custom_path)
        else:
            filename = f"grafico_gastos_mensuales_{año}.png"
            filepath = self.reports_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return str(filepath)

    def crear_grafico_por_tipo(self, totales_por_tipo: Dict[str, float], custom_path: str = None) -> str:
        """Crea gráfico de gastos por tipo de servicio"""
        if not totales_por_tipo:
            return None

        tipos = list(totales_por_tipo.keys())
        montos = list(totales_por_tipo.values())

        plt.figure(figsize=(10, 8))
        colors_list = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF', '#FFD700']

        plt.pie(montos, labels=tipos, autopct='%1.1f%%', startangle=90,
                colors=colors_list[:len(tipos)])
        plt.title('Distribución de Gastos por Tipo de Servicio', fontsize=16, fontweight='bold')
        plt.axis('equal')

        # Guardar gráfico
        if custom_path:
            filepath = Path(custom_path)
        else:
            filename = f"grafico_por_tipo_{datetime.now().strftime('%Y%m%d')}.png"
            filepath = self.reports_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return str(filepath)