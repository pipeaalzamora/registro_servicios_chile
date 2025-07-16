# 🤝 Guía de Contribución

¡Gracias por tu interés en contribuir a **Registro de Servicios Chile**! Este documento te ayudará a comenzar.

## 🚀 Cómo Contribuir

### 1. Configuración del Entorno

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/registro_servicios_chile.git
cd registro_servicios_chile

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Flujo de Trabajo

1. **Fork** el repositorio
2. **Crea una rama** para tu feature:
   ```bash
   git checkout -b feature/nombre-de-tu-feature
   ```
3. **Haz tus cambios** siguiendo las convenciones
4. **Prueba** tu código
5. **Commit** tus cambios:
   ```bash
   git commit -m "feat: agregar nueva funcionalidad"
   ```
6. **Push** a tu fork:
   ```bash
   git push origin feature/nombre-de-tu-feature
   ```
7. **Crea un Pull Request**

## 📋 Convenciones de Código

### Estructura del Proyecto

- **Domain**: Entidades y reglas de negocio
- **Application**: Casos de uso y lógica de aplicación
- **Infrastructure**: Persistencia y servicios externos
- **Presentation**: Interfaz de usuario

### Convenciones de Nomenclatura

- **Clases**: PascalCase (`CuentaService`)
- **Funciones y variables**: snake_case (`crear_cuenta`)
- **Constantes**: UPPER_SNAKE_CASE (`MAX_MONTO`)
- **Archivos**: snake_case (`cuenta_service.py`)

### Documentación

- **Docstrings**: Usar formato Google para todas las funciones públicas
- **Comentarios**: Explicar el "por qué", no el "qué"
- **README**: Mantener actualizado

### Testing

- Crear tests para nuevas funcionalidades
- Mantener cobertura de código > 80%
- Usar nombres descriptivos para los tests

## 🐛 Reportar Bugs

### Antes de Reportar

1. Busca en los [Issues existentes](https://github.com/tu-usuario/registro_servicios_chile/issues)
2. Verifica que el bug no haya sido reportado ya

### Información Requerida

- **Versión**: Python, sistema operativo
- **Pasos**: Cómo reproducir el bug
- **Comportamiento esperado**: Qué debería pasar
- **Comportamiento actual**: Qué está pasando
- **Capturas de pantalla**: Si es relevante

## 💡 Solicitar Features

### Antes de Solicitar

1. Verifica que la feature no exista ya
2. Piensa en el impacto y la implementación

### Información Requerida

- **Descripción**: Qué hace la feature
- **Justificación**: Por qué es necesaria
- **Casos de uso**: Ejemplos específicos
- **Alternativas**: Si las hay

## 🔧 Tipos de Contribuciones

### 🐛 Bug Fixes

- Corregir errores existentes
- Mejorar manejo de errores
- Optimizar rendimiento

### ✨ Nuevas Features

- Agregar funcionalidades
- Mejorar interfaz de usuario
- Nuevos reportes o análisis

### 📚 Documentación

- Mejorar README
- Agregar ejemplos
- Documentar APIs

### 🧪 Testing

- Agregar tests unitarios
- Tests de integración
- Tests de UI

## 📝 Convenciones de Commit

Usa el formato [Conventional Commits](https://www.conventionalcommits.org/):

```
tipo(alcance): descripción

[body opcional]

[footer opcional]
```

### Tipos

- **feat**: Nueva feature
- **fix**: Bug fix
- **docs**: Documentación
- **style**: Formato (no afecta código)
- **refactor**: Refactorización
- **test**: Tests
- **chore**: Mantenimiento

### Ejemplos

```bash
feat(ui): agregar búsqueda en tiempo real
fix(validation): corregir validación de montos negativos
docs(readme): actualizar instrucciones de instalación
refactor(domain): simplificar entidad Cuenta
```

## 🔍 Revisión de Código

### Antes de Enviar PR

- [ ] Código sigue las convenciones
- [ ] Tests pasan
- [ ] Documentación actualizada
- [ ] No hay warnings
- [ ] Funciona en Windows

### Checklist del Revisor

- [ ] Código es legible y mantenible
- [ ] Funcionalidad es correcta
- [ ] Tests son apropiados
- [ ] Documentación es clara
- [ ] No hay regresiones

## 🎯 Áreas de Mejora

### Prioridad Alta

- [ ] Tests unitarios completos
- [ ] Documentación de API
- [ ] Optimización de rendimiento
- [ ] Mejoras de UX

### Prioridad Media

- [ ] Nuevos tipos de reportes
- [ ] Integración con APIs externas
- [ ] Soporte multiplataforma
- [ ] Funcionalidades avanzadas

### Prioridad Baja

- [ ] Temas visuales adicionales
- [ ] Plugins de exportación
- [ ] Integración con calendarios
- [ ] Funcionalidades sociales

## 📞 Contacto

Si tienes preguntas sobre contribuir:

1. **Issues**: Para bugs y features
2. **Discussions**: Para preguntas generales
3. **Wiki**: Para documentación detallada

## 🙏 Agradecimientos

¡Gracias por contribuir a hacer este proyecto mejor para todos!

---

**Nota**: Este proyecto sigue el [Código de Conducta](CODE_OF_CONDUCT.md). Por favor, léelo antes de contribuir.
