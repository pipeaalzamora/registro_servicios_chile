import json
import os
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ..domain.entities import CuentaServicio, ResumenMensual, TipoServicio, HistorialCambio, TipoCambio
from ..domain.repositories import CuentaServicioRepository, ResumenRepository
from .security import security_manager

class JSONCuentaServicioRepository(CuentaServicioRepository):
    """Implementación del repositorio usando JSON para almacenamiento local"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cuentas_file = self.data_dir / "cuentas.json"
        self._cargar_cuentas()

    def _cargar_cuentas(self):
        """Carga las cuentas desde el archivo JSON con validaciones de seguridad"""
        if self.cuentas_file.exists():
            # Validar archivo antes de cargar
            if not security_manager.validar_archivo_json(str(self.cuentas_file)):
                security_manager.generar_log_seguridad(
                    "ARCHIVO_INVALIDO",
                    f"Archivo {self.cuentas_file} no es válido o seguro",
                    "ERROR"
                )
                self.cuentas = {}
                return

            try:
                with open(self.cuentas_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cuentas = {}
                    for cuenta_data in data.values():
                        # Sanitizar datos antes de procesar
                        cuenta_data_sanitizada = security_manager.sanitizar_datos_json(cuenta_data)
                        cuenta = self._deserializar_cuenta(cuenta_data_sanitizada)
                        self.cuentas[cuenta.id] = cuenta

                security_manager.generar_log_seguridad(
                    "CARGA_EXITOSA",
                    f"Cargadas {len(self.cuentas)} cuentas desde {self.cuentas_file}"
                )
            except Exception as e:
                security_manager.generar_log_seguridad(
                    "ERROR_CARGA",
                    f"Error al cargar cuentas: {str(e)}",
                    "ERROR"
                )
                self.cuentas = {}
        else:
            self.cuentas = {}

    def _guardar_cuentas(self):
        """Guarda las cuentas en el archivo JSON con validaciones de seguridad"""
        try:
            # Crear backup antes de guardar
            if self.cuentas_file.exists():
                backup_path = security_manager.crear_backup_seguro(str(self.cuentas_file))
                if backup_path:
                    security_manager.generar_log_seguridad(
                        "BACKUP_CREADO",
                        f"Backup creado: {backup_path}"
                    )

            data = {}
            for cuenta in self.cuentas.values():
                # Sanitizar datos antes de guardar
                cuenta_data = self._serializar_cuenta(cuenta)
                data[cuenta.id] = security_manager.sanitizar_datos_json(cuenta_data)

            with open(self.cuentas_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

            security_manager.generar_log_seguridad(
                "GUARDADO_EXITOSO",
                f"Guardadas {len(self.cuentas)} cuentas en {self.cuentas_file}"
            )

            # Limpiar backups antiguos
            eliminados = security_manager.limpiar_backups_antiguos()
            if eliminados > 0:
                security_manager.generar_log_seguridad(
                    "BACKUPS_LIMPIADOS",
                    f"Eliminados {eliminados} backups antiguos"
                )

        except Exception as e:
            security_manager.generar_log_seguridad(
                "ERROR_GUARDADO",
                f"Error al guardar cuentas: {str(e)}",
                "ERROR"
            )
            raise

    def _serializar_cuenta(self, cuenta: CuentaServicio) -> dict:
        """Serializa una cuenta a diccionario"""
        return {
            'id': cuenta.id,
            'tipo_servicio': cuenta.tipo_servicio.value,
            'fecha_emision': cuenta.fecha_emision.isoformat(),
            'fecha_vencimiento': cuenta.fecha_vencimiento.isoformat(),
            'monto': cuenta.monto,
            'descripcion': cuenta.descripcion,
            'pagado': cuenta.pagado,
            'fecha_pago': cuenta.fecha_pago.isoformat() if cuenta.fecha_pago else None,
            'observaciones': cuenta.observaciones,
            'fecha_proxima_lectura': cuenta.fecha_proxima_lectura.isoformat() if cuenta.fecha_proxima_lectura else None,
            'fecha_corte': cuenta.fecha_corte.isoformat() if cuenta.fecha_corte else None,
            'historial': [self._serializar_historial(h) for h in (cuenta.historial or [])]
        }

    def _serializar_historial(self, historial: HistorialCambio) -> dict:
        """Serializa un cambio de historial a diccionario"""
        return {
            'id': historial.id,
            'cuenta_id': historial.cuenta_id,
            'tipo_cambio': historial.tipo_cambio.value,
            'fecha_cambio': historial.fecha_cambio.isoformat(),
            'descripcion': historial.descripcion,
            'datos_anteriores': historial.datos_anteriores,
            'datos_nuevos': historial.datos_nuevos
        }

    def _deserializar_cuenta(self, data: dict) -> CuentaServicio:
        """Deserializa un diccionario a cuenta"""
        cuenta = CuentaServicio(
            id=data['id'],
            tipo_servicio=TipoServicio(data['tipo_servicio']),
            fecha_emision=datetime.fromisoformat(data['fecha_emision']),
            fecha_vencimiento=datetime.fromisoformat(data['fecha_vencimiento']),
            monto=data['monto'],
            descripcion=data['descripcion'],
            pagado=data['pagado'],
            observaciones=data['observaciones']
        )

        # Cargar fechas opcionales
        if data.get('fecha_pago'):
            cuenta.fecha_pago = datetime.fromisoformat(data['fecha_pago'])
        if data.get('fecha_proxima_lectura'):
            cuenta.fecha_proxima_lectura = datetime.fromisoformat(data['fecha_proxima_lectura'])
        if data.get('fecha_corte'):
            cuenta.fecha_corte = datetime.fromisoformat(data['fecha_corte'])

        # Cargar historial
        if data.get('historial'):
            cuenta.historial = [self._deserializar_historial(h) for h in data['historial']]

        return cuenta

    def _deserializar_historial(self, data: dict) -> HistorialCambio:
        """Deserializa un diccionario a cambio de historial"""
        return HistorialCambio(
            id=data['id'],
            cuenta_id=data['cuenta_id'],
            tipo_cambio=TipoCambio(data['tipo_cambio']),
            fecha_cambio=datetime.fromisoformat(data['fecha_cambio']),
            descripcion=data['descripcion'],
            datos_anteriores=data.get('datos_anteriores'),
            datos_nuevos=data.get('datos_nuevos')
        )

    def guardar(self, cuenta: CuentaServicio) -> None:
        """Guarda una cuenta de servicio"""
        self.cuentas[cuenta.id] = cuenta
        self._guardar_cuentas()

    def obtener_por_id(self, id: str) -> Optional[CuentaServicio]:
        """Obtiene una cuenta por su ID"""
        return self.cuentas.get(id)

    def obtener_todas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas"""
        return list(self.cuentas.values())

    def obtener_por_tipo(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo de servicio"""
        return [cuenta for cuenta in self.cuentas.values()
                if cuenta.tipo_servicio == tipo]

    def obtener_por_fecha(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[CuentaServicio]:
        """Obtiene cuentas por rango de fechas"""
        return [cuenta for cuenta in self.cuentas.values()
                if fecha_inicio <= cuenta.fecha_emision <= fecha_fin]

    def obtener_vencidas(self) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        return [cuenta for cuenta in self.cuentas.values()
                if cuenta.esta_vencida()]

    def obtener_pendientes(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes de pago"""
        return [cuenta for cuenta in self.cuentas.values()
                if not cuenta.pagado]

    def eliminar(self, id: str) -> bool:
        """Elimina una cuenta por su ID"""
        if id in self.cuentas:
            del self.cuentas[id]
            self._guardar_cuentas()
            return True
        return False

    def actualizar(self, cuenta: CuentaServicio) -> bool:
        """Actualiza una cuenta existente"""
        if cuenta.id in self.cuentas:
            self.cuentas[cuenta.id] = cuenta
            self._guardar_cuentas()
            return True
        return False

class JSONResumenRepository(ResumenRepository):
    """Implementación del repositorio de resúmenes"""

    def __init__(self, cuenta_repository: CuentaServicioRepository):
        self.cuenta_repository = cuenta_repository

    def generar_resumen_mensual(self, mes: int, año: int) -> ResumenMensual:
        """Genera un resumen mensual"""
        resumen = ResumenMensual(mes=mes, año=año)
        todas_las_cuentas = self.cuenta_repository.obtener_todas()

        for cuenta in todas_las_cuentas:
            resumen.agregar_cuenta(cuenta)

        return resumen

    def obtener_resumenes_por_año(self, año: int) -> List[ResumenMensual]:
        """Obtiene todos los resúmenes de un año"""
        resumenes = []
        for mes in range(1, 13):
            resumen = self.generar_resumen_mensual(mes, año)
            resumenes.append(resumen)
        return resumenes