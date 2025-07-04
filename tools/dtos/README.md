# DTOs (Data Transfer Objects) - Tools

## Descripción General
Este directorio contiene las estructuras de datos (DTOs) utilizadas para transferir información entre diferentes servicios y componentes del sistema de herramientas.

## Propósito

Los DTOs proporcionan:
- **Estructura consistente**: Formato estandarizado para intercambio de datos
- **Validación**: Validación de datos entrantes y salientes
- **Serialización**: Conversión entre objetos Python y JSON
- **Documentación**: Definición clara de la estructura de datos esperada

## Estructura Típica

Los DTOs en este directorio incluyen:

### Request DTOs
- Estructuras para parámetros de entrada de herramientas
- Validadores de tipos de datos
- Valores por defecto y opcionales

### Response DTOs
- Estructuras para respuestas de herramientas
- Códigos de estado y mensajes de error
- Datos de resultado procesados

### Configuration DTOs
- Estructuras para configuración de herramientas
- Parámetros de autenticación
- Configuraciones específicas por tipo de herramienta

## Uso

Los DTOs se utilizan en:
- Servicios de herramientas para validar datos
- APIs para serializar/deserializar información
- Pruebas unitarias para estructuras de datos consistentes
- Documentación automática de APIs

## Ejemplos de Uso

```python
# Ejemplo de uso de un DTO de respuesta
from .response_dto import ToolResponseDTO

response = ToolResponseDTO(
    success=True,
    data={"result": "processed_data"},
    message="Tool executed successfully"
)
```

## Beneficios

- **Tipo Safety**: Validación de tipos en tiempo de ejecución
- **Mantenibilidad**: Cambios centralizados en estructuras de datos
- **Documentación**: Auto-documentación de la estructura de datos
- **Testabilidad**: Fácil creación de datos de prueba
