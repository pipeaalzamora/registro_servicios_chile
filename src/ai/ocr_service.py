"""
Servicio de OCR para extraer datos de boletas de servicios
"""

import re
from datetime import datetime
from typing import Dict, Optional, Tuple, List
from pathlib import Path
import logging

# Importaciones opcionales para evitar errores si no están instaladas
try:
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR no disponible. Instala: pip install -r requirements_ai.txt")

from ..domain.entities import TipoServicio

logger = logging.getLogger(__name__)


class OCRService:
    """Servicio para extraer datos de boletas usando OCR"""

    def __init__(self):
        self.ocr_available = OCR_AVAILABLE

        # Patrones de regex para extraer información
        self.patterns = {
            'monto': [
                r'\$\s*([0-9,]+(?:\.[0-9]{2})?)',
                r'CLP\s*([0-9,]+(?:\.[0-9]{2})?)',
                r'PESOS\s*([0-9,]+(?:\.[0-9]{2})?)',
                r'TOTAL\s*[:\s]*\$?\s*([0-9,]+(?:\.[0-9]{2})?)',
                r'MONTO\s*[:\s]*\$?\s*([0-9,]+(?:\.[0-9]{2})?)',
            ],
            'fecha_emision': [
                r'FECHA\s*[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'EMISION\s*[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'fecha_vencimiento': [
                r'VENCIMIENTO\s*[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'VENCE\s*[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'PAGAR\s*HASTA\s*[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'tipo_servicio': [
                r'(AGUA|WATER)',
                r'(LUZ|ELECTRICIDAD|ELECTRICITY)',
                r'(GAS)',
                r'(INTERNET|WIFI)',
                r'(GASTOS\s*COMUNES|COMUNES)',
            ]
        }

    def preprocess_image(self, image_path: str) -> Optional[str]:
        """Preprocesa la imagen para mejorar el OCR"""
        if not self.ocr_available:
            return None

        try:
            # Cargar imagen
            image = cv2.imread(image_path)
            if image is None:
                return None

            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Aplicar filtros para mejorar el texto
            # Reducción de ruido
            denoised = cv2.medianBlur(gray, 3)

            # Aumentar contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)

            # Binarización adaptativa
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )

            # Guardar imagen procesada temporalmente
            temp_path = Path(image_path).parent / f"temp_{Path(image_path).name}"
            cv2.imwrite(str(temp_path), binary)

            return str(temp_path)

        except Exception as e:
            logger.error(f"Error preprocesando imagen: {e}")
            return None

    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Extrae texto de una imagen usando OCR"""
        if not self.ocr_available:
            return None

        try:
            # Preprocesar imagen
            processed_path = self.preprocess_image(image_path)
            if not processed_path:
                return None

            # Configurar OCR
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$.,/\-:() '

            # Extraer texto
            text = pytesseract.image_to_string(
                Image.open(processed_path),
                config=custom_config,
                lang='spa+eng'
            )

            # Limpiar archivo temporal
            try:
                Path(processed_path).unlink()
            except:
                pass

            return text

        except Exception as e:
            logger.error(f"Error en OCR: {e}")
            return None

    def parse_amount(self, text: str) -> Optional[float]:
        """Extrae el monto de un texto"""
        for pattern in self.patterns['monto']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Limpiar el monto (remover comas y convertir a float)
                    amount_str = matches[-1].replace(',', '')
                    return float(amount_str)
                except ValueError:
                    continue
        return None

    def parse_date(self, text: str, date_type: str) -> Optional[datetime]:
        """Extrae fecha de un texto"""
        patterns = self.patterns.get(date_type, [])

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    date_str = matches[-1]
                    # Intentar diferentes formatos de fecha
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue
        return None

    def detect_service_type(self, text: str) -> Optional[TipoServicio]:
        """Detecta el tipo de servicio basado en el texto"""
        text_upper = text.upper()

        # Mapeo de palabras clave a tipos de servicio
        service_keywords = {
            TipoServicio.AGUA: ['AGUA', 'WATER', 'SANITARIAS', 'ALCANTARILLADO'],
            TipoServicio.LUZ: ['LUZ', 'ELECTRICIDAD', 'ELECTRICITY', 'ENERGIA', 'ENERGY'],
            TipoServicio.GAS: ['GAS', 'GAS NATURAL', 'GAS LICUADO'],
            TipoServicio.INTERNET: ['INTERNET', 'WIFI', 'BANDA ANCHA', 'CONEXION'],
            TipoServicio.GASTOS_COMUNES: ['GASTOS COMUNES', 'COMUNES', 'ADMINISTRACION']
        }

        for service_type, keywords in service_keywords.items():
            for keyword in keywords:
                if keyword in text_upper:
                    return service_type

        return None

    def extract_invoice_data(self, image_path: str) -> Dict[str, any]:
        """Extrae todos los datos relevantes de una boleta"""
        if not self.ocr_available:
            return {'error': 'OCR no disponible'}

        try:
            # Extraer texto
            text = self.extract_text_from_image(image_path)
            if not text:
                return {'error': 'No se pudo extraer texto de la imagen'}

            # Extraer datos
            monto = self.parse_amount(text)
            fecha_emision = self.parse_date(text, 'fecha_emision')
            fecha_vencimiento = self.parse_date(text, 'fecha_vencimiento')
            tipo_servicio = self.detect_service_type(text)

            # Extraer descripción (primeras líneas del texto)
            lines = text.strip().split('\n')
            descripcion = lines[0] if lines else ""

            return {
                'success': True,
                'monto': monto,
                'fecha_emision': fecha_emision,
                'fecha_vencimiento': fecha_vencimiento,
                'tipo_servicio': tipo_servicio.value if tipo_servicio else None,
                'descripcion': descripcion[:100],  # Limitar longitud
                'texto_extraido': text[:500],  # Primeros 500 caracteres para debug
                'confianza': self.calculate_confidence(text, monto, fecha_emision, fecha_vencimiento, tipo_servicio)
            }

        except Exception as e:
            logger.error(f"Error extrayendo datos: {e}")
            return {'error': f'Error procesando imagen: {str(e)}'}

    def calculate_confidence(self, text: str, monto: Optional[float],
                           fecha_emision: Optional[datetime],
                           fecha_vencimiento: Optional[datetime],
                           tipo_servicio: Optional[TipoServicio]) -> float:
        """Calcula el nivel de confianza de la extracción"""
        confidence = 0.0
        total_checks = 4

        # Verificar monto
        if monto and monto > 0:
            confidence += 1.0

        # Verificar fecha de emisión
        if fecha_emision:
            confidence += 1.0

        # Verificar fecha de vencimiento
        if fecha_vencimiento:
            confidence += 1.0

        # Verificar tipo de servicio
        if tipo_servicio:
            confidence += 1.0

        return (confidence / total_checks) * 100

    def validate_extracted_data(self, data: Dict[str, any]) -> Tuple[bool, List[str]]:
        """Valida los datos extraídos"""
        errors = []

        if not data.get('monto'):
            errors.append("No se pudo extraer el monto")

        if not data.get('fecha_emision'):
            errors.append("No se pudo extraer la fecha de emisión")

        if not data.get('fecha_vencimiento'):
            errors.append("No se pudo extraer la fecha de vencimiento")

        if not data.get('tipo_servicio'):
            errors.append("No se pudo identificar el tipo de servicio")

        # Validar fechas
        if data.get('fecha_emision') and data.get('fecha_vencimiento'):
            if data['fecha_emision'] >= data['fecha_vencimiento']:
                errors.append("La fecha de vencimiento debe ser posterior a la fecha de emisión")

        return len(errors) == 0, errors

    def get_supported_formats(self) -> List[str]:
        """Retorna los formatos de imagen soportados"""
        return ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']


# Instancia global del servicio OCR
ocr_service = OCRService()