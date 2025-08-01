"""
Operaciones CRUD para base de datos
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional
from models import CuentaServicio
from .json_manager import JsonManager


class CrudOperations:
    """Maneja las operaciones CRUD básicas"""

    def __init__(self, connection_manager, json_manager: JsonManager = None):
        self.connection = connection_manager
        self.json_manager = json_manager

    def _generate_id(self) -> str:
        """Genera un ID único para una cuenta"""
        return str(uuid.uuid4())

    def crear_cuenta(self, cuenta: CuentaServicio) -> str:
        """Crea una nueva cuenta"""
        if not cuenta.id:
            cuenta.id = self._generate_id()

        cuenta.created_at = cuenta.created_at or datetime.now()
        cuenta.updated_at = datetime.now()

        if self.connection.is_mongodb():
            return self._crear_cuenta_mongodb(cuenta)
        else:
            return self._crear_cuenta_json(cuenta)

    def _crear_cuenta_mongodb(self, cuenta: CuentaServicio) -> str:
        """Crea cuenta en MongoDB"""
        try:
            cuenta_dict = cuenta.to_dict()
            self.connection.collection.insert_one(cuenta_dict)
            return cuenta.id
        except Exception as e:
            raise Exception(f"Error creando cuenta en MongoDB: {e}")

    def _crear_cuenta_json(self, cuenta: CuentaServicio) -> str:
        """Crea cuenta en JSON"""
        self.json_manager.cuentas[cuenta.id] = cuenta
        self.json_manager.save_data()
        return cuenta.id

    def obtener_cuenta(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene una cuenta por ID"""
        if self.connection.is_mongodb():
            return self._obtener_cuenta_mongodb(cuenta_id)
        else:
            return self._obtener_cuenta_json(cuenta_id)

    def _obtener_cuenta_mongodb(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene cuenta desde MongoDB"""
        try:
            cuenta_dict = self.connection.collection.find_one({"id": cuenta_id})
            if cuenta_dict:
                return CuentaServicio.from_dict(cuenta_dict)
            return None
        except Exception as e:
            print(f"Error obteniendo cuenta desde MongoDB: {e}")
            return None

    def _obtener_cuenta_json(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene cuenta desde JSON"""
        return self.json_manager.cuentas.get(cuenta_id)

    def obtener_todas_las_cuentas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas"""
        if self.connection.is_mongodb():
            return self._obtener_todas_mongodb()
        else:
            return self._obtener_todas_json()

    def _obtener_todas_mongodb(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas desde MongoDB"""
        try:
            cuentas = []
            for cuenta_dict in self.connection.collection.find():
                cuenta = CuentaServicio.from_dict(cuenta_dict)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas desde MongoDB: {e}")
            return []

    def _obtener_todas_json(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas desde JSON"""
        return list(self.json_manager.cuentas.values())

    def actualizar_cuenta(self, cuenta: CuentaServicio) -> bool:
        """Actualiza una cuenta existente"""
        if not cuenta.id:
            return False

        cuenta.updated_at = datetime.now()

        if self.connection.is_mongodb():
            return self._actualizar_cuenta_mongodb(cuenta)
        else:
            return self._actualizar_cuenta_json(cuenta)

    def _actualizar_cuenta_mongodb(self, cuenta: CuentaServicio) -> bool:
        """Actualiza cuenta en MongoDB"""
        try:
            cuenta_dict = cuenta.to_dict()
            result = self.connection.collection.update_one(
                {"id": cuenta.id}, {"$set": cuenta_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error actualizando cuenta en MongoDB: {e}")
            return False

    def _actualizar_cuenta_json(self, cuenta: CuentaServicio) -> bool:
        """Actualiza cuenta en JSON"""
        if cuenta.id in self.json_manager.cuentas:
            self.json_manager.cuentas[cuenta.id] = cuenta
            self.json_manager.save_data()
            return True
        return False

    def eliminar_cuenta(self, cuenta_id: str) -> bool:
        """Elimina una cuenta"""
        if self.connection.is_mongodb():
            return self._eliminar_cuenta_mongodb(cuenta_id)
        else:
            return self._eliminar_cuenta_json(cuenta_id)

    def _eliminar_cuenta_mongodb(self, cuenta_id: str) -> bool:
        """Elimina cuenta de MongoDB"""
        try:
            result = self.connection.collection.delete_one({"id": cuenta_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error eliminando cuenta de MongoDB: {e}")
            return False

    def _eliminar_cuenta_json(self, cuenta_id: str) -> bool:
        """Elimina cuenta de JSON"""
        if cuenta_id in self.json_manager.cuentas:
            del self.json_manager.cuentas[cuenta_id]
            self.json_manager.save_data()
            return True
        return False