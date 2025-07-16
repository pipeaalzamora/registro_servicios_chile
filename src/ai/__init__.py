"""
Módulo de Inteligencia Artificial para la aplicación
"""

from .prediction_service import PredictionService, prediction_service
from .ocr_service import OCRService, ocr_service
from .advanced_prediction_service import AdvancedPredictionService, advanced_prediction_service
from .recommendation_service import RecommendationService, recommendation_service

__all__ = [
    'PredictionService',
    'prediction_service',
    'OCRService',
    'ocr_service',
    'AdvancedPredictionService',
    'advanced_prediction_service',
    'RecommendationService',
    'recommendation_service'
]