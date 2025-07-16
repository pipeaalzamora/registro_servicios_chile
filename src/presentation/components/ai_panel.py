"""
Panel de Inteligencia Artificial para la aplicación
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from typing import Optional
import os

from ...domain.entities import TipoServicio
from ...ai import prediction_service, ocr_service
from ..utils import error_handler, handle_ui_errors


class AIPanel:
    """Panel para funcionalidades de Inteligencia Artificial"""

    def __init__(self, parent, gestionar_cuenta):
        self.parent = parent
        self.gestionar_cuenta = gestionar_cuenta

        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz del panel"""
        # Frame principal
        self.main_frame = ttk.LabelFrame(self.parent, text="🤖 Inteligencia Artificial", padding="10")

        # Configurar grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # Barra de navegación superior
        self.create_navigation_bar()

        # Sección de predicciones
        self.create_prediction_section()

        # Sección de OCR
        self.create_ocr_section()

        # Sección de análisis
        self.create_analysis_section()

    def create_navigation_bar(self):
        """Crea la barra de navegación"""
        nav_frame = ttk.Frame(self.main_frame)
        nav_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
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
            text="🤖 Panel de Inteligencia Artificial",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=1)

        # Botón de ayuda
        help_button = tk.Button(
            nav_frame,
            text="❓ Ayuda IA",
            command=self.mostrar_ayuda_ia,
            relief="flat",
            borderwidth=1,
            padx=8,
            pady=5,
            cursor="hand2"
        )
        help_button.grid(row=0, column=2, sticky="e")

    def volver_al_principal(self):
        """Vuelve al panel principal"""
        if hasattr(self, 'parent') and hasattr(self.parent, 'destroy'):
            # Cerrar solo la ventana del panel de IA
            self.parent.destroy()

    def mostrar_ayuda_ia(self):
        """Muestra ayuda sobre las funcionalidades de IA"""
        help_text = """
🤖 INTELIGENCIA ARTIFICIAL - AYUDA

📊 PREDICCIONES:
• Entrena modelos con al menos 10 cuentas
• Predice montos futuros basado en historial
• Muestra nivel de confianza de predicciones

📷 OCR (Reconocimiento de Texto):
• Sube fotos de boletas para extraer datos
• Detecta automáticamente tipo, monto y fechas
• Crea cuentas directamente desde imágenes

📈 ANÁLISIS DE TENDENCIAS:
• Analiza patrones de precios por servicio
• Detecta tendencias estacionales
• Muestra estadísticas detalladas

💡 CONSEJOS:
• Cuantas más cuentas tengas, mejor serán las predicciones
• Las fotos de boletas deben ser claras y bien iluminadas
• Revisa siempre los datos extraídos por OCR
        """
        messagebox.showinfo("Ayuda - Inteligencia Artificial", help_text)

    def create_prediction_section(self):
        """Crea la sección de predicciones"""
        prediction_frame = ttk.LabelFrame(self.main_frame, text="📊 Predicciones", padding="8")
        prediction_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))

        # Botón para entrenar modelos
        train_button = tk.Button(
            prediction_frame,
            text="🔄 Entrenar Modelos de IA",
            command=self.train_models,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        train_button.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Frame para predicción
        pred_input_frame = ttk.Frame(prediction_frame)
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

        # Botón de predicción
        predict_button = tk.Button(
            prediction_frame,
            text="🔮 Predecir Monto",
            command=self.predict_amount,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=5,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        predict_button.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        # Resultado de predicción
        self.prediction_result = ttk.Label(prediction_frame, text="", font=("Arial", 11, "bold"))
        self.prediction_result.grid(row=3, column=0, sticky="ew", pady=(8, 0))

    def create_ocr_section(self):
        """Crea la sección de OCR"""
        ocr_frame = ttk.LabelFrame(self.main_frame, text="📷 Reconocimiento de Texto (OCR)", padding="8")
        ocr_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))

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
            text="📸 Sube una foto clara de tu boleta\npara extraer datos automáticamente",
            font=("Arial", 9),
            justify="center"
        )
        self.ocr_info.grid(row=1, column=0, sticky="ew", pady=(0, 8))

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
        self.create_from_ocr_btn.grid(row=2, column=0, sticky="ew")

    def create_analysis_section(self):
        """Crea la sección de análisis"""
        analysis_frame = ttk.LabelFrame(self.main_frame, text="📈 Análisis de Tendencias", padding="8")
        analysis_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

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
            text="📊 Analizar Tendencia",
            command=self.analyze_trends,
            relief="flat",
            borderwidth=1,
            padx=10,
            pady=3,
            cursor="hand2",
            font=("Arial", 10, "bold")
        )
        analyze_button.grid(row=0, column=2, padx=(10, 0))

        # Resultado del análisis
        self.analysis_result = tk.Text(analysis_frame, height=8, width=70, wrap=tk.WORD, font=("Consolas", 9))
        self.analysis_result.grid(row=1, column=0, sticky="nsew", pady=(8, 0))

        # Scrollbar para el texto
        scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=self.analysis_result.yview)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(8, 0))
        self.analysis_result.configure(yscrollcommand=scrollbar.set)

    @handle_ui_errors("Error entrenando modelos", "AIPanel.train_models")
    def train_models(self):
        """Entrena los modelos de predicción"""
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        if len(cuentas) < 10:
            error_handler.handle_validation_error("Se necesitan al menos 10 cuentas para entrenar los modelos")
            return

        # Mostrar progreso
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("Entrenando Modelos")
        progress_window.geometry("300x150")
        progress_window.transient(self.parent)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Entrenando modelos de predicción...").pack(pady=20)
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()

        # Entrenar modelos
        results = prediction_service.train_models(cuentas)

        progress_window.destroy()

        # Mostrar resultados
        if results:
            message = "Modelos entrenados exitosamente:\n\n"
            for tipo, result in results.items():
                if isinstance(result, dict) and 'error' not in result:
                    message += f"• {tipo}: Precisión {result['accuracy']:.1f}% ({result['samples']} muestras)\n"
                else:
                    error_msg = result.get('error', 'Error desconocido') if isinstance(result, dict) else str(result)
                    message += f"• {tipo}: Error - {error_msg}\n"

            messagebox.showinfo("Entrenamiento Completado", message)
        else:
            error_handler.handle_ui_error("No se pudieron entrenar los modelos")

    @handle_ui_errors("Error en predicción", "AIPanel.predict_amount")
    def predict_amount(self):
        """Predice el monto para los datos ingresados"""
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

        # Realizar predicción
        prediction = prediction_service.predict_amount(tipo_servicio, fecha_emision, fecha_vencimiento)
        confidence = prediction_service.get_prediction_confidence(tipo_servicio, fecha_emision, fecha_vencimiento)

        if prediction:
            result_text = f"💰 Monto Predicho: ${prediction:,.0f} CLP"
            if confidence:
                result_text += f"\n🎯 Confianza: {confidence:.1f}%"

            self.prediction_result.config(text=result_text, foreground="green")
        else:
            self.prediction_result.config(text="❌ No se pudo realizar la predicción", foreground="red")

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

    @handle_ui_errors("Error procesando imagen", "AIPanel.process_invoice_image")
    def process_invoice_image(self, image_path: str):
        """Procesa la imagen de la boleta"""
        if not ocr_service.ocr_available:
            error_handler.handle_ui_error("OCR no disponible. Instala las dependencias de IA")
            return

        # Mostrar progreso
        self.ocr_info.config(text="Procesando imagen...")
        self.parent.update()

        # Extraer datos
        result = ocr_service.extract_invoice_data(image_path)

        if result.get('success'):
            # Validar datos
            is_valid, errors = ocr_service.validate_extracted_data(result)

            if is_valid:
                # Guardar datos extraídos
                self.extracted_data = result

                # Mostrar información
                info_text = f"✅ Datos extraídos (Confianza: {result['confianza']:.1f}%)\n"
                info_text += f"Monto: ${result['monto']:,.0f}\n"
                info_text += f"Tipo: {result['tipo_servicio']}"

                self.ocr_info.config(text=info_text)
                self.create_from_ocr_btn.config(state="normal")
            else:
                error_text = "⚠️ Datos extraídos con errores:\n" + "\n".join(errors)
                self.ocr_info.config(text=error_text)
                self.create_from_ocr_btn.config(state="disabled")
        else:
            self.ocr_info.config(text=f"❌ Error: {result.get('error', 'Error desconocido')}")
            self.create_from_ocr_btn.config(state="disabled")

    @handle_ui_errors("Error creando cuenta desde OCR", "AIPanel.create_account_from_ocr")
    def create_account_from_ocr(self):
        """Crea una cuenta usando los datos extraídos por OCR"""
        if not hasattr(self, 'extracted_data'):
            return

        data = self.extracted_data

        # Crear cuenta
        cuenta = self.gestionar_cuenta.crear_cuenta(
            tipo_servicio=TipoServicio(data['tipo_servicio']),
            fecha_emision=data['fecha_emision'],
            fecha_vencimiento=data['fecha_vencimiento'],
            monto=data['monto'],
            descripcion=data['descripcion']
        )

        if cuenta:
            messagebox.showinfo("Éxito", "Cuenta creada exitosamente desde la imagen")
            self.ocr_info.config(text="✅ Cuenta creada exitosamente")
            self.create_from_ocr_btn.config(state="disabled")
        else:
            error_handler.handle_ui_error("No se pudo crear la cuenta")

    @handle_ui_errors("Error analizando tendencias", "AIPanel.analyze_trends")
    def analyze_trends(self):
        """Analiza las tendencias de precios"""
        if not self.analysis_tipo_var.get():
            error_handler.handle_validation_error("Debe seleccionar un tipo de servicio")
            return

        tipo_servicio = TipoServicio(self.analysis_tipo_var.get())
        cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()

        analysis = prediction_service.get_trend_analysis(cuentas, tipo_servicio)

        if 'error' in analysis:
            self.analysis_result.delete('1.0', tk.END)
            self.analysis_result.insert('1.0', f"Error: {analysis['error']}")
        else:
            # Formatear análisis
            report = f"📊 Análisis de Tendencias - {tipo_servicio.value}\n"
            report += "=" * 50 + "\n\n"
            report += f"📈 Total de cuentas: {analysis['total_cuentas']}\n"
            report += f"💰 Promedio actual: ${analysis['promedio_actual']:,.0f} CLP\n"
            report += f"📊 Tendencia: {analysis['tendencia'].title()}\n"
            report += f"📉 Cambio promedio mensual: ${analysis['cambio_promedio_mensual']:,.0f} CLP\n"
            report += f"📅 Variación total: {analysis['variacion_total']:.1f}%\n\n"

            report += "📅 Promedio por mes:\n"
            for mes, promedio in analysis['promedio_por_mes'].items():
                report += f"   Mes {mes}: ${promedio:,.0f} CLP\n"

            self.analysis_result.delete('1.0', tk.END)
            self.analysis_result.insert('1.0', report)

    def get_widget(self):
        """Retorna el widget principal del panel"""
        return self.main_frame