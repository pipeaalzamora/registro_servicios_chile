# 📊 Registro de Servicios Chile

Aplicación de escritorio para gestionar cuentas de servicios básicos (luz, agua, gas, internet, gastos comunes) con tema oscuro y reportes PDF.

## ✨ Características

- **Gestión de cuentas**: Servicios básicos con fechas y montos
- **Estados automáticos**: Pagado, vencido, pendiente
- **Tema oscuro**: Interfaz optimizada para fondo oscuro
- **Reportes PDF**: Mensuales y anuales
- **Base de datos dual**: MongoDB con fallback a JSON
- **Búsqueda y filtros**: Por tipo y estado

## 🚀 Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/registro_servicios_chile.git
cd registro_servicios_chile

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

## 📖 Uso

1. **Nueva cuenta**: Botón "Nueva Cuenta" con meses por nombre
2. **Editar**: Doble click en cuenta existente
3. **Reportes**: Botón "Generar" para PDFs
4. **Filtros**: Búsqueda por tipo y estado

## 🛠️ Tecnologías

- **Python 3.8+** con Tkinter
- **MongoDB** (opcional, fallback a JSON)
- **ReportLab** para PDFs
- **Matplotlib** para gráficos

## 🏗️ Estructura

```
├── app.py              # Aplicación principal
├── models.py           # Modelos de datos
├── database_mongodb.py # Gestor de BD
├── reports.py          # Reportes PDF
├── ui/                 # Interfaz
│   ├── main_window.py  # Ventana principal
│   ├── components.py   # Diálogos y componentes
│   └── themes.py       # Tema oscuro
└── requirements.txt    # Dependencias
```

---

**Versión simplificada con tema oscuro y meses por nombre**
