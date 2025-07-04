# Models - Tools

## Descripción General
Este directorio contiene los modelos de datos para el sistema de herramientas, definiendo la estructura de las tablas de base de datos y las relaciones entre diferentes tipos de herramientas.

## Modelos Principales

### api_call_model.py
Define el modelo `ApiCallModel` para herramientas que realizan llamadas a APIs externas.

#### Campos Principales:
- **name**: Nombre identificativo de la herramienta
- **url**: URL base de la API
- **method**: Método HTTP (GET, POST, PUT, DELETE)
- **headers**: Headers personalizados para la solicitud
- **authentication**: Tipo de autenticación (Bearer, API Key, etc.)
- **timeout**: Tiempo límite para la solicitud
- **retry_count**: Número de reintentos en caso de fallo
- **tenant**: Relación con el tenant propietario

#### Funcionalidades:
- Validación de URLs y métodos HTTP
- Gestión de autenticación
- Configuración de timeouts y reintentos
- Serialización de parámetros
- Logging de llamadas

### Otros Modelos (Extensiones Futuras)

#### DatabaseToolModel
Para herramientas que interactúan con bases de datos:
- **connection_string**: Cadena de conexión a la base de datos
- **query_template**: Plantilla de consulta SQL
- **parameters**: Parámetros de la consulta

#### FileProcessingToolModel
Para herramientas que procesan archivos:
- **supported_formats**: Formatos de archivo soportados
- **max_file_size**: Tamaño máximo de archivo
- **processing_options**: Opciones de procesamiento

#### NotificationToolModel
Para herramientas de notificación:
- **notification_type**: Tipo de notificación (email, SMS, webhook)
- **template**: Plantilla de mensaje
- **recipients**: Destinatarios por defecto

## Relaciones con otros Modelos

### Con AgentModel
- Las herramientas se asocian a agentes a través de ManyToManyField
- Un agente puede tener múltiples herramientas
- Una herramienta puede ser usada por múltiples agentes

### Con TenantModel
- Todas las herramientas están asociadas a un tenant
- Aislamiento de datos por tenant
- Configuraciones específicas por tenant

## Funcionalidades Comunes

### Validación
- Validación de URLs y formatos
- Validación de parámetros de configuración
- Validación de permisos y autenticación

### Serialización
- Serialización de configuraciones complejas
- Manejo de tipos de datos específicos
- Conversión entre formatos

### Auditoría
- Tracking de uso de herramientas
- Logging de ejecuciones
- Métricas de rendimiento

## Ejemplo de Uso

```python
from .api_call_model import ApiCallModel

# Crear una nueva herramienta API
api_tool = ApiCallModel.objects.create(
    name="Weather API",
    url="https://api.weather.com/v1/current",
    method="GET",
    headers={"API-Key": "your_api_key"},
    timeout=30,
    retry_count=3,
    tenant=current_tenant
)

# Asociar a un agente
agent.api_call_models.add(api_tool)
```

## Extensibilidad

### Agregar Nuevos Tipos de Herramientas
1. Crear nuevo modelo heredando de `BaseToolModel`
2. Definir campos específicos del tipo de herramienta
3. Implementar métodos de validación
4. Agregar al admin de Django
5. Crear migraciones correspondientes

### Migración de Datos
- Scripts para migrar herramientas existentes
- Validación de integridad de datos
- Backup automático antes de migraciones

## Mejores Prácticas

1. **Herencia**: Usar herencia de modelos para funcionalidades comunes
2. **Validación**: Implementar validación a nivel de modelo
3. **Métodos Helper**: Agregar métodos útiles a los modelos
4. **Documentación**: Documentar todos los campos y métodos
5. **Tests**: Crear pruebas para todos los modelos
