"""
Utilidades para la capa de presentación
"""

from .error_handler import (
    ErrorHandler,
    error_handler,
    handle_ui_errors,
    handle_validation_errors,
    safe_execute,
    validate_and_execute
)

__all__ = [
    'ErrorHandler',
    'error_handler',
    'handle_ui_errors',
    'handle_validation_errors',
    'safe_execute',
    'validate_and_execute'
]