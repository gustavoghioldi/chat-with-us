# Configuradores de Agentes IA

## Descripción General

El sistema de configuradores utiliza el **patrón Factory** para crear y configurar agentes IA de manera flexible y extensible. Actualmente soporta Ollama y Gemini como proveedores de IA activos.

## Arquitectura

```
BaseAgentConfigurator (Clase Abstracta)
├── OllamaConfigurator
└── GeminiConfigurator

AgentConfiguratorFactory
└── Gestiona todos los configuradores
```

## Configuradores Disponibles

### 1. OllamaConfigurator
- **Modelo**: `ollama`
- **Configuración**: Usa `IA_MODEL` de settings
- **Dependencias**: `agno.models.ollama.Ollama`

### 2. GeminiConfigurator ⭐
- **Modelo**: `gemini`
- **Configuración**: Requiere `ai_token` (Google API Key)
- **Modelos soportados**:
  - `gemini-pro` (por defecto)
  - `gemini-pro-vision`
  - `gemini-1.5-pro`
  - `gemini-1.5-flash`
  - `gemini-ultra`
- **Dependencias**: `google-generativeai` o `agno.models.gemini`

## Configuradores Deshabilitados

Los siguientes configuradores existen en el código pero no están disponibles para nuevos tenants:

### OpenAIConfigurator (DESHABILITADO)
- **Modelo**: `openai` - ❌ No disponible en TenantModel
- **Razón**: Removido de las opciones válidas del modelo

### BedrockConfigurator (DESHABILITADO)
- **Modelo**: `bedrock` - ❌ No disponible en TenantModel
- **Razón**: Removido de las opciones válidas del modelo

## Uso Básico

### 1. Usando el Factory (Recomendado)

```python
from agents.services.configurators import AgentConfiguratorFactory

# Crear configurador automáticamente según el tenant
configurator = AgentConfiguratorFactory.create_configurator(
    agent_model=mi_agente_model,
    knowledge_base=knowledge_base,  # Opcional
    storage_service=storage_service  # Opcional
)

# Configurar el agente
agent = configurator.configure()
```

### 2. Usando configuradores específicos

```python
from agents.services.configurators import GeminiConfigurator

# Crear configurador específico
configurator = GeminiConfigurator(
    agent_model=mi_agente_model,
    knowledge_base=knowledge_base,
    storage_service=storage_service
)

# Configurar el agente
agent = configurator.configure()
```

## Configuración del Tenant para Gemini

Para usar Gemini, configure el tenant así:

```python
tenant = TenantModel.objects.create(
    name="Mi Tenant Gemini",
    model="gemini",  # ← Importante
    ai_token="your-google-api-key"  # ← API Key de Google
)

agent = AgentModel.objects.create(
    name="Mi Agente Gemini",
    instructions="Eres un asistente IA inteligente",
    agent_model_id="gemini-pro",  # Opcional, usa gemini-pro por defecto
    temperature=0.7,
    top_p=0.9,
    max_tokens=1000,
    tenant=tenant
)
```

## Instalación de Dependencias

### Para Gemini
```bash
pip install google-generativeai
```

### Para OpenAI
```bash
pip install openai
```

### Para otros modelos
Consulte la documentación de `agno` para dependencias específicas.

## Validaciones

Cada configurador implementa validaciones específicas:

### Validaciones Comunes (BaseAgentConfigurator)
- ✅ Modelo de agente requerido
- ✅ Nombre del agente requerido
- ✅ Instrucciones requeridas
- ✅ Temperature entre 0.0 y 1.0
- ✅ top_p entre 0.0 y 1.0
- ✅ max_tokens > 0

### Validaciones Específicas de Gemini
- ✅ Tenant configurado para "gemini"
- ✅ API Key presente y no vacío
- ✅ Modelo ID válido (opcional)
- ⚠️ Advertencia si max_tokens > 8192

## Extensibilidad

### Agregar un Nuevo Configurador

1. **Crear el configurador**:
```python
from .base_configurator import BaseAgentConfigurator

class MiNuevoConfigurator(BaseAgentConfigurator):
    def configure(self) -> Agent:
        self._validate_configuration()
        # Implementar configuración específica
        return Agent(...)

    def _validate_configuration(self):
        super()._validate_configuration()
        # Validaciones específicas
```

2. **Registrar en el factory**:
```python
# En agents/services/configurators/factory.py
_configurators = {
    'ollama': OllamaConfigurator,
    'gemini': GeminiConfigurator,
    'mi_modelo': MiNuevoConfigurator,  # ← Agregar aquí
}
```

3. **Actualizar TenantModel**:
```python
# En tenants/models.py - Agregar nueva opción
model = models.CharField(
    max_length=50,
    choices=[
        ("ollama", "OLLAMA"),
        ("gemini", "GEMINI"),
        ("mi_modelo", "MI_MODELO"),  # ← Agregar aquí
    ],
    default="ollama",
)
```

4. **Actualizar imports**:
```python
# En agents/services/configurators/__init__.py
from .mi_nuevo_configurator import MiNuevoConfigurator
```

## Manejo de Errores

```python
try:
    configurator = AgentConfiguratorFactory.create_configurator(agent_model)
    agent = configurator.configure()
except ValueError as e:
    print(f"Error de configuración: {e}")
except NotImplementedError as e:
    print(f"Funcionalidad no implementada: {e}")
except ImportError as e:
    print(f"Dependencia faltante: {e}")
```

## Ejemplos Prácticos

### Ejemplo 1: Agente Multi-modelo
```python
def create_agent_by_provider(provider: str):
    tenant = TenantModel.objects.get(model=provider)
    agent_model = AgentModel.objects.get(tenant=tenant)

    configurator = AgentConfiguratorFactory.create_configurator(agent_model)
    return configurator.configure()

# Uso - Solo modelos soportados
ollama_agent = create_agent_by_provider("ollama")
gemini_agent = create_agent_by_provider("gemini")
```

### Ejemplo 2: Configuración Dinámica
```python
def configure_agent_with_custom_settings(agent_model, **kwargs):
    configurator = AgentConfiguratorFactory.create_configurator(agent_model, **kwargs)

    # Configuraciones adicionales antes de crear el agente
    if hasattr(configurator, 'set_custom_options'):
        configurator.set_custom_options(kwargs)

    return configurator.configure()
```

## Testing

```python
def test_gemini_configurator():
    tenant = TenantModel(model="gemini", ai_token="test-key")
    agent = AgentModel(tenant=tenant, name="Test", instructions="Test")

    configurator = GeminiConfigurator(agent)

    # Test validaciones
    with pytest.raises(ValueError):
        agent.tenant.ai_token = ""
        configurator._validate_configuration()
```

## Próximas Mejoras

- [ ] Soporte para Claude (Anthropic)
- [ ] Configuración de parámetros avanzados por modelo
- [ ] Cache de configuraciones
- [ ] Configuración desde archivos JSON/YAML
- [ ] Métricas y logging detallado
