"""
Gestor de base de datos con soporte para MongoDB
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
import uuid
import shutil

# MongoDB imports
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoClient = None

from models import CuentaServicio, TipoServicio, ResumenMensual
from config import DATABASE_CONFIG


class DatabaseManager:
    """Gestor de base de datos unificado (JSON/MongoDB)"""

    def __init__(self, db_type: str = None):
        self.db_type = db_type or DATABASE_CONFIG.get('type', 'json')

        if self.db_type == 'mongodb' and MONGODB_AVAILABLE:
            self._init_mongodb()
        else:
            if self.db_type == 'mongodb' and not MONGODB_AVAILABLE:
                print("⚠️  MongoDB no disponible, usando JSON como fallback")
            self._init_json()

    def _init_mongodb(self):
        """Inicializa conexión a MongoDB"""
        try:
            self.client = MongoClient(
                DATABASE_CONFIG['mongodb_uri'],
                serverSelectionTimeoutMS=5000  # 5 segundos timeout
            )

            # Probar conexión
            self.client.admin.command('ping')

            self.db = self.client[DATABASE_CONFIG['mongodb_database']]
            self.collection = self.db.cuentas

            # Crear índices para mejor rendimiento
            self.collection.create_index("id", unique=True)
            self.collection.create_index("tipo_servicio")
            self.collection.create_index("fecha_vencimiento")
            self.collection.create_index("pagado")

            print("✅ Conectado a MongoDB exitosamente")

            # Migración automática desde JSON si está habilitada
            if DATABASE_CONFIG.get('auto_migrate', False):
                self._auto_migrate_from_json()

            self.db_type = 'mongodb'

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            print("🔄 Usando JSON como fallback")
            self._init_json()

    def _init_json(self):
        """Inicializa almacenamiento JSON"""
        self.db_type = 'json'
        self.data_dir = Path(DATABASE_CONFIG.get('json_file', 'data/cuentas.json')).parent
        self.data_dir.mkdir(exist_ok=True)
        self.cuentas_file = Path(DATABASE_CONFIG.get('json_file', 'data/cuentas.json'))
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

        # Cargar datos existentes
        self._load_json_data()
        print("✅ Usando almacenamiento JSON")

    def _load_json_data(self):
        """Carga los datos desde el archivo JSON"""
        if self.cuentas_file.exists():
            try:
                with open(self.cuentas_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cuentas = {
                        cuenta_id: CuentaServicio.from_dict(cuenta_data)
                        for cuenta_id, cuenta_data in data.items()
                    }
            except Exception as e:
                print(f"Error cargando datos JSON: {e}")
                self.cuentas = {}
        else:
            self.cuentas = {}

    def _save_json_data(self):
        """Guarda los datos en el archivo JSON"""
        try:
            # Crear backup antes de guardar
            self._create_backup()

            data = {
                cuenta_id: cuenta.to_dict()
                for cuenta_id, cuenta in self.cuentas.items()
            }

            with open(self.cuentas_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error guardando datos JSON: {e}")
            raise

    def _create_backup(self):
        """Crea un backup de los datos actuales (solo para JSON)"""
        if self.db_type == 'json' and self.cuentas_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"cuentas_backup_{timestamp}.json"
            shutil.copy2(self.cuentas_file, backup_file)

            # Limpiar backups antiguos (mantener solo los últimos 10)
            self._cleanup_old_backups()

    def _cleanup_old_backups(self, max_backups: int = 10):
        """Limpia backups antiguos (solo para JSON)"""
        if self.db_type == 'json':
            backup_files = list(self.backup_dir.glob("cuentas_backup_*.json"))
            if len(backup_files) > max_backups:
                # Ordenar por fecha de modificación y eliminar los más antiguos
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                for old_backup in backup_files[:-max_backups]:
                    old_backup.unlink()

    def _generate_id(self) -> str:
        """Genera un ID único para una cuenta"""
        return str(uuid.uuid4())

    # CRUD Operations - Interfaz unificada
    def crear_cuenta(self, cuenta: CuentaServicio) -> str:
        """Crea una nueva cuenta"""
        if not cuenta.id:
            cuenta.id = self._generate_id()

        cuenta.created_at = datetime.now()
        cuenta.updated_at = datetime.now()

        if self.db_type == 'mongodb':
            return self._crear_cuenta_mongodb(cuenta)
        else:
            return self._crear_cuenta_json(cuenta)

    def _crear_cuenta_mongodb(self, cuenta: CuentaServicio) -> str:
        """Crea cuenta en MongoDB"""
        try:
            cuenta_dict = cuenta.to_dict()
            result = self.collection.insert_one(cuenta_dict)
            if result.inserted_id:
                return cuenta.id
            else:
                raise Exception("Error insertando en MongoDB")
        except Exception as e:
            raise Exception(f"Error creando cuenta en MongoDB: {e}")

    def _crear_cuenta_json(self, cuenta: CuentaServicio) -> str:
        """Crea cuenta en JSON"""
        self.cuentas[cuenta.id] = cuenta
        self._save_json_data()
        return cuenta.id

    def obtener_cuenta(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene una cuenta por ID"""
        if self.db_type == 'mongodb':
            return self._obtener_cuenta_mongodb(cuenta_id)
        else:
            return self._obtener_cuenta_json(cuenta_id)

    def _obtener_cuenta_mongodb(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene cuenta desde MongoDB"""
        try:
            doc = self.collection.find_one({"id": cuenta_id})
            if doc:
                # Remover _id de MongoDB antes de crear el objeto
                doc.pop('_id', None)
                return CuentaServicio.from_dict(doc)
            return None
        except Exception as e:
            print(f"Error obteniendo cuenta desde MongoDB: {e}")
            return None

    def _obtener_cuenta_json(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene cuenta desde JSON"""
        return self.cuentas.get(cuenta_id)

    def obtener_todas_las_cuentas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas"""
        if self.db_type == 'mongodb':
            return self._obtener_todas_mongodb()
        else:
            return self._obtener_todas_json()

    def _obtener_todas_mongodb(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas desde MongoDB"""
        try:
            cuentas = []
            for doc in self.collection.find():
                doc.pop('_id', None)  # Remover _id de MongoDB
                cuenta = CuentaServicio.from_dict(doc)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas desde MongoDB: {e}")
            return []

    def _obtener_todas_json(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas desde JSON"""
        return list(self.cuentas.values())

    def actualizar_cuenta(self, cuenta: CuentaServicio) -> bool:
        """Actualiza una cuenta existente"""
        if not cuenta.id:
            return False

        cuenta.updated_at = datetime.now()

        if self.db_type == 'mongodb':
            return self._actualizar_cuenta_mongodb(cuenta)
        else:
            return self._actualizar_cuenta_json(cuenta)

    def _actualizar_cuenta_mongodb(self, cuenta: CuentaServicio) -> bool:
        """Actualiza cuenta en MongoDB"""
        try:
            cuenta_dict = cuenta.to_dict()
            result = self.collection.replace_one(
                {"id": cuenta.id},
                cuenta_dict
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error actualizando cuenta en MongoDB: {e}")
            return False

    def _actualizar_cuenta_json(self, cuenta: CuentaServicio) -> bool:
        """Actualiza cuenta en JSON"""
        if cuenta.id in self.cuentas:
            self.cuentas[cuenta.id] = cuenta
            self._save_json_data()
            return True
        return False

    def eliminar_cuenta(self, cuenta_id: str) -> bool:
        """Elimina una cuenta"""
        if self.db_type == 'mongodb':
            return self._eliminar_cuenta_mongodb(cuenta_id)
        else:
            return self._eliminar_cuenta_json(cuenta_id)

    def _eliminar_cuenta_mongodb(self, cuenta_id: str) -> bool:
        """Elimina cuenta de MongoDB"""
        try:
            result = self.collection.delete_one({"id": cuenta_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error eliminando cuenta de MongoDB: {e}")
            return False

    def _eliminar_cuenta_json(self, cuenta_id: str) -> bool:
        """Elimina cuenta de JSON"""
        if cuenta_id in self.cuentas:
            del self.cuentas[cuenta_id]
            self._save_json_data()
            return True
        return False

    # Consultas específicas
    def obtener_cuentas_por_tipo(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo de servicio"""
        if self.db_type == 'mongodb':
            return self._obtener_por_tipo_mongodb(tipo)
        else:
            return self._obtener_por_tipo_json(tipo)

    def _obtener_por_tipo_mongodb(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo desde MongoDB"""
        try:
            cuentas = []
            for doc in self.collection.find({"tipo_servicio": tipo.value}):
                doc.pop('_id', None)
                cuenta = CuentaServicio.from_dict(doc)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas por tipo desde MongoDB: {e}")
            return []

    def _obtener_por_tipo_json(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo desde JSON"""
        return [cuenta for cuenta in self.cuentas.values()
                if cuenta.tipo_servicio == tipo]

    def obtener_cuentas_pendientes(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes de pago"""
        if self.db_type == 'mongodb':
            return self._obtener_pendientes_mongodb()
        else:
            return self._obtener_pendientes_json()

    def _obtener_pendientes_mongodb(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes desde MongoDB"""
        try:
            cuentas = []
            for doc in self.collection.find({"pagado": False}):
                doc.pop('_id', None)
                cuenta = CuentaServicio.from_dict(doc)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas pendientes desde MongoDB: {e}")
            return []

    def _obtener_pendientes_json(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes desde JSON"""
        return [cuenta for cuenta in self.cuentas.values()
                if not cuenta.pagado]

    def obtener_cuentas_vencidas(self) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        todas_las_cuentas = self.obtener_todas_las_cuentas()
        return [cuenta for cuenta in todas_las_cuentas
                if cuenta.get_estado().value == "Vencido"]

    def obtener_cuentas_por_mes(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes y año"""
        if self.db_type == 'mongodb':
            return self._obtener_por_mes_mongodb(mes, año)
        else:
            return self._obtener_por_mes_json(mes, año)

    def _obtener_por_mes_mongodb(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes desde MongoDB"""
        try:
            # Crear rango de fechas para el mes
            from datetime import datetime
            inicio_mes = datetime(año, mes, 1)
            if mes == 12:
                fin_mes = datetime(año + 1, 1, 1)
            else:
                fin_mes = datetime(año, mes + 1, 1)

            cuentas = []
            for doc in self.collection.find({
                "fecha_emision": {
                    "$gte": inicio_mes.isoformat(),
                    "$lt": fin_mes.isoformat()
                }
            }):
                doc.pop('_id', None)
                cuenta = CuentaServicio.from_dict(doc)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error obteniendo cuentas por mes desde MongoDB: {e}")
            return []

    def _obtener_por_mes_json(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes desde JSON"""
        return [cuenta for cuenta in self.cuentas.values()
                if cuenta.fecha_emision.month == mes and cuenta.fecha_emision.year == año]

    def buscar_cuentas(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas por término en descripción u observaciones"""
        if self.db_type == 'mongodb':
            return self._buscar_cuentas_mongodb(termino)
        else:
            return self._buscar_cuentas_json(termino)

    def _buscar_cuentas_mongodb(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas en MongoDB"""
        try:
            # Usar regex para búsqueda case-insensitive
            regex_pattern = {"$regex": termino, "$options": "i"}

            cuentas = []
            for doc in self.collection.find({
                "$or": [
                    {"descripcion": regex_pattern},
                    {"observaciones": regex_pattern},
                    {"tipo_servicio": regex_pattern}
                ]
            }):
                doc.pop('_id', None)
                cuenta = CuentaServicio.from_dict(doc)
                cuentas.append(cuenta)
            return cuentas
        except Exception as e:
            print(f"Error buscando cuentas en MongoDB: {e}")
            return []

    def _buscar_cuentas_json(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas en JSON"""
        termino = termino.lower()
        return [cuenta for cuenta in self.cuentas.values()
                if termino in cuenta.descripcion.lower() or
                   termino in cuenta.observaciones.lower() or
                   termino in cuenta.tipo_servicio.value.lower()]

    # Estadísticas
    def obtener_resumen_mensual(self, mes: int, año: int) -> ResumenMensual:
        """Genera resumen mensual"""
        cuentas_mes = self.obtener_cuentas_por_mes(mes, año)

        resumen = ResumenMensual(mes=mes, año=año)
        cuentas_por_tipo = {}

        for cuenta in cuentas_mes:
            resumen.total_gastos += cuenta.monto

            if cuenta.pagado:
                resumen.total_pagado += cuenta.monto
                resumen.cuentas_pagadas += 1
            else:
                resumen.total_pendiente += cuenta.monto
                resumen.cuentas_pendientes += 1

                if cuenta.get_estado().value == "Vencido":
                    resumen.cuentas_vencidas += 1

            # Agrupar por tipo
            tipo = cuenta.tipo_servicio.value
            if tipo not in cuentas_por_tipo:
                cuentas_por_tipo[tipo] = {'total': 0, 'pagado': 0, 'pendiente': 0}

            cuentas_por_tipo[tipo]['total'] += cuenta.monto
            if cuenta.pagado:
                cuentas_por_tipo[tipo]['pagado'] += cuenta.monto
            else:
                cuentas_por_tipo[tipo]['pendiente'] += cuenta.monto

        resumen.cuentas_por_tipo = cuentas_por_tipo
        return resumen

    def obtener_total_por_tipo(self) -> Dict[str, float]:
        """Obtiene el total gastado por tipo de servicio"""
        if self.db_type == 'mongodb':
            return self._obtener_total_por_tipo_mongodb()
        else:
            return self._obtener_total_por_tipo_json()

    def _obtener_total_por_tipo_mongodb(self) -> Dict[str, float]:
        """Obtiene totales por tipo desde MongoDB usando agregación"""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$tipo_servicio",
                        "total": {"$sum": "$monto"}
                    }
                }
            ]

            totales = {}
            for result in self.collection.aggregate(pipeline):
                totales[result['_id']] = result['total']

            return totales
        except Exception as e:
            print(f"Error obteniendo totales por tipo desde MongoDB: {e}")
            return {}

    def _obtener_total_por_tipo_json(self) -> Dict[str, float]:
        """Obtiene totales por tipo desde JSON"""
        totales = {}
        for cuenta in self.cuentas.values():
            tipo = cuenta.tipo_servicio.value
            if tipo not in totales:
                totales[tipo] = 0
            totales[tipo] += cuenta.monto
        return totales

    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales"""
        todas_las_cuentas = self.obtener_todas_las_cuentas()

        if not todas_las_cuentas:
            return {
                'total_cuentas': 0,
                'total_gastos': 0,
                'total_pagado': 0,
                'total_pendiente': 0,
                'cuentas_pagadas': 0,
                'cuentas_pendientes': 0,
                'cuentas_vencidas': 0
            }

        total_gastos = sum(cuenta.monto for cuenta in todas_las_cuentas)
        cuentas_pagadas = [cuenta for cuenta in todas_las_cuentas if cuenta.pagado]
        cuentas_pendientes = [cuenta for cuenta in todas_las_cuentas if not cuenta.pagado]
        cuentas_vencidas = [cuenta for cuenta in todas_las_cuentas
                           if cuenta.get_estado().value == "Vencido"]

        total_pagado = sum(cuenta.monto for cuenta in cuentas_pagadas)
        total_pendiente = sum(cuenta.monto for cuenta in cuentas_pendientes)

        return {
            'total_cuentas': len(todas_las_cuentas),
            'total_gastos': total_gastos,
            'total_pagado': total_pagado,
            'total_pendiente': total_pendiente,
            'cuentas_pagadas': len(cuentas_pagadas),
            'cuentas_pendientes': len(cuentas_pendientes),
            'cuentas_vencidas': len(cuentas_vencidas)
        }

    # Utilidades
    def get_connection_info(self) -> Dict[str, str]:
        """Obtiene información de la conexión actual"""
        if self.db_type == 'mongodb':
            return {
                'type': 'MongoDB',
                'uri': DATABASE_CONFIG['mongodb_uri'],
                'database': DATABASE_CONFIG['mongodb_database'],
                'status': 'Conectado' if hasattr(self, 'client') else 'Desconectado'
            }
        else:
            return {
                'type': 'JSON',
                'file': str(self.cuentas_file),
                'status': 'Activo'
            }

    def _auto_migrate_from_json(self):
        """Migración automática desde JSON si existen datos"""
        json_file = Path(DATABASE_CONFIG.get('json_file', 'data/cuentas.json'))

        if not json_file.exists():
            return

        # Verificar si ya hay datos en MongoDB
        if self.collection.count_documents({}) > 0:
            print("📊 MongoDB ya contiene datos, omitiendo migración automática")
            return

        try:
            # Cargar datos JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not data:
                return

            print(f"🔄 Migrando {len(data)} cuentas desde JSON a MongoDB...")

            # Migrar cada cuenta
            cuentas_migradas = 0
            for cuenta_id, cuenta_data in data.items():
                try:
                    # Convertir a objeto CuentaServicio y luego a dict para MongoDB
                    cuenta = CuentaServicio.from_dict(cuenta_data)
                    cuenta_dict = cuenta.to_dict()

                    # Insertar en MongoDB
                    self.collection.insert_one(cuenta_dict)
                    cuentas_migradas += 1

                except Exception as e:
                    print(f"⚠️  Error migrando cuenta {cuenta_id}: {e}")

            print(f"✅ Migración completada: {cuentas_migradas} cuentas transferidas a MongoDB")

            # Crear backup del archivo JSON original
            backup_file = json_file.parent / f"cuentas_backup_migrated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(json_file, backup_file)
            print(f"💾 Backup creado: {backup_file}")

        except Exception as e:
            print(f"❌ Error en migración automática: {e}")

    def migrar_json_a_mongodb(self) -> bool:
        """Migra datos de JSON a MongoDB"""
        if self.db_type != 'json':
            print("❌ Solo se puede migrar desde JSON")
            return False

        if not MONGODB_AVAILABLE:
            print("❌ MongoDB no está disponible")
            return False

        try:
            # Crear conexión temporal a MongoDB
            temp_client = MongoClient(DATABASE_CONFIG['mongodb_uri'])
            temp_db = temp_client[DATABASE_CONFIG['mongodb_database']]
            temp_collection = temp_db.cuentas

            # Migrar todas las cuentas
            cuentas_migradas = 0
            for cuenta in self.cuentas.values():
                cuenta_dict = cuenta.to_dict()
                temp_collection.insert_one(cuenta_dict)
                cuentas_migradas += 1

            print(f"✅ Migradas {cuentas_migradas} cuentas a MongoDB")

            # Cambiar a MongoDB
            self._init_mongodb()
            return True

        except Exception as e:
            print(f"❌ Error en migración: {e}")
            return False

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.db_type == 'mongodb' and hasattr(self, 'client'):
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")