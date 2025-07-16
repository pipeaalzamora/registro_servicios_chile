"""
Servicio de predicción de montos usando Machine Learning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
from pathlib import Path

from ..domain.entities import CuentaServicio, TipoServicio


class PredictionService:
    """Servicio para predecir montos de servicios usando ML"""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

        # Modelos por tipo de servicio
        self.models: Dict[str, RandomForestRegressor] = {}
        self.scalers: Dict[str, StandardScaler] = {}

        # Cargar modelos existentes
        self._load_models()

    def _load_models(self):
        """Carga modelos guardados previamente"""
        for tipo in TipoServicio:
            model_path = self.models_dir / f"model_{tipo.value}.joblib"
            scaler_path = self.models_dir / f"scaler_{tipo.value}.joblib"

            if model_path.exists() and scaler_path.exists():
                try:
                    self.models[tipo.value] = joblib.load(model_path)
                    self.scalers[tipo.value] = joblib.load(scaler_path)
                except Exception as e:
                    print(f"Error cargando modelo para {tipo.value}: {e}")

    def _save_models(self):
        """Guarda los modelos entrenados"""
        for tipo, model in self.models.items():
            model_path = self.models_dir / f"model_{tipo}.joblib"
            scaler_path = self.models_dir / f"scaler_{tipo}.joblib"

            joblib.dump(model, model_path)
            joblib.dump(self.scalers[tipo], scaler_path)

    def _extract_features(self, cuenta: CuentaServicio) -> List[float]:
        """Extrae características de una cuenta para el modelo"""
        fecha_emision = cuenta.fecha_emision

        features = [
            float(fecha_emision.month),  # Mes del año (1-12)
            float(fecha_emision.day),    # Día del mes (1-31)
            float(fecha_emision.weekday()),  # Día de la semana (0-6)
            float((fecha_emision - cuenta.fecha_vencimiento).days),  # Días entre emisión y vencimiento
            float(fecha_emision.year),   # Año
        ]

        # Características estacionales
        features.extend([
            np.sin(2 * np.pi * fecha_emision.month / 12),  # Sinusoidal del mes
            np.cos(2 * np.pi * fecha_emision.month / 12),  # Cosenoidal del mes
        ])

        # Características de temporada
        features.extend([
            1.0 if fecha_emision.month in [12, 1, 2] else 0.0,  # Verano
            1.0 if fecha_emision.month in [6, 7, 8] else 0.0,   # Invierno
        ])

        return features

    def _prepare_training_data(self, cuentas: List[CuentaServicio]) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Prepara datos de entrenamiento por tipo de servicio"""
        training_data = {}

        for tipo in TipoServicio:
            # Filtrar cuentas por tipo
            cuentas_tipo = [c for c in cuentas if c.tipo_servicio == tipo]

            if len(cuentas_tipo) < 5:  # Necesitamos al menos 5 muestras
                continue

            X = []
            y = []

            for cuenta in cuentas_tipo:
                features = self._extract_features(cuenta)
                X.append(features)
                y.append(cuenta.monto)

            if X and y:
                training_data[tipo.value] = (np.array(X), np.array(y))

        return training_data

    def train_models(self, cuentas: List[CuentaServicio]) -> Dict[str, float]:
        """Entrena modelos de predicción para cada tipo de servicio"""
        print("Iniciando entrenamiento de modelos de predicción...")

        training_data = self._prepare_training_data(cuentas)
        results = {}

        for tipo, (X, y) in training_data.items():
            try:
                # Dividir datos en entrenamiento y validación
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                # Escalar características
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_val_scaled = scaler.transform(X_val)

                # Entrenar modelo
                model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )

                model.fit(X_train_scaled, y_train)

                # Evaluar modelo
                y_pred = model.predict(X_val_scaled)
                mae = mean_absolute_error(y_val, y_pred)
                mse = mean_squared_error(y_val, y_pred)
                rmse = np.sqrt(mse)

                # Calcular precisión como porcentaje del monto promedio
                avg_amount = np.mean(y_val)
                accuracy = (1 - mae / avg_amount) * 100 if avg_amount > 0 else 0

                # Guardar modelo y scaler
                self.models[tipo] = model
                self.scalers[tipo] = scaler

                results[tipo] = {
                    'mae': mae,
                    'rmse': rmse,
                    'accuracy': accuracy,
                    'samples': len(X)
                }

                print(f"Modelo {tipo}: MAE=${mae:.0f}, RMSE=${rmse:.0f}, Precisión={accuracy:.1f}%, Muestras={len(X)}")

            except Exception as e:
                print(f"Error entrenando modelo para {tipo}: {e}")
                results[tipo] = {'error': str(e)}

        # Guardar modelos
        self._save_models()

        return results

    def predict_amount(self, tipo_servicio: TipoServicio, fecha_emision: datetime,
                      fecha_vencimiento: datetime) -> Optional[float]:
        """Predice el monto para una cuenta futura"""
        if tipo_servicio.value not in self.models:
            return None

        try:
            # Crear cuenta temporal para extraer características
            temp_cuenta = CuentaServicio(
                id="temp",
                tipo_servicio=tipo_servicio,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                monto=0,
                descripcion=""
            )

            features = self._extract_features(temp_cuenta)
            features_scaled = self.scalers[tipo_servicio.value].transform([features])

            prediction = self.models[tipo_servicio.value].predict(features_scaled)[0]

            # Asegurar que la predicción sea positiva
            return max(0.0, float(prediction))

        except Exception as e:
            print(f"Error en predicción para {tipo_servicio.value}: {e}")
            return None

    def get_prediction_confidence(self, tipo_servicio: TipoServicio,
                                fecha_emision: datetime, fecha_vencimiento: datetime) -> Optional[float]:
        """Obtiene el nivel de confianza de la predicción"""
        if tipo_servicio.value not in self.models:
            return None

        try:
            temp_cuenta = CuentaServicio(
                id="temp",
                tipo_servicio=tipo_servicio,
                fecha_emision=fecha_emision,
                fecha_vencimiento=fecha_vencimiento,
                monto=0,
                descripcion=""
            )

            features = self._extract_features(temp_cuenta)
            features_scaled = self.scalers[tipo_servicio.value].transform([features])

            # Obtener predicciones de todos los árboles
            predictions = []
            for estimator in self.models[tipo_servicio.value].estimators_:
                pred = estimator.predict(features_scaled)[0]
                predictions.append(pred)

            # Calcular confianza basada en la desviación estándar
            std = np.std(predictions)
            mean = np.mean(predictions)

            # Confianza inversamente proporcional a la desviación estándar
            confidence = max(0, 100 - (std / mean * 100)) if mean > 0 else 0

            return min(100, confidence)

        except Exception as e:
            print(f"Error calculando confianza para {tipo_servicio.value}: {e}")
            return None

    def get_trend_analysis(self, cuentas: List[CuentaServicio],
                          tipo_servicio: TipoServicio) -> Dict[str, any]:
        """Analiza tendencias de precios para un tipo de servicio"""
        cuentas_tipo = [c for c in cuentas if c.tipo_servicio == tipo_servicio]

        if len(cuentas_tipo) < 3:
            return {'error': 'Insuficientes datos para análisis'}

        # Ordenar por fecha
        cuentas_tipo.sort(key=lambda x: x.fecha_emision)

        # Calcular estadísticas
        montos = [c.monto for c in cuentas_tipo]
        fechas = [c.fecha_emision for c in cuentas_tipo]

        # Tendencia lineal simple
        x = np.arange(len(montos))
        z = np.polyfit(x, montos, 1)
        trend_slope = z[0]

        # Análisis estacional
        montos_por_mes = {}
        for cuenta in cuentas_tipo:
            mes = cuenta.fecha_emision.month
            if mes not in montos_por_mes:
                montos_por_mes[mes] = []
            montos_por_mes[mes].append(cuenta.monto)

        # Promedio por mes
        promedio_por_mes = {mes: np.mean(montos) for mes, montos in montos_por_mes.items()}

        return {
            'total_cuentas': len(cuentas_tipo),
            'promedio_actual': np.mean(montos),
            'tendencia': 'creciente' if trend_slope > 0 else 'decreciente' if trend_slope < 0 else 'estable',
            'cambio_promedio_mensual': trend_slope,
            'promedio_por_mes': promedio_por_mes,
            'ultimo_monto': montos[-1] if montos else 0,
            'primer_monto': montos[0] if montos else 0,
            'variacion_total': ((montos[-1] - montos[0]) / montos[0] * 100) if montos and montos[0] > 0 else 0
        }

    def suggest_optimal_payment_date(self, cuenta: CuentaServicio) -> Optional[datetime]:
        """Sugiere la fecha óptima de pago basada en el historial"""
        # Por ahora, una lógica simple: pagar 3 días antes del vencimiento
        # En el futuro, podría usar ML para optimizar esto
        return cuenta.fecha_vencimiento - timedelta(days=3)


# Instancia global del servicio de predicción
prediction_service = PredictionService()