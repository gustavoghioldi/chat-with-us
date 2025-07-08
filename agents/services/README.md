# Servicios de Agentes

## Descripción General
Este directorio contiene los servicios principales para la gestión y configuración de agentes de IA. Proporciona una abstracción para diferentes proveedores de modelos de lenguaje y maneja la configuración, almacenamiento y operaciones de agentes.

## Estructura de Archivos

### `agent_service.py`
Servicio principal para la gestión de agentes. Incluye:
- Creación y configuración de agentes
- Manejo de conversaciones
- Integración con diferentes proveedores de IA
- Gestión de contexto y memoria

```python
from agents.services.agent_service import AgentService

# Ejemplo de uso
agent_service = AgentService()
response = agent_service.generate_response(
    agent_id="agent_123",
    message="Hola, ¿cómo puedo ayudarte?",
    context={"user_id": "user_456"}
)
```

### `agent_service_configure.py`
Servicio para la configuración de agentes. Funcionalidades:
- Configuración de parámetros de modelo
- Validación de configuraciones
- Actualización de configuraciones existentes
- Gestión de templates y prompts

```python
from agents.services.agent_service_configure import AgentServiceConfigure

# Ejemplo de configuración
configurator = AgentServiceConfigure()
configurator.configure_agent(
    agent_id="agent_123",
    model_config={
        "temperature": 0.7,
        "max_tokens": 1000,
        "provider": "openai"
    }
)
```

### `agent_storage_service.py`
Servicio para el almacenamiento y recuperación de agentes. Incluye:
- Persistencia de configuraciones
- Caché de modelos
- Manejo de metadatos
- Integración con diferentes sistemas de almacenamiento

```python
from agents.services.agent_storage_service import AgentStorageService

# Ejemplo de uso
storage_service = AgentStorageService()
agent_data = storage_service.get_agent_data("agent_123")
storage_service.save_agent_data("agent_123", updated_data)
```

### `storage_factory.py`
Factory pattern para la creación de diferentes tipos de almacenamiento. Soporta:
- Almacenamiento en base de datos
- Almacenamiento en archivos
- Almacenamiento en S3
- Caché en memoria

```python
from agents.services.storage_factory import StorageFactory

# Ejemplo de uso
storage = StorageFactory.create_storage("database")
storage.save(key="agent_123", data=agent_data)
```

### Carpeta `configurators/`
Contiene configuradores específicos para diferentes proveedores de IA:
- `openai_configurator.py`: Configuración para OpenAI GPT
- `gemini_configurator.py`: Configuración para Google Gemini
- `bedrock_configurator.py`: Configuración para Amazon Bedrock
- `ollama_configurator.py`: Configuración para Ollama
- `base_configurator.py`: Clase base para configuradores
- `factory.py`: Factory para crear configuradores

## Patrones de Diseño

### Factory Pattern
Se utiliza para crear instancias de configuradores según el proveedor:

```python
from agents.services.configurators.factory import ConfiguratorFactory

configurator = ConfiguratorFactory.create_configurator("openai")
config = configurator.get_config(model_params)
```

### Strategy Pattern
Cada configurador implementa una estrategia específica para su proveedor:

```python
class OpenAIConfigurator(BaseConfigurator):
    def configure(self, params):
        # Implementación específica para OpenAI
        pass
```

## Casos de Uso

### 1. Crear un Nuevo Agente
```python
# Configurar el agente
configurator = AgentServiceConfigure()
configurator.configure_agent(
    agent_id="new_agent",
    model_config={
        "provider": "openai",
        "model": "gpt-4",
        "temperature": 0.7
    }
)

# Guardar configuración
storage_service = AgentStorageService()
storage_service.save_agent_data("new_agent", config_data)
```

### 2. Procesar Conversación
```python
# Obtener respuesta del agente
agent_service = AgentService()
response = agent_service.generate_response(
    agent_id="agent_123",
    message="¿Cuál es el clima hoy?",
    context={"location": "Madrid"}
)
```

### 3. Cambiar Proveedor de IA
```python
# Reconfigurar para usar diferente proveedor
configurator_factory = ConfiguratorFactory()
new_configurator = configurator_factory.create_configurator("gemini")
new_config = new_configurator.configure(params)
```

## Dependencias
- `django`: Framework web
- `openai`: Cliente para OpenAI
- `google-generativeai`: Cliente para Gemini
- `boto3`: Cliente para AWS Bedrock
- `requests`: Para llamadas HTTP a Ollama

## Configuración
Las configuraciones se manejan a través de variables de entorno:

```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Gemini
GEMINI_API_KEY=your_gemini_key

# AWS Bedrock
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
```

## Testing
Los servicios incluyen tests unitarios y de integración:

```python
# Ejemplo de test
def test_agent_service_response():
    agent_service = AgentService()
    response = agent_service.generate_response(
        agent_id="test_agent",
        message="Test message"
    )
    assert response is not None
    assert len(response) > 0
```

## Mejores Prácticas

1. **Manejo de Errores**: Siempre manejar excepciones de APIs externas
2. **Logging**: Registrar operaciones importantes para debugging
3. **Caching**: Cachear configuraciones para mejorar rendimiento
4. **Validación**: Validar parámetros antes de enviar a APIs
5. **Timeouts**: Configurar timeouts apropiados para APIs externas

## Monitoreo
- Métricas de latencia de respuesta
- Conteo de tokens utilizados
- Errores de API por proveedor
- Uso de memoria y CPU

## Extensibilidad
Para agregar un nuevo proveedor:

1. Crear configurador específico heredando de `BaseConfigurator`
2. Implementar métodos requeridos
3. Registrar en `ConfiguratorFactory`
4. Agregar tests correspondientes

```python
class NewProviderConfigurator(BaseConfigurator):
    def configure(self, params):
        # Implementación específica
        pass
```
