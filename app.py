#!/usr/bin/env python3
"""
Registro de Servicios Chile - Aplicación Principal
Versión simplificada y optimizada
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
from pathlib import Path

from models import CuentaServicio, TipoServicio
from database_mongodb import DatabaseManager
from reports import ReportGenerator
from ui.main_window import MainWindow
from config import DATABASE_CONFIG


def main():
    """Función principal de la aplicación"""
    try:
        print("Iniciando Registro de Servicios Chile...")

        # Crear directorios necesarios
        Path("data").mkdir(exist_ok=True)
        Path("reports").mkdir(exist_ok=True)
        Path("backups").mkdir(exist_ok=True)

        # Inicializar base de datos
        db_manager = DatabaseManager(DATABASE_CONFIG.get('type', 'json'))

        # Mostrar información de conexión
        conn_info = db_manager.get_connection_info()
        print(f"Base de datos: {conn_info['type']} - {conn_info['status']}")

        # Inicializar generador de reportes
        report_generator = ReportGenerator()

        # Crear y ejecutar la interfaz de usuario
        app = MainWindow(db_manager, report_generator)

        try:
            app.run()
        finally:
            # Cerrar conexión a la base de datos
            db_manager.close()

    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        messagebox.showerror("Error", f"Error al iniciar la aplicación:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()