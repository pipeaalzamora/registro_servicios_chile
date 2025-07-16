"""
Panel de Inteligencia Artificial Avanzado
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from typing import Optional
import os

from ...domain.entities import TipoServicio
from ...ai import prediction_service, ocr_service
from ...ai.advanced_prediction_service import advanced_prediction_service
from ...ai.recommendation_service import recommendation_service
from ..utils import error_handler, handle_ui_errors


class AdvancedAIPanel:
    """Panel avanzado para funcionalidades de Inteligencia Artificial"""

    def __init__(self, parent, gestionar_cuenta):
        self.parent = parent
        self.gestionar_cuenta = gestionar_cuenta
        self.current_tab = None

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del panel"""
        # Frame principal
        self.main_frame = ttk.LabelFrame(self.parent, text="🤖 IA Avanzada", padding="10")

        # Configurar grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # Barra de navegación superior
        self.create_navigation_bar()

        # Notebook para pestañas
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # Crear pestañas
        self.create_prediction_tab()
        self.create_recommendations_tab()
        self.create_ocr_tab()
        self.create_analysis_tab()
        self.create_insights_tab()

    def create_navigation_bar(self):
        """Crea la barra de navegación"""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        nav_frame.columnconfigure(0, weight=1)

        # Botón para volver al panel principal
        back_button = tk.Button(
            nav_frame,
            text="🏠 Volver al Panel Principal",
            command=self.volver_al_principal,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        back_button.grid(row=0, column=0, sticky="w")

        # Título centrado
        title_label = tk.Label(
            nav_frame,
            text="🚀 IA Avanzada - Análisis Inteligente",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=1)

        # Botón de ayuda
        help_button = tk.Button(
            nav_frame,
            text="❓ Ayuda IA Avanzada",
            command=self.mostrar_ayuda_avanzada,
            relief="flat",
            borderwidth=1,
            padx=8,
            pady=5,
            cursor="hand2"
        )
        help_button.grid(row=0, column=2, sticky="e")

    def create_prediction_tab(self):
        """Crea la pestaña de predicciones avanzadas"""
        prediction_frame = ttk.Frame(self.notebook)
        self.notebook.add(prediction_frame, text="🔮 Predicciones")

        # Configurar grid
        prediction_frame.columnconfigure(0, weight=1)
        prediction_frame.columnconfigure(1, weight=1)
        prediction_frame.rowconfigure(1, weight=1)

        # Panel izquierdo - Controles
        controls_frame = ttk.LabelFrame(prediction_frame, text="Controles", padding="8")
        controls_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))

        # Botón para entrenar modelos avanzados
        train_advanced_button = tk.Button(
            controls_frame,
            text="🚀 Entrenar Modelos Avanzados",
            command=self.train_advanced_models,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        train_advanced_button.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Frame para predicción
        pred_input_frame = ttk.Frame(controls_frame)
        pred_input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        # Tipo de servicio
        ttk.Label(pred_input_frame, text="Tipo de Servicio:").grid(row=0, column=0, sticky="w", pady=2)
        self.tipo_var = tk.StringVar()
        tipo_combo = ttk.Combobox(
            pred_input_frame,
            textvariable=self.tipo_var,
            values=[t.value for t in TipoServicio],
            state="readonly",
            width=20
        )
        tipo_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)

        # Fecha de emisión
        ttk.Label(pred_input_frame, text="Fecha de Emisión:").grid(row=1, column=0, sticky="w", pady=2)
        self.fecha_emision_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        ttk.Entry(pred_input_frame, textvariable=self.fecha_emision_var, width=20).grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)

        # Fecha de vencimiento
        ttk.Label(pred_input_frame, text="Fecha de Vencimiento:").grid(row=2, column=0, sticky="w", pady=2)
        self.fecha_vencimiento_var = tk.StringVar(value=(datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'))
        ttk.Entry(pred_input_frame, textvariable=self.fecha_vencimiento_var, width=20).grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=2)

        # Botón de predicción ensemble
        predict_ensemble_button = tk.Button(
            controls_frame,
            text="🎯 Predicción Ensemble",
            command=self.predict_with_ensemble,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        predict_ensemble_button.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        # Panel derecho - Resultados
        results_frame = ttk.LabelFrame(prediction_frame, text="Resultados", padding="8")
        results_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))

        # Resultado de predicción
        self.prediction_result = ttk.Label(results_frame, text="", font=("Arial", 11, "bold"))
        self.prediction_result.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Análisis de importancia de características
        self.feature_importance_text = tk.Text(results_frame, height=8, width=40, wrap=tk.WORD, font=("Consolas", 9))
        self.feature_importance_text.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        # Scrollbar para el texto
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.feature_importance_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(8, 0))
        self.feature_importance_text.configure(yscrollcommand=scrollbar.set)

    def create_recommendations_tab(self):
        """Crea la pestaña de recomendaciones"""
        recommendations_frame = ttk.Frame(self.notebook)
        self.notebook.add(recommendations_frame, text="💡 Recomendaciones")

        # Configurar grid
        recommendations_frame.columnconfigure(0, weight=1)
        recommendations_frame.rowconfigure(1, weight=1)

        # Botón para generar recomendaciones
        generate_button = tk.Button(
            recommendations_frame,
            text="🔍 Generar Recomendaciones Inteligentes",
            command=self.generate_recommendations,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        generate_button.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Lista de recomendaciones
        self.recommendations_text = tk.Text(recommendations_frame, height=15, width=80, wrap=tk.WORD, font=("Arial", 10))
        self.recommendations_text.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Scrollbar
        scrollbar = ttk.Scrollbar(recommendations_frame, orient="vertical", command=self.recommendations_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))
        self.recommendations_text.configure(yscrollcommand=scrollbar.set)

    def create_ocr_tab(self):
        """Crea la pestaña de OCR"""
        ocr_frame = ttk.Frame(self.notebook)
        self.notebook.add(ocr_frame, text="📷 OCR Avanzado")

        # Configurar grid
        ocr_frame.columnconfigure(0, weight=1)
        ocr_frame.rowconfigure(1, weight=1)

        # Botón para seleccionar imagen
        select_button = tk.Button(
            ocr_frame,
            text="📁 Seleccionar Foto de Boleta",
            command=self.select_invoice_image,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        select_button.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Información de OCR
        self.ocr_info = ttk.Label(
            ocr_frame,
            text="📸 Sube una foto clara de tu boleta para extraer datos automáticamente",
            font=("Arial", 9),
            justify="center"
        )
        self.ocr_info.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        # Resultado del OCR
        self.ocr_result = tk.Text(ocr_frame, height=12, width=70, wrap=tk.WORD, font=("Consolas", 9))
        self.ocr_result.grid(row=2, column=0, sticky="nsew", pady=(0, 8))

        # Botón para crear cuenta desde OCR
        self.create_from_ocr_btn = tk.Button(
            ocr_frame,
            text="➕ Crear Cuenta desde OCR",
            command=self.create_account_from_ocr,
            state="disabled",
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        self.create_from_ocr_btn.grid(row=3, column=0, sticky="ew")

    def create_analysis_tab(self):
        """Crea la pestaña de análisis avanzado"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📊 Análisis Avanzado")

        # Configurar grid
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(2, weight=1)

        # Frame para controles
        controls_frame = ttk.Frame(analysis_frame)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(controls_frame, text="Tipo de servicio:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.analysis_tipo_var = tk.StringVar()
        analysis_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.analysis_tipo_var,
            values=[t.value for t in TipoServicio],
            state="readonly",
            width=20
        )
        analysis_combo.grid(row=0, column=1, sticky="ew", padx=(5, 10))

        analyze_button = tk.Button(
            controls_frame,
            text="📊 Análisis Avanzado",
            command=self.analyze_advanced_trends,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=3,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        analyze_button.grid(row=0, column=2, padx=(10, 0))

        # Botón para pronóstico de ahorros
        forecast_button = tk.Button(
            analysis_frame,
            text="💰 Pronóstico de Ahorros",
            command=self.get_savings_forecast,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        forecast_button.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        # Resultado del análisis
        self.advanced_analysis_result = tk.Text(analysis_frame, height=12, width=80, wrap=tk.WORD, font=("Consolas", 9))
        self.advanced_analysis_result.grid(row=2, column=0, sticky="nsew", pady=(8, 0))

        # Scrollbar
        scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.advanced_analysis_result.yview)
        scrollbar.grid(row=2, column=1, sticky="ns", pady=(8, 0))
        self.advanced_analysis_result.configure(yscrollcommand=scrollbar.set)

    def create_insights_tab(self):
        """Crea la pestaña de insights y acciones prioritarias"""
        insights_frame = ttk.Frame(self.notebook)
        self.notebook.add(insights_frame, text="🎯 Insights")

        # Configurar grid
        insights_frame.columnconfigure(0, weight=1)
        insights_frame.rowconfigure(1, weight=1)

        # Botón para generar insights
        insights_button = tk.Button(
            insights_frame,
            text="🎯 Generar Insights y Acciones Prioritarias",
            command=self.generate_insights,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        insights_button.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Resultado de insights
        self.insights_result = tk.Text(insights_frame, height=15, width=80, wrap=tk.WORD, font=("Arial", 10))
        self.insights_result.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Scrollbar
        scrollbar = ttk.Scrollbar(insights_frame, orient="vertical", command=self.insights_result.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))
        self.insights_result.configure(yscrollcommand=scrollbar.set)

    def volver_al_principal(self):
        """Vuelve al panel principal"""
        if hasattr(self, 'parent') and hasattr(self.parent, 'destroy'):
            self.parent.destroy()

    def mostrar_ayuda_avanzada(self):
        """Muestra ayuda sobre las funcionalidades avanzadas de IA"""
        help_text = """
🚀 IA AVANZADA - AYUDA COMPLETA

🔮 PREDICCIONES AVANZADAS:
• Ensemble de múltiples algoritmos (Random Forest, Gradient Boosting, SVR, etc.)
• Análisis de importancia de características
• Predicciones con nivel de confianza
• Entrenamiento automático con validación cruzada

💡 RECOMENDACIONES INTELIGENTES:
• Detección automática de patrones de gasto
• Alertas de incrementos significativos
• Oportunidades de optimización
• Análisis de consistencia en pagos
• Recomendaciones priorizadas por impacto

📷 OCR AVANZADO:
• Extracción mejorada de datos de boletas
• Validación automática de datos extraídos
• Creación directa de cuentas desde imágenes
• Soporte para múltiples formatos

📊 ANÁLISIS AVANZADO:
• Análisis de tendencias con regresión polinomial
• Detección de estacionalidad
• Análisis de volatilidad
• Pronóstico de ahorros potenciales
• Estadísticas detalladas por mes

🎯 INSIGHTS Y ACCIONES:
• Análisis de patrones de consumo
• Acciones prioritarias basadas en datos
• Pronóstico de ahorros a 6 meses
• Recomendaciones personalizadas

💡 CONSEJOS:
• Cuantas más cuentas tengas, mejor serán las predicciones
• Las fotos de boletas deben ser claras y bien iluminadas
• Revisa siempre las recomendaciones de alta prioridad
• Usa el análisis avanzado para planificar gastos futuros
        """
        messagebox.showinfo("Ayuda - IA Avanzada", help_text)

    @handle_ui_errors("Error entrenando modelos avanzados", "AdvancedAIPanel.train_advanced_models")
    def train_advanced_models(self):
        """Entrena los modelos avanzados de predicción"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        if len(cuentas) < 10:
            error_handler.handle_validation_error("Se necesitan al menos 10 cuentas para entrenar los modelos avanzados")
            return

        # Mostrar progreso
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("Entrenando Modelos Avanzados")
        progress_window.geometry("400x200")
        progress_window.transient(self.parent)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Entrenando modelos avanzados...").pack(pady=20)
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()

        # Entrenar modelos avanzados
        results = advanced_prediction_service.train_advanced_models(cuentas)

        progress_window.destroy()

        # Mostrar resultados
        if results:
            message = "Modelos avanzados entrenados exitosamente:\n\n"
            for tipo, result in results.items():
                if isinstance(result, dict) and 'error' not in result:
                    message += f"• {tipo}: R²={result['best_r2']:.3f}, {result['models_trained']} modelos ({result['samples']} muestras)\n"
                else:
                    error_msg = result.get('error', 'Error desconocido') if isinstance(result, dict) else str(result)
                    message += f"• {tipo}: Error - {error_msg}\n"

            messagebox.showinfo("Entrenamiento Avanzado Completado", message)
        else:
            error_handler.handle_ui_error("No se pudieron entrenar los modelos avanzados")

    @handle_ui_errors("Error en predicción ensemble", "AdvancedAIPanel.predict_with_ensemble")
    def predict_with_ensemble(self):
        """Predice usando ensemble de modelos"""
        if not self.tipo_var.get():
            error_handler.handle_validation_error("Debe seleccionar un tipo de servicio")
            return

        try:
            # Parsear fechas
            fecha_emision = datetime.strptime(self.fecha_emision_var.get(), '%d/%m/%Y')
            fecha_vencimiento = datetime.strptime(self.fecha_vencimiento_var.get(), '%d/%m/%Y')
            tipo_servicio = TipoServicio(self.tipo_var.get())
        except ValueError:
            error_handler.handle_data_error("Formato de fecha inválido. Use DD/MM/YYYY")
            return

        # Realizar predicción ensemble
        result = advanced_prediction_service.predict_with_ensemble(tipo_servicio, fecha_emision, fecha_vencimiento)

        if result:
            # Mostrar predicción principal
            prediction_text = f"🎯 Predicción Ensemble: ${result['ensemble_prediction']:,.0f} CLP\n"
            prediction_text += f"🎯 Confianza: {result['confidence']:.1f}%\n"
            prediction_text += f"🤖 Modelos utilizados: {result['models_used']}\n\n"

            # Mostrar predicciones individuales
            prediction_text += "📊 Predicciones por modelo:\n"
            for model_name, pred in result['individual_predictions'].items():
                prediction_text += f"  • {model_name}: ${pred:,.0f}\n"

            self.prediction_result.config(text=prediction_text, foreground="green")

            # Mostrar análisis de importancia de características
            importance_analysis = advanced_prediction_service.get_feature_importance_analysis(tipo_servicio)
            if importance_analysis:
                importance_text = f"🔍 Análisis de Importancia de Características\n"
                importance_text += f"Mejor modelo: {importance_analysis['best_model']}\n\n"
                importance_text += "Top 5 características más importantes:\n"

                for i, feature in enumerate(importance_analysis['top_features'], 1):
                    importance_text += f"{i}. {feature['feature']}: {feature['importance']:.3f}\n"

                self.feature_importance_text.delete('1.0', tk.END)
                self.feature_importance_text.insert('1.0', importance_text)
        else:
            self.prediction_result.config(text="❌ No se pudo realizar la predicción ensemble", foreground="red")

    @handle_ui_errors("Error generando recomendaciones", "AdvancedAIPanel.generate_recommendations")
    def generate_recommendations(self):
        """Genera recomendaciones inteligentes"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        if len(cuentas) < 5:
            error_handler.handle_validation_error("Se necesitan al menos 5 cuentas para generar recomendaciones")
            return

        # Generar recomendaciones
        recomendaciones = recommendation_service.generate_recommendations(cuentas)

        if recomendaciones:
            # Formatear recomendaciones
            report = "💡 RECOMENDACIONES INTELIGENTES\n"
            report += "=" * 50 + "\n\n"

            for i, rec in enumerate(recomendaciones, 1):
                report += f"{i}. {rec.titulo}\n"
                report += f"   📝 {rec.descripcion}\n"
                report += f"   🎯 Impacto: {rec.impacto:.1f}% | Prioridad: {rec.prioridad.upper()}\n"
                report += f"   ✅ Acción: {rec.accion}\n"
                report += "-" * 40 + "\n\n"

            self.recommendations_text.delete('1.0', tk.END)
            self.recommendations_text.insert('1.0', report)
        else:
            self.recommendations_text.delete('1.0', tk.END)
            self.recommendations_text.insert('1.0', "✅ No se detectaron recomendaciones específicas. ¡Buen trabajo!")

    def select_invoice_image(self):
        """Selecciona una imagen de boleta"""
        filetypes = [
            ("Imágenes", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("Todos los archivos", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Seleccionar Boleta",
            filetypes=filetypes
        )

        if filename:
            self.process_invoice_image(filename)

    @handle_ui_errors("Error procesando imagen", "AdvancedAIPanel.process_invoice_image")
    def process_invoice_image(self, image_path: str):
        """Procesa la imagen de la boleta"""
        self.ocr_info.config(text="🔄 Procesando imagen...")
        self.ocr_result.delete('1.0', tk.END)

        # Extraer datos usando OCR
        data = ocr_service.extract_invoice_data(image_path)

        if data.get('success'):
            # Mostrar datos extraídos
            result_text = "📷 DATOS EXTRAÍDOS DE LA BOLETA\n"
            result_text += "=" * 40 + "\n\n"
            result_text += f"💰 Monto: ${data['monto']:,.0f} CLP\n" if data['monto'] else "💰 Monto: No detectado\n"
            result_text += f"📅 Fecha Emisión: {data['fecha_emision'].strftime('%d/%m/%Y')}\n" if data['fecha_emision'] else "📅 Fecha Emisión: No detectada\n"
            result_text += f"⏰ Fecha Vencimiento: {data['fecha_vencimiento'].strftime('%d/%m/%Y')}\n" if data['fecha_vencimiento'] else "⏰ Fecha Vencimiento: No detectada\n"
            result_text += f"🔧 Tipo Servicio: {data['tipo_servicio']}\n" if data['tipo_servicio'] else "🔧 Tipo Servicio: No detectado\n"
            result_text += f"📝 Descripción: {data['descripcion']}\n" if data['descripcion'] else "📝 Descripción: No detectada\n"
            result_text += f"🎯 Confianza: {data['confianza']:.1f}%\n\n"

            # Validar datos
            is_valid, errors = ocr_service.validate_extracted_data(data)
            if is_valid:
                result_text += "✅ Datos válidos - Se puede crear la cuenta\n"
                self.create_from_ocr_btn.config(state="normal")
                self.ocr_data = data
            else:
                result_text += "❌ Errores en los datos:\n"
                for error in errors:
                    result_text += f"   • {error}\n"
                self.create_from_ocr_btn.config(state="disabled")

            self.ocr_info.config(text="✅ Procesamiento completado")
        else:
            result_text = f"❌ Error: {data.get('error', 'Error desconocido')}"
            self.ocr_info.config(text="❌ Error en el procesamiento")
            self.create_from_ocr_btn.config(state="disabled")

        self.ocr_result.delete('1.0', tk.END)
        self.ocr_result.insert('1.0', result_text)

    @handle_ui_errors("Error creando cuenta desde OCR", "AdvancedAIPanel.create_account_from_ocr")
    def create_account_from_ocr(self):
        """Crea una cuenta desde los datos extraídos por OCR"""
        if not hasattr(self, 'ocr_data'):
            error_handler.handle_validation_error("No hay datos de OCR disponibles")
            return

        data = self.ocr_data

        # Crear cuenta usando el servicio de gestión
        cuenta = CuentaServicio(
            id=f"{data['tipo_servicio']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            tipo_servicio=TipoServicio(data['tipo_servicio']),
            fecha_emision=data['fecha_emision'],
            fecha_vencimiento=data['fecha_vencimiento'],
            monto=data['monto'],
            descripcion=data['descripcion']
        )

        self.gestionar_cuenta.crear_cuenta(cuenta)
        messagebox.showinfo("Éxito", "Cuenta creada exitosamente desde OCR")

        # Limpiar datos
        self.create_from_ocr_btn.config(state="disabled")
        self.ocr_result.delete('1.0', tk.END)
        self.ocr_info.config(text="📸 Sube una foto clara de tu boleta para extraer datos automáticamente")

    @handle_ui_errors("Error analizando tendencias avanzadas", "AdvancedAIPanel.analyze_advanced_trends")
    def analyze_advanced_trends(self):
        """Analiza las tendencias avanzadas"""
        if not self.analysis_tipo_var.get():
            error_handler.handle_validation_error("Debe seleccionar un tipo de servicio")
            return

        tipo_servicio = TipoServicio(self.analysis_tipo_var.get())
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        analysis = advanced_prediction_service.get_advanced_trend_analysis(cuentas, tipo_servicio)

        if 'error' in analysis:
            self.advanced_analysis_result.delete('1.0', tk.END)
            self.advanced_analysis_result.insert('1.0', f"Error: {analysis['error']}")
        else:
            # Formatear análisis avanzado
            report = f"📊 ANÁLISIS AVANZADO - {tipo_servicio.value}\n"
            report += "=" * 50 + "\n\n"
            report += f"📈 Total de cuentas: {analysis['total_cuentas']}\n"
            report += f"💰 Promedio actual: ${analysis['promedio_actual']:,.0f} CLP\n"
            report += f"📊 Mediana: ${analysis['mediana']:,.0f} CLP\n"
            report += f"📊 Tendencia lineal: {analysis['tendencia_lineal'].title()}\n"
            report += f"📊 Tendencia cuadrática: {analysis['tendencia_cuadratica'].title()}\n"
            report += f"📉 Cambio promedio mensual: ${analysis['cambio_promedio_mensual']:,.0f} CLP\n"
            report += f"📊 Volatilidad: {analysis['volatilidad']:.3f}\n"
            report += f"📅 Estacionalidad: {analysis['estacionalidad']}\n"
            report += f"💰 Predicción próximo mes: ${analysis['prediccion_proximo_mes']:,.0f} CLP\n"
            report += f"📅 Variación total: {analysis['variacion_total']:.1f}%\n\n"

            report += "📅 Estadísticas por mes:\n"
            for mes, stats in analysis['estadisticas_mensuales'].items():
                report += f"   Mes {mes}: Promedio=${stats['promedio']:,.0f}, Mediana=${stats['mediana']:,.0f}, Std=${stats['std']:,.0f} ({stats['count']} cuentas)\n"

            self.advanced_analysis_result.delete('1.0', tk.END)
            self.advanced_analysis_result.insert('1.0', report)

    @handle_ui_errors("Error obteniendo pronóstico de ahorros", "AdvancedAIPanel.get_savings_forecast")
    def get_savings_forecast(self):
        """Obtiene el pronóstico de ahorros"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        if len(cuentas) < 5:
            error_handler.handle_validation_error("Se necesitan al menos 5 cuentas para el pronóstico")
            return

        forecast = recommendation_service.get_savings_forecast(cuentas, meses=6)

        if 'error' in forecast:
            self.advanced_analysis_result.delete('1.0', tk.END)
            self.advanced_analysis_result.insert('1.0', f"Error: {forecast['error']}")
        else:
            # Formatear pronóstico
            report = "💰 PRONÓSTICO DE AHORROS (6 meses)\n"
            report += "=" * 50 + "\n\n"
            report += f"🎯 Total ahorro potencial: ${forecast['total_ahorro_potencial']:,.0f} CLP\n"
            report += f"📅 Período: {forecast['periodo_meses']} meses\n\n"

            if forecast['ahorros_proyectados']:
                report += "📊 Ahorros por servicio:\n"
                for tipo, data in forecast['ahorros_proyectados'].items():
                    report += f"   • {tipo}: ${data['ahorro_potencial']:,.0f} (impacto: {data['impacto']})\n"
            else:
                report += "✅ No se detectaron oportunidades de ahorro significativas\n"

            report += f"\n💡 Recomendación: {forecast['recomendacion']}"

            self.advanced_analysis_result.delete('1.0', tk.END)
            self.advanced_analysis_result.insert('1.0', report)

    @handle_ui_errors("Error generando insights", "AdvancedAIPanel.generate_insights")
    def generate_insights(self):
        """Genera insights y acciones prioritarias"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        if len(cuentas) < 5:
            error_handler.handle_validation_error("Se necesitan al menos 5 cuentas para generar insights")
            return

        # Obtener acciones prioritarias
        acciones = recommendation_service.get_priority_actions(cuentas)

        if acciones:
            # Formatear insights
            report = "🎯 INSIGHTS Y ACCIONES PRIORITARIAS\n"
            report += "=" * 50 + "\n\n"

            for i, accion in enumerate(acciones, 1):
                report += f"{i}. {accion['titulo']}\n"
                report += f"   📝 {accion['descripcion']}\n"
                report += f"   🎯 Impacto: {accion['impacto']:.1f}%\n"
                report += f"   ✅ Acción: {accion['accion']}\n"
                report += "-" * 40 + "\n\n"
        else:
            report = "✅ No se detectaron acciones prioritarias. ¡Excelente gestión de tus cuentas!"

        self.insights_result.delete('1.0', tk.END)
        self.insights_result.insert('1.0', report)

    def get_widget(self):
        """Retorna el widget principal del panel"""
        return self.main_frame