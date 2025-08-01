"""
Gestor de conexiones de base de datos
"""

from pathlib import Path
from typing import Dict

# MongoDB imports
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoClient = None

from config import DATABASE_CONFIG


class ConnectionManager:
    """Maneja las conexiones a MongoDB y configuración JSON"""

    def __init__(self, db_type: str = None):
        self.db_type = db_type or DATABASE_CONFIG.get('type', 'json')
        self.client = None
        self.db = None
        self.collection = None

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
        """Inicializa configuración para almacenamiento JSON"""
        self.db_type = 'json'
        self.data_dir = Path(DATABASE_CONFIG.get('json_file', 'data/cuentas.json')).parent
        self.data_dir.mkdir(exist_ok=True)
        self.cuentas_file = Path(DATABASE_CONFIG.get('json_file', 'data/cuentas.json'))
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

        print("✅ Usando almacenamiento JSON")

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
            import json
            import shutil
            from datetime import datetime
            from models import CuentaServicio

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

    def get_connection_info(self) -> Dict[str, str]:
        """Obtiene información de la conexión actual"""
        if self.db_type == 'mongodb':
            return {
                'type': 'MongoDB',
                'status': 'Conectado',
                'database': DATABASE_CONFIG.get('mongodb_database', 'N/A'),
                'uri': DATABASE_CONFIG.get('mongodb_uri', 'N/A')[:50] + '...'
            }
        else:
            return {
                'type': 'JSON',
                'status': 'Activo',
                'file': str(self.cuentas_file),
                'backup_dir': str(self.backup_dir)
            }

    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.db_type == 'mongodb' and hasattr(self, 'client') and self.client:
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")
        elif self.db_type == 'json':
            # Para JSON, no hay conexión que cerrar, pero podríamos hacer un guardado final
            # si fuera necesario. Por ahora, las operaciones CRUD ya guardan automáticamente.
            print("💾 Datos JSON ya guardados automáticamente")

    def is_mongodb(self) -> bool:
        """Verifica si está usando MongoDB"""
        return self.db_type == 'mongodb'

    def is_json(self) -> bool:
        """Verifica si está usando JSON"""
        return self.db_type == 'json'