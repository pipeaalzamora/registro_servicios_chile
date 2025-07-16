"""
Servicio de predicción avanzado con múltiples algoritmos de ML
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import joblib
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from ..domain.entities import CuentaServicio, TipoServicio


class AdvancedPredictionService:
    """Servicio avanzado de predicción con múltiples algoritmos"""

    def __init__(self, models_dir: str = "models/advanced"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Múltiples modelos por tipo de servicio
        self.models: Dict[str, Dict[str, Any]] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        self.feature_importances: Dict[str, Dict[str, float]] = {}

        # Configuración de algoritmos
        self.algorithms = {
            'random_forest': RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=150, max_depth=8, random_state=42),
            'extra_trees': ExtraTreesRegressor(n_estimators=200, max_depth=15, random_state=42),
            'svr': SVR(kernel='rbf', C=100, gamma='scale'),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1)
        }

        # Cargar modelos existentes
        self._load_models()

    def _load_models(self):
        """Carga modelos guardados previamente"""
        for tipo in TipoServicio:
            model_path = self.models_dir / f"advanced_model_{tipo.value}.joblib"
            scaler_path = self.models_dir / f"advanced_scaler_{tipo.value}.joblib"
            importance_path = self.models_dir / f"importance_{tipo.value}.joblib"

            if model_path.exists() and scaler_path.exists():
                try:
                    self.models[tipo.value] = joblib.load(model_path)
                    self.scalers[tipo.value] = joblib.load(scaler_path)
                    if importance_path.exists():
                        self.feature_importances[tipo.value] = joblib.load(importance_path)
                except Exception as e:
                    print(f"Error cargando modelo avanzado para {tipo.value}: {e}")

    def _save_models(self):
        """Guarda los modelos entrenados"""
        for tipo, model_dict in self.models.items():
            model_path = self.models_dir / f"advanced_model_{tipo}.joblib"
            scaler_path = self.models_dir / f"advanced_scaler_{tipo}.joblib"
            importance_path = self.models_dir / f"importance_{tipo}.joblib"

            joblib.dump(model_dict, model_path)
            joblib.dump(self.scalers[tipo], scaler_path)
            if tipo in self.feature_importances:
                joblib.dump(self.feature_importances[tipo], importance_path)

    def _extract_advanced_features(self, cuenta: CuentaServicio) -> List[float]:
        """Extrae características avanzadas para el modelo"""
        fecha_emision = cuenta.fecha_emision
        fecha_vencimiento = cuenta.fecha_vencimiento

        # Características temporales básicas
        features = [
            float(fecha_emision.month),  # Mes del año (1-12)
            float(fecha_emision.day),    # Día del mes (1-31)
            float(fecha_emision.weekday()),  # Día de la semana (0-6)
            float((fecha_vencimiento - fecha_emision).days),  # Días entre emisión y vencimiento
            float(fecha_emision.year),   # Año
            float(fecha_emision.dayofyear),  # Día del año (1-365)
        ]

        # Características estacionales avanzadas
        features.extend([
            np.sin(2 * np.pi * fecha_emision.month / 12),  # Sinusoidal del mes
            np.cos(2 * np.pi * fecha_emision.month / 12),  # Cosenoidal del mes
            np.sin(2 * np.pi * fecha_emision.dayofyear / 365),  # Sinusoidal del año
            np.cos(2 * np.pi * fecha_emision.dayofyear / 365),  # Cosenoidal del año
        ])

        # Características de temporada más detalladas
        features.extend([
            1.0 if fecha_emision.month in [12, 1, 2] else 0.0,  # Verano
            1.0 if fecha_emision.month in [3, 4, 5] else 0.0,   # Otoño
            1.0 if fecha_emision.month in [6, 7, 8] else 0.0,   # Invierno
            1.0 if fecha_emision.month in [9, 10, 11] else 0.0, # Primavera
        ])

        # Características de fin de mes/semana
        features.extend([
            1.0 if fecha_emision.day >= 25 else 0.0,  # Fin de mes
            1.0 if fecha_emision.weekday() >= 5 else 0.0,  # Fin de semana
        ])

        # Características de días festivos (simplificado)
        # En una implementación real, se usaría una librería de festivos chilenos
        is_holiday = 0.0
        if fecha_emision.month == 1 and fecha_emision.day == 1:  # Año Nuevo
            is_holiday = 1.0
        elif fecha_emision.month == 5 and fecha_emision.day == 1:  # Día del Trabajo
            is_holiday = 1.0
        elif fecha_emision.month == 9 and fecha_emision.day == 18:  # Fiestas Patrias
            is_holiday = 1.0
        elif fecha_emision.month == 12 and fecha_emision.day == 25:  # Navidad
            is_holiday = 1.0

        features.append(is_holiday)

        return features

    def _prepare_advanced_training_data(self, cuentas: List[CuentaServicio]) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Prepara datos de entrenamiento avanzados por tipo de servicio"""
        training_data = {}

        for tipo in TipoServicio:
            # Filtrar cuentas por tipo
            cuentas_tipo = [c for c in cuentas if c.tipo_servicio == tipo]

            if len(cuentas_tipo) < 10:  # Necesitamos al menos 10 muestras
                continue

            X = []
            y = []

            for cuenta in cuentas_tipo:
                features = self._extract_advanced_features(cuenta)
                X.append(features)
                y.append(cuenta.monto)

            if X and y:
                training_data[tipo.value] = (np.array(X), np.array(y))

        return training_data

    def train_advanced_models(self, cuentas: List[CuentaServicio]) -> Dict[str, Dict[str, Any]]:
        """Entrena múltiples modelos avanzados para cada tipo de servicio"""
        print("Iniciando entrenamiento de modelos avanzados...")

        training_data = self._prepare_advanced_training_data(cuentas)
        results = {}

        for tipo, (X, y) in training_data.items():
            try:
                print(f"\nEntrenando modelos para {tipo}...")

                # Dividir datos
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                # Escalar características
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_val_scaled = scaler.transform(X_val)

                # Entrenar múltiples modelos
                model_results = {}
                best_model = None
                best_score = float('-inf')

                for name, algorithm in self.algorithms.items():
                    try:
                        # Entrenar modelo
                        model = algorithm.fit(X_train_scaled, y_train)

                        # Evaluar modelo
                        y_pred = model.predict(X_val_scaled)
                        mae = mean_absolute_error(y_val, y_pred)
                        mse = mean_squared_error(y_val, y_pred)
                        rmse = np.sqrt(mse)
                        r2 = r2_score(y_val, y_pred)

                        # Calcular precisión como porcentaje del monto promedio
                        avg_amount = np.mean(y_val)
                        accuracy = (1 - mae / avg_amount) * 100 if avg_amount > 0 else 0

                        model_results[name] = {
                            'model': model,
                            'mae': mae,
                            'rmse': rmse,
                            'r2': r2,
                            'accuracy': accuracy,
                            'predictions': y_pred
                        }

                        # Guardar el mejor modelo basado en R²
                        if r2 > best_score:
                            best_score = r2
                            best_model = name

                        print(f"  {name}: R²={r2:.3f}, MAE=${mae:.0f}, Precisión={accuracy:.1f}%")

                    except Exception as e:
                        print(f"  Error con {name}: {e}")
                        continue

                # Guardar modelos y resultados
                self.models[tipo] = model_results
                self.scalers[tipo] = scaler

                # Calcular importancia de características para el mejor modelo
                if best_model and hasattr(model_results[best_model]['model'], 'feature_importances_'):
                    self.feature_importances[tipo] = {
                        'model': best_model,
                        'importances': model_results[best_model]['model'].feature_importances_
                    }

                results[tipo] = {
                    'best_model': best_model,
                    'best_r2': best_score,
                    'models_trained': len(model_results),
                    'samples': len(X),
                    'model_results': model_results
                }

            except Exception as e:
                print(f"Error entrenando modelos avanzados para {tipo}: {e}")
                results[tipo] = {'error': str(e)}

        # Guardar modelos
        self._save_models()

        return results

    def predict_with_ensemble(self, tipo_servicio: TipoServicio, fecha_emision: datetime,
                            fecha_vencimiento: datetime) -> Optional[Dict[str, Any]]:
        """Predice usando un ensemble de modelos"""
        if tipo_servicio.value not in self.models:
            return None

        try:
            # Crear cuenta temporal
            temp_cuenta = CuentaServicio(
                id="temp",
                tipo_servicio=tipo_servicio,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                monto=0,
                descripcion=""
            )

            features = self._extract_advanced_features(temp_cuenta)
            features_scaled = self.scalers[tipo_servicio.value].transform([features])

            # Obtener predicciones de todos los modelos
            predictions = {}
            for name, model_data in self.models[tipo_servicio.value].items():
                try:
                    pred = model_data['model'].predict(features_scaled)[0]
                    predictions[name] = max(0.0, float(pred))
                except:
                    continue

            if not predictions:
                return None

            # Calcular predicción ensemble (promedio ponderado por R²)
            total_weight = 0
            weighted_sum = 0

            for name, pred in predictions.items():
                r2 = self.models[tipo_servicio.value][name]['r2']
                weight = max(0, r2)  # Solo usar modelos con R² positivo
                weighted_sum += pred * weight
                total_weight += weight

            ensemble_prediction = weighted_sum / total_weight if total_weight > 0 else np.mean(list(predictions.values()))

            # Calcular confianza basada en la consistencia de predicciones
            predictions_list = list(predictions.values())
            std = np.std(predictions_list)
            mean = np.mean(predictions_list)
            confidence = max(0, 100 - (std / mean * 100)) if mean > 0 else 0

            return {
                'ensemble_prediction': ensemble_prediction,
                'individual_predictions': predictions,
                'confidence': min(100, confidence),
                'models_used': len(predictions)
            }

        except Exception as e:
            print(f"Error en predicción ensemble para {tipo_servicio.value}: {e}")
            return None

    def get_feature_importance_analysis(self, tipo_servicio: TipoServicio) -> Optional[Dict[str, Any]]:
        """Obtiene análisis de importancia de características"""
        if tipo_servicio.value not in self.feature_importances:
            return None

        try:
            importance_data = self.feature_importances[tipo_servicio.value]
            importances = importance_data['importances']

            # Nombres de características
            feature_names = [
                'Mes', 'Día', 'Día Semana', 'Días Vencimiento', 'Año', 'Día Año',
                'Sin Mes', 'Cos Mes', 'Sin Año', 'Cos Año',
                'Verano', 'Otoño', 'Invierno', 'Primavera',
                'Fin Mes', 'Fin Semana', 'Festivo'
            ]

            # Crear ranking de características
            feature_ranking = []
            for i, importance in enumerate(importances):
                feature_ranking.append({
                    'feature': feature_names[i] if i < len(feature_names) else f'Feature_{i}',
                    'importance': float(importance)
                })

            # Ordenar por importancia
            feature_ranking.sort(key=lambda x: x['importance'], reverse=True)

            return {
                'best_model': importance_data['model'],
                'feature_ranking': feature_ranking,
                'top_features': feature_ranking[:5]
            }

        except Exception as e:
            print(f"Error obteniendo importancia de características para {tipo_servicio.value}: {e}")
            return None

    def get_advanced_trend_analysis(self, cuentas: List[CuentaServicio],
                                  tipo_servicio: TipoServicio) -> Dict[str, Any]:
        """Análisis avanzado de tendencias con múltiples métricas"""
        cuentas_tipo = [c for c in cuentas if c.tipo_servicio == tipo_servicio]

        if len(cuentas_tipo) < 5:
            return {'error': 'Insuficientes datos para análisis avanzado'}

        # Ordenar por fecha
        cuentas_tipo.sort(key=lambda x: x.fecha_emision)

        # Calcular estadísticas avanzadas
        montos = [c.monto for c in cuentas_tipo]
        fechas = [c.fecha_emision for c in cuentas_tipo]

        # Análisis de tendencia con regresión polinomial
        x = np.arange(len(montos))

        # Tendencia lineal
        z_linear = np.polyfit(x, montos, 1)
        trend_slope = z_linear[0]

        # Tendencia cuadrática
        z_quad = np.polyfit(x, montos, 2)
        trend_acceleration = z_quad[0]

        # Análisis de volatilidad
        returns = np.diff(montos) / montos[:-1] if len(montos) > 1 else [0]
        volatility = np.std(returns) if len(returns) > 0 else 0

        # Análisis estacional avanzado
        montos_por_mes = {}
        for cuenta in cuentas_tipo:
            mes = cuenta.fecha_emision.month
            if mes not in montos_por_mes:
                montos_por_mes[mes] = []
            montos_por_mes[mes].append(cuenta.monto)

        # Estadísticas por mes
        monthly_stats = {}
        for mes, montos_mes in montos_por_mes.items():
            monthly_stats[mes] = {
                'promedio': np.mean(montos_mes),
                'mediana': np.median(montos_mes),
                'std': np.std(montos_mes),
                'count': len(montos_mes)
            }

        # Detectar estacionalidad
        seasonal_pattern = self._detect_seasonality(montos_por_mes)

        # Predicción simple para el próximo mes
        next_month_prediction = montos[-1] + trend_slope if len(montos) > 0 else 0

        return {
            'total_cuentas': len(cuentas_tipo),
            'promedio_actual': np.mean(montos),
            'mediana': np.median(montos),
            'tendencia_lineal': 'creciente' if trend_slope > 0 else 'decreciente' if trend_slope < 0 else 'estable',
            'tendencia_cuadratica': 'acelerando' if trend_acceleration > 0 else 'desacelerando' if trend_acceleration < 0 else 'constante',
            'cambio_promedio_mensual': trend_slope,
            'volatilidad': volatility,
            'estacionalidad': seasonal_pattern,
            'prediccion_proximo_mes': next_month_prediction,
            'estadisticas_mensuales': monthly_stats,
            'ultimo_monto': montos[-1] if montos else 0,
            'primer_monto': montos[0] if montos else 0,
            'variacion_total': ((montos[-1] - montos[0]) / montos[0] * 100) if montos and montos[0] > 0 else 0
        }

    def _detect_seasonality(self, montos_por_mes: Dict[int, List[float]]) -> str:
        """Detecta patrones estacionales en los datos"""
        if len(montos_por_mes) < 4:
            return "insuficientes datos"

        # Calcular coeficiente de variación por mes
        cv_por_mes = {}
        for mes, montos in montos_por_mes.items():
            if len(montos) > 1:
                cv = np.std(montos) / np.mean(montos)
                cv_por_mes[mes] = cv

        if not cv_por_mes:
            return "sin variación"

        # Detectar estacionalidad basada en la variación
        avg_cv = np.mean(list(cv_por_mes.values()))

        if avg_cv > 0.3:
            return "alta estacionalidad"
        elif avg_cv > 0.15:
            return "moderada estacionalidad"
        else:
            return "baja estacionalidad"


# Instancia global del servicio avanzado
advanced_prediction_service = AdvancedPredictionService()