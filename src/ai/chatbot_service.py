"""
Servicio de Chatbot Inteligente para la aplicación
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from ..domain.entities import CuentaServicio, TipoServicio
from ..application.casos_uso import GestionarCuentaServicio


@dataclass
class ChatMessage:
    """Mensaje del chat"""
    text: str
    is_user: bool
    timestamp: datetime
    message_type: str = "text"  # text, suggestion, action


@dataclass
class ChatSuggestion:
    """Sugerencia del chatbot"""
    text: str
    action: str
    icon: str
    description: str


class ChatbotService:
    """Servicio de chatbot inteligente"""

    def __init__(self, gestionar_cuenta: GestionarCuentaServicio):
        self.gestionar_cuenta = gestionar_cuenta
        self.conversation_history: List[ChatMessage] = []
        self.user_context = {}

        # Patrones de reconocimiento
        self.patterns = {
            'saludo': r'\b(hola|buenos días|buenas tardes|buenas noches|hey|hi|hello)\b',
            'despedida': r'\b(adiós|chao|hasta luego|bye|goodbye|salir)\b',
            'ayuda': r'\b(ayuda|help|soporte|cómo|como|qué|que|duda|pregunta)\b',
            'nueva_cuenta': r'\b(nueva|crear|agregar|añadir|registrar)\s+(cuenta|servicio|boleta|factura)\b',
            'editar': r'\b(editar|modificar|cambiar|actualizar)\s+(cuenta|servicio)\b',
            'eliminar': r'\b(eliminar|borrar|quitar|remover)\s+(cuenta|servicio)\b',
            'buscar': r'\b(buscar|encontrar|filtrar)\b',
            'reporte': r'\b(reporte|pdf|generar|descargar)\b',
            'graficos': r'\b(gráfico|grafico|estadística|estadistica|visualizar|ver)\b',
            'ia': r'\b(ia|inteligencia|artificial|predicción|prediccion|ocr|reconocimiento)\b',
            'pago': r'\b(pagar|pagado|vencido|vencimiento|fecha)\b',
            'monto': r'\b(monto|precio|costo|valor|dinero)\b',
            'tipo_servicio': r'\b(luz|electricidad|agua|gas|internet|telefono|telefonía|seguridad|basura)\b'
        }

        # Respuestas predefinidas
        self.responses = {
            'saludo': [
                "¡Hola! 👋 Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?",
                "¡Buenos días! 🌅 ¿Necesitas ayuda con tus servicios?",
                "¡Hola! 😊 Estoy aquí para ayudarte a gestionar tus cuentas de servicios."
            ],
            'despedida': [
                "¡Hasta luego! 👋 ¡Que tengas un buen día!",
                "¡Adiós! 😊 ¡No dudes en volver si necesitas ayuda!",
                "¡Chao! 👋 ¡Recuerda revisar tus vencimientos!"
            ],
            'ayuda_general': [
                "Te puedo ayudar con:\n• Crear nuevas cuentas\n• Editar cuentas existentes\n• Generar reportes\n• Ver gráficos\n• Usar funciones de IA\n• Buscar cuentas\n\n¿Qué te gustaría hacer?",
                "Aquí tienes las funciones principales:\n📝 Crear cuenta nueva\n✏️ Editar cuenta\n📊 Ver gráficos\n🤖 Usar IA\n📄 Generar reportes\n\n¿Cuál te interesa?"
            ],
            'no_entendido': [
                "No estoy seguro de lo que necesitas. ¿Puedes ser más específico?",
                "No entendí bien. ¿Podrías reformular tu pregunta?",
                "No estoy seguro. ¿Te refieres a crear una cuenta, ver gráficos, o algo más?"
            ]
        }

        # Sugerencias contextuales
        self.suggestions = {
            'default': [
                ChatSuggestion("➕ Nueva Cuenta", "nueva_cuenta", "➕", "Crear una nueva cuenta de servicio"),
                ChatSuggestion("📊 Ver Gráficos", "graficos", "📊", "Visualizar estadísticas de gastos"),
                ChatSuggestion("🤖 Panel de IA", "ia", "🤖", "Acceder a funciones de inteligencia artificial"),
                ChatSuggestion("📄 Generar Reporte", "reporte", "📄", "Crear reporte PDF de cuentas")
            ],
            'after_nueva_cuenta': [
                ChatSuggestion("✏️ Editar Cuenta", "editar", "✏️", "Modificar una cuenta existente"),
                ChatSuggestion("🔍 Buscar Cuentas", "buscar", "🔍", "Encontrar cuentas específicas"),
                ChatSuggestion("📊 Ver Gráficos", "graficos", "📊", "Analizar gastos")
            ]
        }

    def process_message(self, user_message: str) -> Tuple[str, List[ChatSuggestion]]:
        """Procesa un mensaje del usuario y retorna respuesta y sugerencias"""
        # Agregar mensaje del usuario al historial
        self.conversation_history.append(ChatMessage(
            text=user_message,
            is_user=True,
            timestamp=datetime.now()
        ))

        # Analizar el mensaje
        intent = self._analyze_intent(user_message.lower())
        response = self._generate_response(intent, user_message)
        suggestions = self._get_suggestions(intent)

        # Agregar respuesta al historial
        self.conversation_history.append(ChatMessage(
            text=response,
            is_user=False,
            timestamp=datetime.now()
        ))

        return response, suggestions

    def _analyze_intent(self, message: str) -> str:
        """Analiza la intención del mensaje del usuario"""
        for intent, pattern in self.patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                return intent

        # Análisis más específico
        if any(word in message for word in ['crear', 'nueva', 'agregar']):
            return 'nueva_cuenta'
        elif any(word in message for word in ['editar', 'modificar', 'cambiar']):
            return 'editar'
        elif any(word in message for word in ['eliminar', 'borrar', 'quitar']):
            return 'eliminar'
        elif any(word in message for word in ['buscar', 'encontrar', 'filtrar']):
            return 'buscar'
        elif any(word in message for word in ['reporte', 'pdf', 'descargar']):
            return 'reporte'
        elif any(word in message for word in ['gráfico', 'grafico', 'estadística', 'estadistica']):
            return 'graficos'
        elif any(word in message for word in ['ia', 'inteligencia', 'predicción', 'ocr']):
            return 'ia'
        elif any(word in message for word in ['pagar', 'pagado', 'vencido']):
            return 'pago'
        elif any(word in message for word in ['monto', 'precio', 'costo']):
            return 'monto'

        return 'no_entendido'

    def _generate_response(self, intent: str, original_message: str) -> str:
        """Genera una respuesta basada en la intención"""
        if intent == 'saludo':
            return self._get_random_response('saludo')
        elif intent == 'despedida':
            return self._get_random_response('despedida')
        elif intent == 'ayuda':
            return self._get_random_response('ayuda_general')
        elif intent == 'nueva_cuenta':
            return self._get_nueva_cuenta_response()
        elif intent == 'editar':
            return self._get_editar_response()
        elif intent == 'eliminar':
            return self._get_eliminar_response()
        elif intent == 'buscar':
            return self._get_buscar_response()
        elif intent == 'reporte':
            return self._get_reporte_response()
        elif intent == 'graficos':
            return self._get_graficos_response()
        elif intent == 'ia':
            return self._get_ia_response()
        elif intent == 'pago':
            return self._get_pago_response()
        elif intent == 'monto':
            return self._get_monto_response()
        else:
            return self._get_random_response('no_entendido')

    def _get_random_response(self, category: str) -> str:
        """Obtiene una respuesta aleatoria de una categoría"""
        import random
        responses = self.responses.get(category, self.responses['no_entendido'])
        return random.choice(responses)

    def _get_nueva_cuenta_response(self) -> str:
        """Genera respuesta para crear nueva cuenta"""
        return ("📝 Para crear una nueva cuenta:\n\n"
                "1. Haz clic en el botón '➕ Nuevo Registro'\n"
                "2. Completa los campos requeridos\n"
                "3. Haz clic en 'Guardar'\n\n"
                "¿Te gustaría que te ayude con algún campo específico?")

    def _get_editar_response(self) -> str:
        """Genera respuesta para editar cuenta"""
        return ("✏️ Para editar una cuenta:\n\n"
                "1. Selecciona la cuenta en la tabla\n"
                "2. Haz clic en '✏️ Editar Cuenta'\n"
                "3. Modifica los campos necesarios\n"
                "4. Haz clic en 'Guardar'\n\n"
                "¿Necesitas ayuda con algún campo específico?")

    def _get_eliminar_response(self) -> str:
        """Genera respuesta para eliminar cuenta"""
        return ("🗑️ Para eliminar cuentas:\n\n"
                "• Eliminar una: Selecciona y haz clic en '🗑️ Eliminar'\n"
                "• Eliminar múltiples: Selecciona varias y haz clic en '🗑️ Eliminar Seleccionadas'\n\n"
                "⚠️ Esta acción no se puede deshacer.")

    def _get_buscar_response(self) -> str:
        """Genera respuesta para buscar cuentas"""
        return ("🔍 Para buscar cuentas:\n\n"
                "1. Usa el campo de búsqueda en la tabla\n"
                "2. Puedes buscar por:\n"
                "   • Tipo de servicio\n"
                "   • Descripción\n"
                "   • Monto\n"
                "   • Fechas\n\n"
                "¿Qué tipo de cuenta estás buscando?")

    def _get_reporte_response(self) -> str:
        """Genera respuesta para generar reportes"""
        return ("📄 Para generar reportes:\n\n"
                "• Reporte General: Haz clic en '📄 Generar Reporte'\n"
                "• Resumen Mensual: Usa el botón '📅 Resumen Mensual'\n"
                "• Reporte Anual: Usa el botón '📊 Reporte Anual'\n\n"
                "Los reportes se guardan en la carpeta 'reports/'")

    def _get_graficos_response(self) -> str:
        """Genera respuesta para gráficos"""
        return ("📊 Para ver gráficos:\n\n"
                "1. Haz clic en '📊 Gráficos'\n"
                "2. Selecciona el tipo de gráfico:\n"
                "   • Gastos por Servicio\n"
                "   • Gastos por Mes\n"
                "   • Evolución Anual\n\n"
                "¿Qué tipo de análisis te interesa?")

    def _get_ia_response(self) -> str:
        """Genera respuesta para funciones de IA"""
        return ("🤖 Funciones de IA disponibles:\n\n"
                "• 🔮 Predicciones: Predice montos futuros\n"
                "• 📷 OCR: Extrae datos de fotos de boletas\n"
                "• 📈 Análisis: Analiza tendencias de gastos\n"
                "• 💡 Recomendaciones: Sugiere optimizaciones\n\n"
                "Haz clic en '🤖 IA' para acceder.")

    def _get_pago_response(self) -> str:
        """Genera respuesta sobre pagos"""
        cuentas_vencidas = self._get_cuentas_vencidas()
        if cuentas_vencidas:
            return (f"⚠️ Tienes {len(cuentas_vencidas)} cuenta(s) vencida(s):\n\n" +
                    "\n".join([f"• {c.descripcion} - Vence: {c.fecha_vencimiento.strftime('%d/%m/%Y')}"
                              for c in cuentas_vencidas[:3]]) +
                    "\n\nTe recomiendo revisarlas pronto.")
        else:
            return ("✅ No tienes cuentas vencidas.\n\n"
                    "Para marcar una cuenta como pagada:\n"
                    "1. Selecciona la cuenta\n"
                    "2. Haz clic en '✅ Marcar como Pagada'")

    def _get_monto_response(self) -> str:
        """Genera respuesta sobre montos"""
        total_gastos = self._get_total_gastos()
        return (f"💰 Resumen de gastos:\n\n"
                f"• Total este mes: ${total_gastos['mes']:,} CLP\n"
                f"• Total este año: ${total_gastos['año']:,} CLP\n"
                f"• Promedio mensual: ${total_gastos['promedio']:,} CLP\n\n"
                "Para ver más detalles, revisa los gráficos.")

    def _get_suggestions(self, intent: str) -> List[ChatSuggestion]:
        """Obtiene sugerencias contextuales"""
        if intent == 'nueva_cuenta':
            return self.suggestions['after_nueva_cuenta']
        else:
            return self.suggestions['default']

    def _get_cuentas_vencidas(self) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        try:
            todas_cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
            hoy = datetime.now().date()
            return [c for c in todas_cuentas if not c.pagado and c.fecha_vencimiento.date() < hoy]
        except:
            return []

    def _get_total_gastos(self) -> Dict[str, int]:
        """Calcula totales de gastos"""
        try:
            todas_cuentas = self.gestionar_cuenta.obtener_todas_las_cuentas()
            hoy = datetime.now()

            # Gastos del mes actual
            mes_actual = list(filter(
                lambda c: c.fecha_emision.month == hoy.month and
                         c.fecha_emision.year == hoy.year,
                todas_cuentas
            ))
            total_mes = sum(c.monto for c in mes_actual)

            # Gastos del año actual
            año_actual = list(filter(
                lambda c: c.fecha_emision.year == hoy.year,
                todas_cuentas
            ))
            total_año = sum(c.monto for c in año_actual)

            # Promedio mensual (últimos 12 meses)
            promedio = total_año / 12 if total_año > 0 else 0

            return {
                'mes': int(total_mes),
                'año': int(total_año),
                'promedio': int(promedio)
            }
        except:
            return {'mes': 0, 'año': 0, 'promedio': 0}

    def get_conversation_history(self) -> List[ChatMessage]:
        """Obtiene el historial de conversación"""
        return self.conversation_history.copy()

    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history.clear()
        self.user_context.clear()