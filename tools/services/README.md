# Services - Tools

## Descripción General
Este directorio contiene los servicios que implementan la lógica de negocio para la gestión y ejecución de herramientas. Los servicios actúan como capa intermedia entre los modelos y las vistas/APIs.

## Servicios Principales

### ToolExecutionService
Servicio principal para la ejecución de herramientas:

#### Funcionalidades:
- **Ejecución de herramientas**: Ejecuta herramientas con parámetros dados
- **Validación de parámetros**: Valida parámetros antes de la ejecución
- **Manejo de errores**: Captura y maneja errores de ejecución
- **Logging**: Registra todas las ejecuciones para auditoría
- **Caching**: Cachea resultados para optimizar rendimiento

#### Métodos Principales:
```python
def execute_tool(tool_id, parameters, context=None)
def validate_parameters(tool, parameters)
def handle_execution_error(error, tool, parameters)
def log_execution(tool, parameters, result, duration)
```

### ToolRegistryService
Servicio para gestionar el registro de herramientas:

#### Funcionalidades:
- **Registro de herramientas**: Registra nuevas herramientas en el sistema
- **Descubrimiento**: Descubre herramientas disponibles automáticamente
- **Validación**: Valida que las herramientas cumplan con las interfaces
- **Metadatos**: Gestiona metadatos de herramientas

#### Métodos Principales:
```python
def register_tool(tool_class, metadata)
def discover_tools()
def get_tool_metadata(tool_name)
def validate_tool_interface(tool_class)
```

### ApiCallService
Servicio especializado para herramientas que realizan llamadas API:

#### Funcionalidades:
- **Llamadas HTTP**: Ejecuta llamadas HTTP con configuración específica
- **Autenticación**: Maneja diferentes tipos de autenticación
- **Reintentos**: Implementa lógica de reintentos automáticos
- **Procesamiento de respuestas**: Procesa y valida respuestas de API

#### Métodos Principales:
```python
def make_api_call(api_tool, parameters)
def handle_authentication(api_tool, request)
def process_response(response, api_tool)
def implement_retry_logic(api_tool, call_function)
```

### ToolConfigurationService
Servicio para gestionar configuraciones de herramientas:

#### Funcionalidades:
- **Configuración dinámica**: Permite configurar herramientas en tiempo de ejecución
- **Validación de configuración**: Valida configuraciones antes de aplicarlas
- **Plantillas**: Gestiona plantillas de configuración
- **Versionado**: Mantiene versiones de configuraciones

#### Métodos Principales:
```python
def configure_tool(tool_id, configuration)
def validate_configuration(tool_type, configuration)
def apply_configuration_template(tool_id, template_id)
def get_configuration_history(tool_id)
```

### ToolMonitoringService
Servicio para monitorear el uso y rendimiento de herramientas:

#### Funcionalidades:
- **Métricas de uso**: Recolecta métricas de uso de herramientas
- **Análisis de rendimiento**: Analiza tiempos de ejecución y errores
- **Alertas**: Genera alertas para problemas de rendimiento
- **Reportes**: Genera reportes de uso y rendimiento

#### Métodos Principales:
```python
def collect_usage_metrics(tool_id, execution_data)
def analyze_performance(tool_id, time_range)
def generate_alerts(tool_id, thresholds)
def create_usage_report(tenant_id, time_range)
```

## Servicios de Soporte

### ToolValidationService
- Validación de parámetros de entrada
- Validación de configuraciones
- Validación de permisos y autorizaciones

### ToolCacheService
- Cacheo de resultados de herramientas
- Invalidación de caché
- Gestión de TTL (Time To Live)

### ToolSecurityService
- Verificación de permisos
- Sanitización de datos
- Auditoría de seguridad

## Integración con otros Módulos

### Con Agents
- Los agentes utilizan estos servicios para ejecutar herramientas
- Contexto de ejecución específico por agente
- Configuraciones personalizadas por agente

### Con Tenants
- Aislamiento de datos por tenant
- Configuraciones específicas por tenant
- Métricas segmentadas por tenant

### Con Analysis
- Envío de métricas para análisis
- Datos de rendimiento para reportes
- Información de uso para optimizaciones

## Patrones de Diseño

### Patrón Strategy
- Diferentes estrategias para diferentes tipos de herramientas
- Intercambio dinámico de estrategias de ejecución

### Patrón Observer
- Notificación de eventos de ejecución
- Suscripción a cambios en configuraciones

### Patrón Factory
- Creación de instancias de herramientas
- Configuración automática según tipo

## Manejo de Errores

### Tipos de Errores
- **ValidationError**: Errores de validación de parámetros
- **ExecutionError**: Errores durante la ejecución
- **ConfigurationError**: Errores de configuración
- **AuthenticationError**: Errores de autenticación

### Estrategias de Recuperación
- Reintentos automáticos
- Fallback a configuraciones alternativas
- Notificación de errores críticos

## Configuración y Personalización

### Variables de Entorno
- `TOOL_EXECUTION_TIMEOUT`: Timeout por defecto
- `TOOL_RETRY_COUNT`: Número de reintentos
- `TOOL_CACHE_TTL`: TTL del caché

### Configuración por Tenant
- Límites de ejecución por tenant
- Configuraciones específicas
- Herramientas disponibles por tenant

## Ejemplos de Uso

```python
# Ejecutar una herramienta
from .tool_execution_service import ToolExecutionService

service = ToolExecutionService()
result = service.execute_tool(
    tool_id=123,
    parameters={"url": "https://api.example.com"},
    context={"user_id": 456}
)

# Registrar una nueva herramienta
from .tool_registry_service import ToolRegistryService

registry = ToolRegistryService()
registry.register_tool(CustomTool, {
    "name": "Custom Tool",
    "description": "A custom tool for specific tasks"
})
```
