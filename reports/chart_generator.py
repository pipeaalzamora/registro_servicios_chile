"""
Generador de gráficos para reportes
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from models import ResumenMensual


class ChartGenerator:
    """Generador de gráficos usando matplotlib"""

    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)

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