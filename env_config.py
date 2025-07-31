"""
Configuración de variables de entorno para la aplicación
"""

import os
from pathlib import Path
from typing import Dict, Any


class EnvironmentConfig:
    """Gestor de configuración basado en variables de entorno"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self._load_env_file()

    def _load_env_file(self):
        """Carga variables desde archivo .env si existe"""
        env_file = self.base_dir / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            os.environ[key] = value
                print(f"✅ Variables de entorno cargadas desde {env_file}")
            except Exception as e:
                print(f"⚠️ Error cargando .env: {e}")

    def get_database_config(self) -> Dict[str, Any]:
        """Obtiene configuración de base de datos desde variables de entorno"""
        return {
            'type': os.getenv('DB_TYPE', 'json'),
            'json_file': Path(os.getenv('DB_JSON_FILE', 'data/cuentas.json')),
            'mongodb_uri': os.getenv('DB_MONGODB_URI', 'mongodb://localhost:27017/'),
            'mongodb_database': os.getenv('DB_MONGODB_DATABASE', 'registro_servicios_chile'),
            'auto_migrate': os.getenv('DB_AUTO_MIGRATE', 'true').lower() == 'true'
        }

    def get_app_config(self) -> Dict[str, Any]:
        """Obtiene configuración de aplicación desde variables de entorno"""
        return {
            'title': os.getenv('APP_TITLE', 'Registro de Servicios Chile'),
            'version': os.getenv('APP_VERSION', '3.0.0'),
            'author': os.getenv('APP_AUTHOR', 'Usuario'),
            'window_size': os.getenv('APP_WINDOW_SIZE', '1400x800'),
            'min_window_size': os.getenv('APP_MIN_WINDOW_SIZE', '1000x700'),
            'theme': os.getenv('APP_THEME', 'modern'),
            'auto_save': os.getenv('APP_AUTO_SAVE', 'true').lower() == 'true',
            'show_notifications': os.getenv('APP_SHOW_NOTIFICATIONS', 'true').lower() == 'true',
            'check_updates': os.getenv('APP_CHECK_UPDATES', 'true').lower() == 'true'
        }

    def get_notifications_config(self) -> Dict[str, Any]:
        """Obtiene configuración de notificaciones desde variables de entorno"""
        return {
            'enabled': os.getenv('NOTIFICATIONS_ENABLED', 'true').lower() == 'true',
            'check_interval': int(os.getenv('NOTIFICATIONS_CHECK_INTERVAL', '300')),
            'days_before_due': int(os.getenv('NOTIFICATIONS_DAYS_BEFORE_DUE', '3')),
            'days_before_cut': int(os.getenv('NOTIFICATIONS_DAYS_BEFORE_CUT', '1')),
            'sound_enabled': os.getenv('NOTIFICATIONS_SOUND_ENABLED', 'false').lower() == 'true',
            'desktop_notifications': os.getenv('NOTIFICATIONS_DESKTOP', 'true').lower() == 'true'
        }

    def get_ui_config(self) -> Dict[str, Any]:
        """Obtiene configuración de UI desde variables de entorno"""
        return {
            'show_tooltips': os.getenv('UI_SHOW_TOOLTIPS', 'true').lower() == 'true',
            'animate_transitions': os.getenv('UI_ANIMATE_TRANSITIONS', 'true').lower() == 'true',
            'auto_refresh': os.getenv('UI_AUTO_REFRESH', 'true').lower() == 'true',
            'refresh_interval': int(os.getenv('UI_REFRESH_INTERVAL', '60')),
            'show_progress_bars': os.getenv('UI_SHOW_PROGRESS_BARS', 'true').lower() == 'true',
            'enable_keyboard_shortcuts': os.getenv('UI_ENABLE_KEYBOARD_SHORTCUTS', 'true').lower() == 'true',
            'color_coding': os.getenv('UI_COLOR_CODING', 'true').lower() == 'true'
        }

    def get_reports_config(self) -> Dict[str, Any]:
        """Obtiene configuración de reportes desde variables de entorno"""
        return {
            'max_backups': int(os.getenv('REPORTS_MAX_BACKUPS', '10')),
            'date_format': os.getenv('REPORTS_DATE_FORMAT', '%d/%m/%Y'),
            'currency_format': os.getenv('REPORTS_CURRENCY_FORMAT', 'CLP')
        }

    def set_env_var(self, key: str, value: str):
        """Establece una variable de entorno"""
        os.environ[key] = value

    def get_env_var(self, key: str, default: str = None) -> str:
        """Obtiene una variable de entorno"""
        return os.getenv(key, default)

    def create_env_file_template(self):
        """Crea un archivo .env de ejemplo"""
        env_template = """# Configuración de Base de Datos
DB_TYPE=json
# DB_TYPE=mongodb
DB_JSON_FILE=data/cuentas.json
DB_MONGODB_URI=mongodb://localhost:27017/
DB_MONGODB_DATABASE=registro_servicios_chile
DB_AUTO_MIGRATE=true

# Configuración de Aplicación
APP_TITLE=Registro de Servicios Chile
APP_VERSION=3.0.0
APP_AUTHOR=Usuario
APP_WINDOW_SIZE=1400x800
APP_MIN_WINDOW_SIZE=1000x700
APP_THEME=modern
APP_AUTO_SAVE=true
APP_SHOW_NOTIFICATIONS=true
APP_CHECK_UPDATES=true

# Configuración de Notificaciones
NOTIFICATIONS_ENABLED=true
NOTIFICATIONS_CHECK_INTERVAL=300
NOTIFICATIONS_DAYS_BEFORE_DUE=3
NOTIFICATIONS_DAYS_BEFORE_CUT=1
NOTIFICATIONS_SOUND_ENABLED=false
NOTIFICATIONS_DESKTOP=true

# Configuración de UI
UI_SHOW_TOOLTIPS=true
UI_ANIMATE_TRANSITIONS=true
UI_AUTO_REFRESH=true
UI_REFRESH_INTERVAL=60
UI_SHOW_PROGRESS_BARS=true
UI_ENABLE_KEYBOARD_SHORTCUTS=true
UI_COLOR_CODING=true

# Configuración de Reportes
REPORTS_MAX_BACKUPS=10
REPORTS_DATE_FORMAT=%d/%m/%Y
REPORTS_CURRENCY_FORMAT=CLP

# Configuración de MongoDB Atlas (opcional)
# DB_MONGODB_URI=mongodb+srv://usuario:password@cluster.mongodb.net/
# DB_MONGODB_DATABASE=registro_servicios_prod

# Configuración de Desarrollo
# DEBUG=true
# LOG_LEVEL=DEBUG
"""

        env_file = self.base_dir / '.env.example'
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)

        print(f"✅ Archivo de ejemplo creado: {env_file}")
        print("💡 Copia .env.example a .env y personaliza las variables")

        return env_file

    def validate_config(self) -> Dict[str, bool]:
        """Valida la configuración actual"""
        validation_results = {}

        # Validar configuración de base de datos
        db_config = self.get_database_config()
        validation_results['database'] = db_config['type'] in ['json', 'mongodb']

        # Validar configuración de aplicación
        app_config = self.get_app_config()
        validation_results['app_window_size'] = 'x' in app_config['window_size']
        validation_results['app_theme'] = app_config['theme'] in ['classic', 'modern', 'dark']

        # Validar configuración de notificaciones
        notif_config = self.get_notifications_config()
        validation_results['notifications_interval'] = notif_config['check_interval'] > 0
        validation_results['notifications_days'] = notif_config['days_before_due'] > 0

        # Validar configuración de UI
        ui_config = self.get_ui_config()
        validation_results['ui_refresh_interval'] = ui_config['refresh_interval'] > 0

        return validation_results

    def print_current_config(self):
        """Imprime la configuración actual"""
        print("\n🔧 CONFIGURACIÓN ACTUAL")
        print("=" * 50)

        print("\n📊 Base de Datos:")
        db_config = self.get_database_config()
        for key, value in db_config.items():
            print(f"  {key}: {value}")

        print("\n🖥️ Aplicación:")
        app_config = self.get_app_config()
        for key, value in app_config.items():
            print(f"  {key}: {value}")

        print("\n🔔 Notificaciones:")
        notif_config = self.get_notifications_config()
        for key, value in notif_config.items():
            print(f"  {key}: {value}")

        print("\n🎨 Interfaz de Usuario:")
        ui_config = self.get_ui_config()
        for key, value in ui_config.items():
            print(f"  {key}: {value}")


# Instancia global del gestor de configuración
env_config = EnvironmentConfig()