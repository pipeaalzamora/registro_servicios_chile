"""
Gestor de base de datos simplificado
Inicialmente con JSON, preparado para migrar a MongoDB
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
import uuid
import shutil

from models import CuentaServicio, TipoServicio, ResumenMensual


class DatabaseManager:
    """Gestor de base de datos con JSON (temporal, migraremos a MongoDB)"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.cuentas_file = self.data_dir / "cuentas.json"
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)

        # Cargar datos existentes
        self._load_data()

    def _load_data(self):
        """Carga los datos desde el archivo JSON"""
        if self.cuentas_file.exists():
            try:
                with open(self.cuentas_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cuentas = {
                        cuenta_id: CuentaServicio.from_dict(cuenta_data)
                        for cuenta_id, cuenta_data in data.items()
                    }
            except Exception as e:
                print(f"Error cargando datos: {e}")
                self.cuentas = {}
        else:
            self.cuentas = {}

    def _save_data(self):
        """Guarda los datos en el archivo JSON"""
        try:
            # Crear backup antes de guardar
            self._create_backup()

            data = {
                cuenta_id: cuenta.to_dict()
                for cuenta_id, cuenta in self.cuentas.items()
            }

            with open(self.cuentas_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error guardando datos: {e}")
            raise

    def _create_backup(self):
        """Crea un backup de los datos actuales"""
        if self.cuentas_file.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"cuentas_backup_{timestamp}.json"
            shutil.copy2(self.cuentas_file, backup_file)

            # Limpiar backups antiguos (mantener solo los últimos 10)
            self._cleanup_old_backups()

    def _cleanup_old_backups(self, max_backups: int = 10):
        """Limpia backups antiguos"""
        backup_files = list(self.backup_dir.glob("cuentas_backup_*.json"))
        if len(backup_files) > max_backups:
            # Ordenar por fecha de modificación y eliminar los más antiguos
            backup_files.sort(key=lambda x: x.stat().st_mtime)
            for old_backup in backup_files[:-max_backups]:
                old_backup.unlink()

    def _generate_id(self) -> str:
        """Genera un ID único para una cuenta"""
        return str(uuid.uuid4())

    # CRUD Operations
    def crear_cuenta(self, cuenta: CuentaServicio) -> str:
        """Crea una nueva cuenta"""
        if not cuenta.id:
            cuenta.id = self._generate_id()

        cuenta.created_at = datetime.now()
        cuenta.updated_at = datetime.now()

        self.cuentas[cuenta.id] = cuenta
        self._save_data()
        return cuenta.id

    def obtener_cuenta(self, cuenta_id: str) -> Optional[CuentaServicio]:
        """Obtiene una cuenta por ID"""
        return self.cuentas.get(cuenta_id)

    def obtener_todas_las_cuentas(self) -> List[CuentaServicio]:
        """Obtiene todas las cuentas"""
        return list(self.cuentas.values())

    def actualizar_cuenta(self, cuenta: CuentaServicio) -> bool:
        """Actualiza una cuenta existente"""
        if cuenta.id and cuenta.id in self.cuentas:
            cuenta.updated_at = datetime.now()
            self.cuentas[cuenta.id] = cuenta
            self._save_data()
            return True
        return False

    def eliminar_cuenta(self, cuenta_id: str) -> bool:
        """Elimina una cuenta"""
        if cuenta_id in self.cuentas:
            del self.cuentas[cuenta_id]
            self._save_data()
            return True
        return False

    # Consultas específicas
    def obtener_cuentas_por_tipo(self, tipo: TipoServicio) -> List[CuentaServicio]:
        """Obtiene cuentas por tipo de servicio"""
        return [cuenta for cuenta in self.cuentas.values()
                if cuenta.tipo_servicio == tipo]

    def obtener_cuentas_pendientes(self) -> List[CuentaServicio]:
        """Obtiene cuentas pendientes de pago"""
        return [cuenta for cuenta in self.cuentas.values()
                if not cuenta.pagado]

    def obtener_cuentas_vencidas(self) -> List[CuentaServicio]:
        """Obtiene cuentas vencidas"""
        return [cuenta for cuenta in self.cuentas.values()
                if cuenta.get_estado().value == "Vencido"]

    def obtener_cuentas_por_mes(self, mes: int, año: int) -> List[CuentaServicio]:
        """Obtiene cuentas por mes y año"""
        return [cuenta for cuenta in self.cuentas.values()
                if cuenta.fecha_emision.month == mes and cuenta.fecha_emision.year == año]

    def buscar_cuentas(self, termino: str) -> List[CuentaServicio]:
        """Busca cuentas por término en descripción u observaciones"""
        termino = termino.lower()
        return [cuenta for cuenta in self.cuentas.values()
                if termino in cuenta.descripcion.lower() or
                   termino in cuenta.observaciones.lower() or
                   termino in cuenta.tipo_servicio.value.lower()]

    # Estadísticas
    def obtener_resumen_mensual(self, mes: int, año: int) -> ResumenMensual:
        """Genera resumen mensual"""
        cuentas_mes = self.obtener_cuentas_por_mes(mes, año)

        resumen = ResumenMensual(mes=mes, año=año)
        cuentas_por_tipo = {}

        for cuenta in cuentas_mes:
            resumen.total_gastos += cuenta.monto

            if cuenta.pagado:
                resumen.total_pagado += cuenta.monto
                resumen.cuentas_pagadas += 1
            else:
                resumen.total_pendiente += cuenta.monto
                resumen.cuentas_pendientes += 1

                if cuenta.get_estado().value == "Vencido":
                    resumen.cuentas_vencidas += 1

            # Agrupar por tipo
            tipo = cuenta.tipo_servicio.value
            if tipo not in cuentas_por_tipo:
                cuentas_por_tipo[tipo] = {'total': 0, 'pagado': 0, 'pendiente': 0}

            cuentas_por_tipo[tipo]['total'] += cuenta.monto
            if cuenta.pagado:
                cuentas_por_tipo[tipo]['pagado'] += cuenta.monto
            else:
                cuentas_por_tipo[tipo]['pendiente'] += cuenta.monto

        resumen.cuentas_por_tipo = cuentas_por_tipo
        return resumen

    def obtener_total_por_tipo(self) -> Dict[str, float]:
        """Obtiene el total gastado por tipo de servicio"""
        totales = {}
        for cuenta in self.cuentas.values():
            tipo = cuenta.tipo_servicio.value
            if tipo not in totales:
                totales[tipo] = 0
            totales[tipo] += cuenta.monto
        return totales

    def obtener_estadisticas_generales(self) -> Dict:
        """Obtiene estadísticas generales"""
        todas_las_cuentas = list(self.cuentas.values())

        if not todas_las_cuentas:
            return {
                'total_cuentas': 0,
                'total_gastos': 0,
                'total_pagado': 0,
                'total_pendiente': 0,
                'cuentas_pagadas': 0,
                'cuentas_pendientes': 0,
                'cuentas_vencidas': 0
            }

        total_gastos = sum(cuenta.monto for cuenta in todas_las_cuentas)
        cuentas_pagadas = [cuenta for cuenta in todas_las_cuentas if cuenta.pagado]
        cuentas_pendientes = [cuenta for cuenta in todas_las_cuentas if not cuenta.pagado]
        cuentas_vencidas = [cuenta for cuenta in todas_las_cuentas
                           if cuenta.get_estado().value == "Vencido"]

        total_pagado = sum(cuenta.monto for cuenta in cuentas_pagadas)
        total_pendiente = sum(cuenta.monto for cuenta in cuentas_pendientes)

        return {
            'total_cuentas': len(todas_las_cuentas),
            'total_gastos': total_gastos,
            'total_pagado': total_pagado,
            'total_pendiente': total_pendiente,
            'cuentas_pagadas': len(cuentas_pagadas),
            'cuentas_pendientes': len(cuentas_pendientes),
            'cuentas_vencidas': len(cuentas_vencidas)
        }