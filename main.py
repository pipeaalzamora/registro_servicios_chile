#!/usr/bin/env python3
"""
Registro de Servicios Chile
Aplicación para llevar el control de cuentas básicas con exportación a PDF
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path para importaciones
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.infrastructure.repositories import JSONCuentaServicioRepository, JSONResumenRepository
from src.infrastructure.pdf_service import PDFService
from src.application.casos_uso import GestionarCuentaServicio, GenerarReportes, Notificaciones
from src.presentation.main_window import MainWindow

def main():
    """Función principal de la aplicación"""
    try:
        print("Iniciando Registro de Servicios Chile...")

        # Crear directorios necesarios
        Path("data").mkdir(exist_ok=True)
        Path("reports").mkdir(exist_ok=True)

        # Inicializar repositorios
        print("Inicializando repositorios...")
        cuenta_repository = JSONCuentaServicioRepository("data")
        resumen_repository = JSONResumenRepository(cuenta_repository)

        # Inicializar servicios
        print("Inicializando servicios...")
        pdf_service = PDFService("reports")

        # Inicializar casos de uso
        print("Inicializando casos de uso...")
        gestionar_cuenta = GestionarCuentaServicio(cuenta_repository)
        generar_reportes = GenerarReportes(cuenta_repository, resumen_repository)
        notificaciones = Notificaciones(cuenta_repository)

        # Crear y ejecutar la interfaz de usuario
        print("Iniciando interfaz de usuario...")
        app = MainWindow(gestionar_cuenta, generar_reportes, notificaciones, pdf_service)
        app.run()

    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()