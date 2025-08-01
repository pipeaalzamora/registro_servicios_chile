"""
Gestor de base de datos refactorizado y modular
"""

from typing import List, Optional, Dict
from models import CuentaServicio, TipoServicio, ResumenMensual

from database.connection_manager import ConnectionManager
from database.json_manager import JsonManager
from database.crud_operations import CrudOperations
from database.query_operations import QueryOperations
from database.statistics_manager import StatisticsManager


class DatabaseManager:
    """Gestor de base de datos unificado y refactorizado"""

    def __init__(self, db_type: str = None):
        # Inicializar gestores especializados
        self.connection = ConnectionManager(db_type)
        self.json_manager = JsonManager(self.connection) if self.connection.is_json() else None

        # Inicializar operaciones
        self.crud = CrudOperations(self.connection, self.json_manager)
        self.queries = QueryOperations(self.connection, self.json_manager)
        self.statistics = StatisticsManager(self.crud, self.queries)

    # Delegación de métodos CRUD
    def crear_cuenta(self, cuenta: CuentaServicio) -> str:
        """Crea una nueva cuenta"""
        return self.crud.crear_cuenta(cuenta)

    def obtener_cuenta(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene una cuenta por ID"""
        return self.crud.obtener_cuenta(cuenta_id)

    def obtener_todas_las_cuentas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas"""
        return self.crud.obtener_todas_las_cuentas()

    def actualizar_cuenta(self, cuenta: CuentaServicio) -> bool:
        """Actualiza una cuenta existente"""
        return self.crud.actualizar_cuenta(cuenta)

    def eliminar_cuenta(self, cuenta_id: str) -> bool:
        """Elimina una cuenta"""
        return self.crud.eliminar_cuenta(cuenta_id)

    # Delegación de consultas específicas
    def obtener_cuentas_por_tipo(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo de servicio"""
        return self.queries.obtener_cuentas_por_tipo(tipo)

    def obtener_cuentas_pendientes(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes de pago"""
        return self.queries.obtener_cuentas_pendientes()

    def obtener_cuentas_vencidas(self) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        return self.queries.obtener_cuentas_vencidas(self.crud)

    def obtener_cuentas_por_mes(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes y año"""
        return self.queries.obtener_cuentas_por_mes(mes, año)

    def buscar_cuentas(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas por término en descripción u observaciones"""
        return self.queries.buscar_cuentas(termino)

    def obtener_total_por_tipo(self) -> Dict[str, float]:
        """Obtiene el total gastado por tipo de servicio"""
        return self.queries.obtener_total_por_tipo()

    # Delegación de estadísticas
    def obtener_resumen_mensual(self, mes: int, año: int) -> ResumenMensual:
        """Genera resumen mensual"""
        return self.statistics.obtener_resumen_mensual(mes, año)

    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales"""
        return self.statistics.obtener_estadisticas_generales()

    def obtener_estadisticas_por_tipo(self) -> Dict[str, Dict]:
        """Obtiene estadísticas detalladas por tipo de servicio"""
        return self.statistics.obtener_estadisticas_por_tipo()

    def obtener_tendencias_mensuales(self, año: int) -> Dict[int, Dict]:
        """Obtiene tendencias mensuales para un año específico"""
        return self.statistics.obtener_tendencias_mensuales(año)

    # Métodos de utilidad
    def get_connection_info(self) -> Dict[str, str]:
        """Obtiene información de la conexión actual"""
        return self.connection.get_connection_info()

    def close(self):
        """Cierra la conexión a la base de datos"""
        self.connection.close()

    @property
    def db_type(self) -> str:
        """Obtiene el tipo de base de datos actual"""
        return self.connection.db_type