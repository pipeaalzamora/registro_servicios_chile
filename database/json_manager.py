"""
Gestor de archivos JSON y backups
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict
from models import CuentaServicio


class JsonManager:
    """Maneja operaciones con archivos JSON"""

    def __init__(self, connection_manager):
        self.connection = connection_manager
        self.cuentas: Dict[str, CuentaServicio] = {}

        if connection_manager.is_json():
            self.load_data()

    def load_data(self):
        """Carga los datos desde el archivo JSON"""
        if self.connection.cuentas_file.exists():
            try:
                with open(self.connection.cuentas_file, 'r', encoding='utf-8') as f:
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

    def save_data(self):
        """Guarda los datos en el archivo JSON"""
        try:
            # Crear backup antes de guardar
            self.create_backup()

            data = {
                cuenta_id: cuenta.to_dict()
                for cuenta_id, cuenta in self.cuentas.items()
            }

            with open(self.connection.cuentas_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error guardando datos JSON: {e}")
            raise

    def create_backup(self):
        """Crea un backup de los datos actuales (solo para JSON)"""
        if self.connection.is_json() and self.connection.cuentas_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.connection.backup_dir / f"cuentas_backup_{timestamp}.json"
            shutil.copy2(self.connection.cuentas_file, backup_file)

            # Limpiar backups antiguos (mantener solo los últimos 10)
            self.cleanup_old_backups()

    def cleanup_old_backups(self, max_backups: int = 10):
        """Limpia backups antiguos (solo para JSON)"""
        if self.connection.is_json():
            backup_files = list(self.connection.backup_dir.glob("cuentas_backup_*.json"))
            if len(backup_files) > max_backups:
                # Ordenar por fecha de modificación y eliminar los más antiguos
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                for old_backup in backup_files[:-max_backups]:
                    old_backup.unlink()

    def get_backup_info(self) -> Dict:
        """Obtiene información sobre los backups"""
        if not self.connection.is_json():
            return {}

        backup_files = list(self.connection.backup_dir.glob("cuentas_backup_*.json"))
        return {
            'total_backups': len(backup_files),
            'backup_dir': str(self.connection.backup_dir),
            'latest_backup': max(backup_files, key=lambda x: x.stat().st_mtime).name if backup_files else None
        }