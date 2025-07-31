"""
Configuración de la aplicación con soporte para variables de entorno
"""

import os
from pathlib import Path
from env_config import env_config

# Directorios de la aplicación
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
BACKUPS_DIR = BASE_DIR / "backups"

# Configuración desde variables de entorno
DATABASE_CONFIG = env_config.get_database_config()
REPORTS_CONFIG = env_config.get_reports_config()
APP_CONFIG = env_config.get_app_config()
NOTIFICATIONS_CONFIG = env_config.get_notifications_config()
UI_CONFIG = env_config.get_ui_config()

# Actualizar rutas relativas
DATABASE_CONFIG['json_file'] = BASE_DIR / DATABASE_CONFIG['json_file']

def ensure_directories():
    """Crea los directorios necesarios si no existen"""
    for directory in [DATA_DIR, REPORTS_DIR, BACKUPS_DIR]:
        directory.mkdir(exist_ok=True)

def print_config_info():
    """Imprime información de configuración al iniciar"""
    print(f"📁 Directorio base: {BASE_DIR}")
    print(f"🗄️ Base de datos: {DATABASE_CONFIG['type']}")
    print(f"🎨 Tema: {APP_CONFIG['theme']}")
    print(f"🔔 Notificaciones: {'✅' if NOTIFICATIONS_CONFIG['enabled'] else '❌'}")

# Llamar al inicializar
ensure_directories()

# Mostrar información de configuración si se ejecuta directamente
if __name__ == "__main__":
    print_config_info()
    env_config.print_current_config()