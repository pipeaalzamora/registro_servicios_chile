@echo off
echo Instalando Registro de Servicios Chile...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está instalado o no está en el PATH
    echo Por favor instale Python 3.8 o superior desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado. Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error al instalar dependencias
    pause
    exit /b 1
)

echo.
echo Instalación completada exitosamente!
echo Para ejecutar la aplicación, use: python main.py
echo.
pause