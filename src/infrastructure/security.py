"""
Módulo de seguridad para la aplicación
"""

import os
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
import re
from datetime import datetime


class SecurityManager:
    """Gestor de seguridad para la aplicación"""

    def __init__(self, data_dir: str = "data", reports_dir: str = "reports"):
        self.data_dir = Path(data_dir).resolve()
        self.reports_dir = Path(reports_dir).resolve()
        self.allowed_extensions = {'.json', '.pdf', '.txt'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    def validar_ruta_archivo(self, filepath: str) -> bool:
        """Valida que la ruta del archivo sea segura"""
        try:
            path = Path(filepath).resolve()
            # Verificar que esté dentro de los directorios permitidos
            is_relative_to_data = path.is_relative_to(self.data_dir)
            is_relative_to_reports = path.is_relative_to(self.reports_dir)
            if not (is_relative_to_data or is_relative_to_reports):
                return False
            # Verificar extensión permitida
            if path.suffix.lower() not in self.allowed_extensions:
                return False
            # Verificar que no contenga caracteres peligrosos
            if not SecurityManager.validar_nombre_archivo(path.name):
                return False
            return True
        except Exception:
            return False

    def sanitizar_datos_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza datos antes de guardarlos en JSON"""
        sanitized = {}

        for key, value in data.items():
            # Validar clave
            if not isinstance(key, str) or len(key) > 100:
                continue

            # Sanitizar clave
            safe_key = SecurityManager.sanitizar_texto(key)
            if not safe_key:
                continue

            # Sanitizar valor según su tipo
            if isinstance(value, str):
                safe_value = SecurityManager.sanitizar_texto(value)
            elif isinstance(value, (int, float, bool)):
                safe_value = value
            elif isinstance(value, list):
                safe_value = [self.sanitizar_datos_json(item) if isinstance(item, dict)
                            else SecurityManager.sanitizar_texto(str(item)) if isinstance(item, str)
                            else item for item in value[:100]]  # Limitar a 100 elementos
            elif isinstance(value, dict):
                safe_value = self.sanitizar_datos_json(value)
            else:
                safe_value = SecurityManager.sanitizar_texto(str(value))

            sanitized[safe_key] = safe_value

        return sanitized

    def validar_archivo_json(self, filepath: str) -> bool:
        """Valida que un archivo JSON sea seguro"""
        try:
            if not self.validar_ruta_archivo(filepath):
                return False

            path = Path(filepath)
            if not path.exists():
                return True  # Archivo nuevo, permitir creación

            # Verificar tamaño
            if path.stat().st_size > self.max_file_size:
                return False

            # Verificar que sea JSON válido
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validar estructura básica
            if not isinstance(data, (dict, list)):
                return False

            return True
        except:
            return False

    def calcular_hash_archivo(self, filepath: str) -> Optional[str]:
        """Calcula el hash SHA-256 de un archivo"""
        try:
            if not self.validar_ruta_archivo(filepath):
                return None

            path = Path(filepath)
            if not path.exists():
                return None

            hash_sha256 = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)

            return hash_sha256.hexdigest()
        except:
            return None

    def verificar_integridad_archivo(self, filepath: str, hash_esperado: str) -> bool:
        """Verifica la integridad de un archivo comparando su hash"""
        hash_actual = self.calcular_hash_archivo(filepath)
        return hash_actual == hash_esperado

    def crear_backup_seguro(self, filepath: str) -> Optional[str]:
        """Crea un backup seguro de un archivo"""
        try:
            if not self.validar_ruta_archivo(filepath):
                return None

            path = Path(filepath)
            if not path.exists():
                return None

            # Crear directorio de backup si no existe
            backup_dir = self.data_dir / "backups"
            backup_dir.mkdir(exist_ok=True)

            # Generar nombre de backup con timestamp
            timestamp = path.stat().st_mtime
            backup_name = f"{path.stem}_{int(timestamp)}_backup{path.suffix}"
            backup_path = backup_dir / backup_name

            # Copiar archivo
            import shutil
            shutil.copy2(path, backup_path)

            return str(backup_path)
        except:
            return None

    def limpiar_backups_antiguos(self, max_backups: int = 10) -> int:
        """Limpia backups antiguos, manteniendo solo los más recientes"""
        try:
            backup_dir = self.data_dir / "backups"
            if not backup_dir.exists():
                return 0

            # Obtener todos los backups
            backups = list(backup_dir.glob("*_backup.*"))
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Eliminar backups excedentes
            eliminados = 0
            for backup in backups[max_backups:]:
                try:
                    backup.unlink()
                    eliminados += 1
                except:
                    pass

            return eliminados
        except:
            return 0

    def validar_configuracion(self, config: Dict[str, Any]) -> List[str]:
        """Valida una configuración y retorna lista de errores"""
        errores = []

        # Validar estructura básica
        if not isinstance(config, dict):
            errores.append("La configuración debe ser un objeto JSON válido")
            return errores

        # Validar configuración de email si existe
        if 'email' in config:
            email_config = config['email']
            if isinstance(email_config, dict):
                # Validar campos de email
                campos_requeridos = ['smtp_server', 'smtp_port', 'username', 'from_email', 'to_email']
                for campo in campos_requeridos:
                    if campo not in email_config or not email_config[campo]:
                        errores.append(f"Campo '{campo}' es requerido en la configuración de email")

                # Validar formato de email
                if 'from_email' in email_config and not SecurityManager.validar_email(email_config['from_email']):
                    errores.append("Formato de email 'from_email' inválido")

                if 'to_email' in email_config and not SecurityManager.validar_email(email_config['to_email']):
                    errores.append("Formato de email 'to_email' inválido")

                # Validar puerto SMTP
                if 'smtp_port' in email_config:
                    try:
                        puerto = int(email_config['smtp_port'])
                        if puerto < 1 or puerto > 65535:
                            errores.append("Puerto SMTP debe estar entre 1 y 65535")
                    except:
                        errores.append("Puerto SMTP debe ser un número válido")

        # Validar configuración de notificaciones si existe
        if 'notifications' in config:
            notif_config = config['notifications']
            if isinstance(notif_config, dict):
                if 'days_before_due' in notif_config:
                    try:
                        dias = int(notif_config['days_before_due'])
                        if dias < 1 or dias > 365:
                            errores.append("Días antes del vencimiento debe estar entre 1 y 365")
                    except:
                        errores.append("Días antes del vencimiento debe ser un número válido")

        return errores

    def generar_log_seguridad(self, evento: str, detalles: str = "", nivel: str = "INFO"):
        """Genera un log de seguridad"""
        try:
            log_dir = self.data_dir / "logs"
            log_dir.mkdir(exist_ok=True)

            log_file = log_dir / "security.log"
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {nivel}: {evento} - {detalles}\n")
        except:
            pass  # No fallar si no se puede escribir el log

    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        if not email or not isinstance(email, str):
            return False

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def sanitizar_texto(texto: str, max_length: Optional[int] = 1000) -> str:
        """Sanitiza texto para prevenir inyección de código"""
        if not texto or not isinstance(texto, str):
            return ""

        # Remover caracteres peligrosos
        texto_limpio = re.sub(r'[<>"\']', '', texto)

        # Limitar longitud
        if max_length:
            texto_limpio = texto_limpio[:max_length]

        return texto_limpio.strip()

    @staticmethod
    def validar_nombre_archivo(nombre: str) -> bool:
        """Valida que el nombre de archivo sea seguro"""
        if not nombre or not isinstance(nombre, str):
            return False

        # No permitir caracteres peligrosos
        if re.search(r'[<>:"/\\|?*]', nombre):
            return False

        # No permitir nombres reservados de Windows
        nombres_reservados = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
                             'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
                             'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']

        nombre_sin_extension = nombre.split('.')[0].upper()
        if nombre_sin_extension in nombres_reservados:
            return False

        return True


# Instancia global del gestor de seguridad
security_manager = SecurityManager()