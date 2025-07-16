"""
Utilidades para manejo centralizado de errores en la interfaz de usuario
"""

import functools
import logging
from typing import Callable, Optional, Type, Union
from tkinter import messagebox

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorHandler:
    """Clase para manejo centralizado de errores"""

    @staticmethod
    def handle_ui_error(error_message: str, title: str = "Error", log_error: bool = True):
        """
        Maneja errores de UI mostrando un messagebox

        Args:
            error_message: Mensaje de error a mostrar
            title: Título del diálogo de error
            log_error: Si se debe registrar el error en el log
        """
        if log_error:
            logger.error(f"UI Error - {title}: {error_message}")

        messagebox.showerror(title, error_message)

    @staticmethod
    def handle_validation_error(error_message: str, log_error: bool = True):
        """
        Maneja errores de validación

        Args:
            error_message: Mensaje de error de validación
            log_error: Si se debe registrar el error en el log
        """
        ErrorHandler.handle_ui_error(error_message, "Error de Validación", log_error)

    @staticmethod
    def handle_data_error(error_message: str, log_error: bool = True):
        """
        Maneja errores de datos

        Args:
            error_message: Mensaje de error de datos
            log_error: Si se debe registrar el error en el log
        """
        ErrorHandler.handle_ui_error(error_message, "Error de Datos", log_error)

    @staticmethod
    def handle_unexpected_error(error: Exception, context: str = "", log_error: bool = True):
        """
        Maneja errores inesperados

        Args:
            error: Excepción capturada
            context: Contexto adicional del error
            log_error: Si se debe registrar el error en el log
        """
        error_message = f"Error inesperado: {str(error)}"
        if context:
            error_message = f"{context}: {error_message}"

        if log_error:
            logger.error(f"Unexpected Error - {context}: {str(error)}", exc_info=True)

        ErrorHandler.handle_ui_error(error_message, "Error Inesperado", False)


def handle_ui_errors(title: str = "Error", context: str = ""):
    """
    Decorador para manejar errores de UI automáticamente

    Args:
        title: Título del diálogo de error
        context: Contexto adicional para logging

    Usage:
        @handle_ui_errors("Error al guardar", "CuentaDialog.guardar")
        def guardar_cuenta(self):
            # código que puede fallar
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = f"Error en {func.__name__}: {str(e)}"
                if context:
                    error_message = f"{context}: {error_message}"

                ErrorHandler.handle_ui_error(error_message, title)
                return None
        return wrapper
    return decorator


def handle_validation_errors(context: str = ""):
    """
    Decorador para manejar errores de validación

    Args:
        context: Contexto adicional para logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                ErrorHandler.handle_validation_error(str(e))
                return None
            except Exception as e:
                error_message = f"Error inesperado en {func.__name__}: {str(e)}"
                if context:
                    error_message = f"{context}: {error_message}"
                ErrorHandler.handle_unexpected_error(e, context)
                return None
        return wrapper
    return decorator


def safe_execute(func: Callable, error_message: str, title: str = "Error",
                default_return=None, log_error: bool = True):
    """
    Ejecuta una función de forma segura con manejo de errores

    Args:
        func: Función a ejecutar
        error_message: Mensaje de error base
        title: Título del diálogo de error
        default_return: Valor a retornar en caso de error
        log_error: Si se debe registrar el error en el log

    Returns:
        Resultado de la función o default_return si hay error
    """
    try:
        return func()
    except Exception as e:
        full_error_message = f"{error_message}: {str(e)}"
        ErrorHandler.handle_ui_error(full_error_message, title, log_error)
        return default_return


def validate_and_execute(validation_func: Callable, execution_func: Callable,
                        error_message: str, title: str = "Error de Validación"):
    """
    Valida y ejecuta una función de forma segura

    Args:
        validation_func: Función de validación que retorna (bool, str)
        execution_func: Función a ejecutar si la validación pasa
        error_message: Mensaje de error base
        title: Título del diálogo de error

    Returns:
        Resultado de execution_func o None si hay error
    """
    try:
        is_valid, validation_error = validation_func()
        if not is_valid:
            ErrorHandler.handle_validation_error(validation_error or error_message)
            return None

        return execution_func()
    except Exception as e:
        ErrorHandler.handle_unexpected_error(e, error_message)
        return None


# Instancia global para uso directo
error_handler = ErrorHandler()