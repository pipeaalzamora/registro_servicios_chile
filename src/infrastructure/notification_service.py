"""
Servicio de notificaciones y recordatorios automáticos
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
from pathlib import Path

from ..domain.entities import CuentaServicio, TipoCambio


class NotificationService:
    """Servicio para manejar notificaciones y recordatorios"""

    def __init__(self, config_file: str = "config/notifications.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Carga la configuración de notificaciones"""
        default_config = {
            "email": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_email": ""
            },
            "notifications": {
                "vencimiento_dias_antes": 7,
                "riesgo_corte_dias_antes": 3,
                "vencimiento_hoy": True,
                "recordatorio_diario": False
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default_config
        else:
            # Crear directorio si no existe
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            # Guardar configuración por defecto
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config

    def save_config(self):
        """Guarda la configuración actual"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_recordatorios_diarios(self, cuentas: List[CuentaServicio]) -> Dict[str, List[CuentaServicio]]:
        """Obtiene los recordatorios diarios organizados por tipo"""
        recordatorios = {
            'vencen_hoy': [],
            'vencen_proximamente': [],
            'en_riesgo_corte': [],
            'vencidas': []
        }

        hoy = datetime.now()
        dias_vencimiento = self.config['notifications']['vencimiento_dias_antes']
        dias_riesgo = self.config['notifications']['riesgo_corte_dias_antes']

        for cuenta in cuentas:
            if cuenta.pagado:
                continue

            # Cuentas que vencen hoy
            if cuenta.fecha_vencimiento.date() == hoy.date():
                recordatorios['vencen_hoy'].append(cuenta)

            # Cuentas que vencen próximamente
            elif (cuenta.fecha_vencimiento.date() - hoy.date()).days <= dias_vencimiento:
                recordatorios['vencen_proximamente'].append(cuenta)

            # Cuentas en riesgo de corte
            elif cuenta.esta_en_riesgo_corte():
                recordatorios['en_riesgo_corte'].append(cuenta)

            # Cuentas vencidas
            elif cuenta.esta_vencida():
                recordatorios['vencidas'].append(cuenta)

        return recordatorios

    def generar_mensaje_recordatorio(self, recordatorios: Dict[str, List[CuentaServicio]]) -> str:
        """Genera el mensaje de recordatorio"""
        mensaje = "🔔 RECORDATORIOS DE SERVICIOS\n\n"

        if recordatorios['vencen_hoy']:
            mensaje += "🚨 CUENTAS QUE VENCEN HOY:\n"
            for cuenta in recordatorios['vencen_hoy']:
                mensaje += f"  • {cuenta.tipo_servicio.value}: ${cuenta.monto:,.0f} - {cuenta.descripcion}\n"
            mensaje += "\n"

        if recordatorios['vencen_proximamente']:
            mensaje += "📅 CUENTAS QUE VENCEN PRÓXIMAMENTE:\n"
            for cuenta in recordatorios['vencen_proximamente']:
                dias = (cuenta.fecha_vencimiento.date() - datetime.now().date()).days
                mensaje += f"  • {cuenta.tipo_servicio.value}: ${cuenta.monto:,.0f} - Vence en {dias} días\n"
            mensaje += "\n"

        if recordatorios['en_riesgo_corte']:
            mensaje += "⚠️ CUENTAS EN RIESGO DE CORTE:\n"
            for cuenta in recordatorios['en_riesgo_corte']:
                mensaje += f"  • {cuenta.tipo_servicio.value}: ${cuenta.monto:,.0f} - {cuenta.descripcion}\n"
            mensaje += "\n"

        if recordatorios['vencidas']:
            mensaje += "❌ CUENTAS VENCIDAS:\n"
            for cuenta in recordatorios['vencidas']:
                dias_vencida = (datetime.now().date() - cuenta.fecha_vencimiento.date()).days
                mensaje += f"  • {cuenta.tipo_servicio.value}: ${cuenta.monto:,.0f} - Vencida hace {dias_vencida} días\n"
            mensaje += "\n"

        if not any(recordatorios.values()):
            mensaje += "✅ No hay recordatorios pendientes. ¡Todo al día!\n"

        mensaje += f"\n---\nGenerado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}"
        return mensaje

    def enviar_email(self, asunto: str, mensaje: str) -> bool:
        """Envía un email con el recordatorio"""
        if not self.config['email']['enabled']:
            return False

        try:
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['from_email']
            msg['To'] = self.config['email']['to_email']
            msg['Subject'] = asunto

            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(mensaje, 'plain', 'utf-8'))

            # Crear conexión segura
            context = ssl.create_default_context()

            with smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port']) as server:
                server.starttls(context=context)
                server.login(self.config['email']['username'], self.config['email']['password'])

                # Enviar email
                text = msg.as_string()
                server.sendmail(self.config['email']['from_email'], self.config['email']['to_email'], text)

            return True

        except Exception as e:
            print(f"Error enviando email: {e}")
            return False

    def enviar_recordatorio_diario(self, cuentas: List[CuentaServicio]) -> bool:
        """Envía el recordatorio diario por email"""
        if not self.config['notifications']['recordatorio_diario']:
            return False

        recordatorios = self.get_recordatorios_diarios(cuentas)
        mensaje = self.generar_mensaje_recordatorio(recordatorios)

        asunto = f"Recordatorio Diario - {datetime.now().strftime('%d/%m/%Y')}"
        return self.enviar_email(asunto, mensaje)

    def configurar_email(self, enabled: bool, smtp_server: str, smtp_port: int,
                        username: str, password: str, from_email: str, to_email: str):
        """Configura los parámetros de email"""
        self.config['email']['enabled'] = enabled
        self.config['email']['smtp_server'] = smtp_server
        self.config['email']['smtp_port'] = smtp_port
        self.config['email']['username'] = username
        self.config['email']['password'] = password
        self.config['email']['from_email'] = from_email
        self.config['email']['to_email'] = to_email

        self.save_config()

    def configurar_notificaciones(self, vencimiento_dias: int, riesgo_dias: int,
                                 vencimiento_hoy: bool, recordatorio_diario: bool):
        """Configura los parámetros de notificaciones"""
        self.config['notifications']['vencimiento_dias_antes'] = vencimiento_dias
        self.config['notifications']['riesgo_corte_dias_antes'] = riesgo_dias
        self.config['notifications']['vencimiento_hoy'] = vencimiento_hoy
        self.config['notifications']['recordatorio_diario'] = recordatorio_diario

        self.save_config()

    def obtener_resumen_notificaciones(self, cuentas: List[CuentaServicio]) -> Dict:
        """Obtiene un resumen de las notificaciones pendientes"""
        recordatorios = self.get_recordatorios_diarios(cuentas)

        return {
            'total_recordatorios': sum(len(cuentas) for cuentas in recordatorios.values()),
            'vencen_hoy': len(recordatorios['vencen_hoy']),
            'vencen_proximamente': len(recordatorios['vencen_proximamente']),
            'en_riesgo_corte': len(recordatorios['en_riesgo_corte']),
            'vencidas': len(recordatorios['vencidas']),
            'email_configurado': self.config['email']['enabled'],
            'recordatorio_diario_activo': self.config['notifications']['recordatorio_diario']
        }