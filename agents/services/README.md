# Servicios de Agentes

## Descripción General
Este directorio contiene los servicios principales para la gestión y operación de agentes de IA. Proporciona una abstracción para diferentes proveedores de modelos de lenguaje (Ollama y Gemini) y maneja la configuración, creación y operaciones de agentes utilizando la librería `agno`.

## Estructura de Archivos

### `agent_service.py`
Servicio principal que actúa como interfaz de alto nivel para interactuar con agentes. Funcionalidades:
- Inicialización de agentes por nombre desde la base de datos
- Manejo de conversaciones y envío de mensajes
- Procesamiento y limpieza de respuestas
- Integración con `AgentFactoryService` para la creación de agentes

```python
from agents.services.agent_service import AgentService

# Ejemplo de uso
agent_service = AgentService(agent_name="mi_agente", session_id="session_123")
response, session_id = agent_service.send_message(
    message="Hola, ¿cómo puedo ayudarte?",
    session_id="session_123"
)
```

**Métodos principales:**
- `__init__(agent_name: str, session_id=None)`: Inicializa el servicio con un agente específico
- `send_message(message: str, session_id: str, clean_response: bool = True)`: Envía un mensaje al agente
- `get_agent_model()`: Obtiene el modelo de agente de la base de datos

### `agent_factory_service.py`
Factory service para la creación y configuración de agentes. Implementa el patrón Factory para crear instancias de agentes configuradas según el proveedor especificado. Funcionalidades:
- Creación de agentes basados en modelos Ollama o Gemini
- Configuración de memoria persistente con PostgreSQL
- Integración con knowledge bases de documentos
- Configuración de almacenamiento de sesiones

```python
from agents.services.agent_factory_service import AgentFactoryService

# Ejemplo de uso
factory = AgentFactoryService(
    agent_model=agent_model_instance,
    session_id="session_123",
    user_id="user_456"
)
agent = factory.get_agent()
```

**Métodos principales:**
- `__init__(agent_model: AgentModel, session_id=None, user_id=None)`: Inicializa el factory
- `get_agent() -> Agent`: Crea y retorna un agente configurado
- `configure(model) -> Agent`: Configura un agente con el modelo especificado

**Proveedores soportados:**
- **Ollama**: Para modelos locales
- **Gemini**: Para modelos de Google AI

### `agent_memory_service.py`
Servicio para la gestión de memoria de agentes (actualmente vacío, preparado para implementación futura).

## Arquitectura del Sistema

### Modelo de Datos
El sistema utiliza los siguientes modelos principales:

**AgentModel:**
- `name`: Nombre único del agente
- `instructions`: Instrucciones para el agente
- `description`: Descripción del agente
- `max_tokens`: Límite de tokens para respuestas
- `temperature`: Control de aleatoriedad (0.0-1.0)
- `top_p`: Control de diversidad (0.0-1.0)
- `agent_model_id`: ID del modelo de IA específico
- `tenant`: Relación con el inquilino (TenantModel)

**TenantModel:**
- `name`: Nombre del inquilino
- `model`: Proveedor de IA ("ollama" o "gemini")
- `ai_token`: Token de autenticación para el proveedor
- `cwu_token`: Token único del tenant

### Flujo de Trabajo

1. **Inicialización**: `AgentService` obtiene el `AgentModel` de la base de datos
2. **Creación**: `AgentFactoryService` crea una instancia de agente configurada
3. **Configuración**: Se configura memoria, almacenamiento y knowledge base
4. **Ejecución**: El agente procesa mensajes y genera respuestas

## Configuración

### Base de Datos
El sistema utiliza PostgreSQL para:
- Almacenamiento de memoria de agentes (tabla: `agent_memory`)
- Almacenamiento de sesiones (tabla: `agent_sessions`)

```python
# Configuración de base de datos
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"
```

### Proveedores de IA

**Ollama (Local):**
- No requiere token de API
- Configuración automática para modelos locales

**Gemini (Google AI):**
- Requiere `ai_token` en el modelo `TenantModel`
- Configuración automática con token de autenticación

## Dependencias

### Principales
- `django`: Framework web para modelos y ORM
- `agno`: Librería para creación y manejo de agentes IA
- `psycopg`: Driver PostgreSQL para Python

### Integración
- `tools.kit.obtener_datos_de_factura`: Herramientas específicas del dominio
- `knowledge.services.document_knowledge_base_service`: Servicio de knowledge base
- `tenants.models`: Modelos de inquilinos

## Casos de Uso

### 1. Crear y Usar un Agente
```python
# Inicializar servicio con agente existente
agent_service = AgentService(agent_name="asistente_ventas")

# Enviar mensaje
response, session_id = agent_service.send_message(
    message="¿Cuáles son nuestros productos estrella?",
    session_id="session_123"
)

print(f"Respuesta: {response}")
```

### 2. Configuración Manual de Agente
```python
# Obtener modelo de agente
agent_model = AgentModel.objects.get(name="mi_agente")

# Crear factory
factory = AgentFactoryService(
    agent_model=agent_model,
    session_id="session_123",
    user_id="user_456"
)

# Obtener agente configurado
agent = factory.get_agent()

# Usar directamente
response = agent.run("Tu mensaje aquí")
```

### 3. Cambiar Proveedor de IA
```python
# Cambiar el proveedor en el tenant
tenant = TenantModel.objects.get(name="mi_empresa")
tenant.model = "gemini"  # Cambiar de "ollama" a "gemini"
tenant.ai_token = "tu_token_de_gemini"
tenant.save()

# El agente automáticamente usará el nuevo proveedor
agent_service = AgentService(agent_name="mi_agente")
```

## Características Avanzadas

### Memoria Persistente
- Memoria de usuario habilitada para recordar contexto entre sesiones
- Resúmenes de sesión automáticos
- Historial de conversaciones configurable

### Knowledge Base
- Integración automática con documentos del knowledge base
- Búsqueda semántica en documentos
- Contextualización de respuestas

### Limpieza de Respuestas
- Eliminación automática de etiquetas `<think>` en respuestas
- Filtrado de contenido no deseado
- Formateo consistente de salida

## Extensibilidad

### Agregar Nuevo Proveedor
Para agregar un nuevo proveedor de IA:

1. Actualizar `TenantModel.model` con nueva opción
2. Modificar `AgentFactoryService.get_agent()` para manejar el nuevo proveedor
3. Agregar configuración específica en `configure()` si es necesario

```python
# Ejemplo de extensión
def get_agent(self) -> Agent:
    if self._agent_model.tenant.model == "ollama":
        self.__model = Ollama
    elif self._agent_model.tenant.model == "gemini":
        self.__model = Gemini
    elif self._agent_model.tenant.model == "nuevo_proveedor":
        self.__model = NuevoProveedor
    return self.configure(self.__model)
```

## Mejores Prácticas

1. **Gestión de Errores**: Manejar `AgentModel.DoesNotExist` en inicialización
2. **Logging**: Utilizar logging para debug y monitoreo
3. **Sesiones**: Usar IDs de sesión consistentes para mantener contexto
4. **Limpieza**: Activar limpieza de respuestas para mejor UX
5. **Memoria**: Configurar límites apropiados de historial según el caso de uso

## Monitoreo y Logging

```python
import logging

logger = logging.getLogger(__name__)

# Los servicios incluyen logging automático para:
# - Errores de inicialización
# - Respuestas de agentes
# - Operaciones de base de datos
```

## Testing

```python
# Ejemplo de test básico
def test_agent_service_creation():
    agent_service = AgentService(agent_name="test_agent")
    assert agent_service.get_agent_model() is not None

def test_agent_response():
    agent_service = AgentService(agent_name="test_agent")
    response, session_id = agent_service.send_message(
        message="Test message",
        session_id="test_session"
    )
    assert response is not None
    assert len(response) > 0
```
