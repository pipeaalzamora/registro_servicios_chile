"""
Operaciones de consulta específicas
"""

from datetime import datetime, timedelta
from typing import List, Dict
from models import CuentaServicio, TipoServicio


class QueryOperations:
    """Maneja consultas específicas y búsquedas"""

    def __init__(self, connection_manager, json_manager=None):
        self.connection = connection_manager
        self.json_manager = json_manager

    def obtener_cuentas_por_tipo(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo de servicio"""
        if self.connection.is_mongodb():
            return self._obtener_por_tipo_mongodb(tipo)
        else:
            return self._obtener_por_tipo_json(tipo)

    def _obtener_por_tipo_mongodb(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo desde MongoDB"""
        try:
            cuentas = []
            for cuenta_dict in self.connection.collection.find({"tipo_servicio": tipo.value}):
                cuenta = CuentaServicio.from_dict(cuenta_dict)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas por tipo desde MongoDB: {e}")
            return []

    def _obtener_por_tipo_json(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo desde JSON"""
        return [cuenta for cuenta in self.json_manager.cuentas.values()
                if cuenta.tipo_servicio == tipo]

    def obtener_cuentas_pendientes(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes de pago"""
        if self.connection.is_mongodb():
            return self._obtener_pendientes_mongodb()
        else:
            return self._obtener_pendientes_json()

    def _obtener_pendientes_mongodb(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes desde MongoDB"""
        try:
            cuentas = []
            for cuenta_dict in self.connection.collection.find({"pagado": False}):
                cuenta = CuentaServicio.from_dict(cuenta_dict)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas pendientes desde MongoDB: {e}")
            return []

    def _obtener_pendientes_json(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes desde JSON"""
        return [cuenta for cuenta in self.json_manager.cuentas.values()
                if not cuenta.pagado]

    def obtener_cuentas_vencidas(self, crud_operations) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        todas_las_cuentas = crud_operations.obtener_todas_las_cuentas()
        return [cuenta for cuenta in todas_las_cuentas
                if cuenta.get_estado().value == "Vencido"]

    def obtener_cuentas_por_mes(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes y año"""
        if self.connection.is_mongodb():
            return self._obtener_por_mes_mongodb(mes, año)
        else:
            return self._obtener_por_mes_json(mes, año)

    def _obtener_por_mes_mongodb(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes desde MongoDB"""
        try:
            # Crear fechas de inicio y fin del mes
            inicio_mes = datetime(año, mes, 1)
            if mes == 12:
                fin_mes = datetime(año + 1, 1, 1)
            else:
                fin_mes = datetime(año, mes + 1, 1)

            cuentas = []
            for cuenta_dict in self.connection.collection.find({
                "fecha_emision": {
                    "$gte": inicio_mes.isoformat(),
                    "$lt": fin_mes.isoformat()
                }
            }):
                cuenta = CuentaServicio.from_dict(cuenta_dict)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas por mes desde MongoDB: {e}")
            return []

    def _obtener_por_mes_json(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes desde JSON"""
        return [cuenta for cuenta in self.json_manager.cuentas.values()
                if cuenta.fecha_emision.month == mes and cuenta.fecha_emision.year == año]

    def buscar_cuentas(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas por término en descripción u observaciones"""
        if self.connection.is_mongodb():
            return self._buscar_cuentas_mongodb(termino)
        else:
            return self._buscar_cuentas_json(termino)

    def _buscar_cuentas_mongodb(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas en MongoDB"""
        try:
            # Búsqueda con regex case-insensitive
            regex_pattern = {"$regex": termino, "$options": "i"}

            cuentas = []
            for cuenta_dict in self.connection.collection.find({
                "$or": [
                    {"descripcion": regex_pattern},
                    {"observaciones": regex_pattern}
                ]
            }):
                cuenta = CuentaServicio.from_dict(cuenta_dict)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error buscando cuentas en MongoDB: {e}")
            return []

    def _buscar_cuentas_json(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas en JSON"""
        termino = termino.lower()
        return [cuenta for cuenta in self.json_manager.cuentas.values()
                if termino in cuenta.descripcion.lower() or
                   termino in cuenta.observaciones.lower()]

    def obtener_total_por_tipo(self) -> Dict[str, float]:
        """Obtiene el total gastado por tipo de servicio"""
        if self.connection.is_mongodb():
            return self._obtener_total_por_tipo_mongodb()
        else:
            return self._obtener_total_por_tipo_json()

    def _obtener_total_por_tipo_mongodb(self) -> Dict[str, float]:
        """Obtiene totales por tipo desde MongoDB usando agregación"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$tipo_servicio",
                    "total": {"$sum": "$monto"}
                }}
            ]

            totales = {}
            for result in self.connection.collection.aggregate(pipeline):
                totales[result["_id"]] = result["total"]

            return totales
        except Exception as e:
            print(f"Error obteniendo totales por tipo desde MongoDB: {e}")
            return {}

    def _obtener_total_por_tipo_json(self) -> Dict[str, float]:
        """Obtiene totales por tipo desde JSON"""
        totales = {}
        for cuenta in self.json_manager.cuentas.values():
            tipo = cuenta.tipo_servicio.value
            totales[tipo] = totales.get(tipo, 0) + cuenta.monto
        return totales