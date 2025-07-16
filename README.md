# 📊 Registro de Servicios Chile

Una aplicación completa y profesional para gestionar cuentas de servicios básicos (luz, agua, gas, internet, gastos comunes) con interfaz gráfica moderna, reportes PDF y funcionalidades avanzadas.

## ✨ Características Principales

### 🏠 Gestión de Cuentas

- **Servicios soportados**: Luz, agua, gas, internet, gastos comunes
- **Información completa**: Montos, fechas de emisión, vencimiento, próxima lectura y corte
- **Estados inteligentes**: Pagado, vencido, en riesgo de corte, pendiente
- **Validaciones avanzadas**: Montos positivos, fechas coherentes, datos obligatorios

### 🎨 Interfaz de Usuario Moderna

- **Búsqueda rápida**: Filtrado en tiempo real por nombre, descripción y monto
- **Ordenamiento avanzado**: Por cualquier columna con indicadores visuales
- **Colores semánticos**: Estados diferenciados por colores intuitivos
- **Calendario integrado**: Selección visual de fechas con navegación
- **Componentes modulares**: Arquitectura escalable y mantenible

### 📈 Análisis y Reportes

- **Estadísticas en tiempo real**: Resumen de cuentas y montos
- **Gráficos interactivos**: Visualización de gastos por servicio, mes y evolución anual
- **Reportes PDF profesionales**: Exportación con formato chileno (CLP)
- **Historial de cambios**: Rastreo completo de modificaciones

### 🔔 Notificaciones Inteligentes

- **Recordatorios automáticos**: Alertas por email configurables
- **Notificaciones de vencimiento**: Avisos antes del corte
- **Sistema de logs**: Registro de actividades y seguridad

### 🛡️ Seguridad y Confiabilidad

- **Backups automáticos**: Respaldo de datos críticos
- **Validación de datos**: Sanitización y verificación de entrada
- **Logs de seguridad**: Auditoría de operaciones
- **Almacenamiento local**: Sin dependencias de bases de datos externas

## 🚀 Instalación Rápida

### Requisitos

- Python 3.8 o superior
- Windows 10/11 (optimizado)

### Instalación Automática (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/registro_servicios_chile.git
cd registro_servicios_chile

# Ejecutar instalador automático
install.bat
```

### Instalación Manual

```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

## 📖 Guía de Uso

### Primeros Pasos

1. **Ejecutar la aplicación**: `python main.py` o `run.bat`
2. **Crear primera cuenta**: Botón "Nuevo Registro"
3. **Completar información**: Usar calendario para fechas
4. **Guardar**: Los datos se almacenan automáticamente

### Funcionalidades Principales

#### 🔍 Búsqueda y Filtrado

- **Búsqueda rápida**: Escribe en el campo de búsqueda para filtrar
- **Ordenamiento**: Haz clic en los encabezados de columna
- **Filtros avanzados**: Por estado, tipo de servicio, rango de fechas

#### 📊 Estadísticas y Gráficos

- **Vista general**: Resumen en tiempo real en la parte superior
- **Gráficos**: Visualiza patrones de gastos y tendencias
- **Reportes**: Exporta a PDF con formato profesional

#### ⚙️ Configuración

- **Notificaciones**: Configura alertas por email en `config/notifications.json`
- **Backups**: Se crean automáticamente en `data/backups/`
- **Logs**: Revisa actividad en `data/logs/`

## 🏗️ Arquitectura del Proyecto

```
registro_servicios_chile/
├── 📁 src/
│   ├── 🏛️ domain/           # Entidades y reglas de negocio
│   ├── ⚙️ application/      # Casos de uso y lógica de aplicación
│   ├── 🔧 infrastructure/   # Persistencia y servicios externos
│   └── 🎨 presentation/     # Interfaz de usuario y componentes
├── 📁 data/                 # Datos locales y backups
├── 📁 config/              # Configuraciones y notificaciones
├── 📁 reports/             # Reportes PDF generados
├── 📄 main.py              # Punto de entrada principal
├── 📄 requirements.txt     # Dependencias de Python
├── 🚀 install.bat          # Instalador automático
└── ▶️ run.bat              # Ejecutor rápido
```

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje principal
- **Tkinter**: Interfaz gráfica nativa
- **ReportLab**: Generación de PDFs
- **Matplotlib**: Gráficos y visualizaciones
- **JSON**: Almacenamiento de datos
- **Arquitectura Limpia**: Separación de responsabilidades

## 📋 Funcionalidades Detalladas

### Gestión de Cuentas

- ✅ Crear, editar y eliminar cuentas
- ✅ Validación automática de datos
- ✅ Estados inteligentes con colores
- ✅ Historial completo de cambios
- ✅ Fechas de próxima lectura y corte

### Interfaz de Usuario

- ✅ Búsqueda en tiempo real
- ✅ Ordenamiento por columnas
- ✅ Calendario integrado
- ✅ Colores semánticos
- ✅ Componentes modulares

### Reportes y Análisis

- ✅ Exportación a PDF
- ✅ Gráficos interactivos
- ✅ Estadísticas en tiempo real
- ✅ Formato de moneda chilena (CLP)

### Seguridad

- ✅ Validaciones avanzadas
- ✅ Backups automáticos
- ✅ Logs de seguridad
- ✅ Sanitización de datos

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes sugerencias:

1. Revisa los [Issues](https://github.com/tu-usuario/registro_servicios_chile/issues)
2. Crea un nuevo issue con detalles del problema
3. Incluye información del sistema y pasos para reproducir

## 🎯 Próximas Mejoras

- [ ] Sincronización en la nube
- [ ] Aplicación móvil
- [ ] Integración con APIs de servicios
- [ ] Reportes personalizables
- [ ] Múltiples monedas
- [ ] Exportación a Excel

---

⭐ **¡Si te gusta este proyecto, dale una estrella en GitHub!**
