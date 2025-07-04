# Analysis Services

## Descripción General

Este directorio contiene los servicios de análisis de sentimientos implementados utilizando el framework **Agno** con modelo **Ollama**. Los servicios están diseñados con un patrón de herencia que permite reutilizar código común mientras mantiene la flexibilidad para diferentes tipos de análisis.

## Estructura del Directorio

```
analysis/services/
├── __init__.py                     # Exportaciones principales
├── base_sentiment_service.py       # Clase base abstracta
├── sentiment_message_service.py    # Servicio para mensajes individuales
├── sentiment_chat_service.py       # Servicio para chats completos
├── scripts/                        # Modelos de respuesta estructurada
│   ├── __init__.py
│   ├── sentiment_script.py         # Modelo base de respuesta
│   └── sentiment_chat_script.py    # Modelo específico para chats
└── README.md                       # Esta documentación
```

## Arquitectura de Servicios

### BaseSentimentService

Clase base abstracta que proporciona la funcionalidad común para todos los servicios de análisis de sentimientos.

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from agno.agent import Agent
from agno.models.ollama import Ollama

class BaseSentimentService(ABC):
    """
    Clase base abstracta para servicios de análisis de sentimientos.

    Proporciona la funcionalidad común para crear y configurar agentes
    de análisis de sentimientos utilizando el framework Agno.
    """

    def __init__(self):
        self.model = Ollama(id=IA_MODEL)

    @abstractmethod
    def get_agent_description(self) -> str:
        """Retorna la descripción específica del agente."""
        pass

    @abstractmethod
    def get_agent_instructions(self) -> str:
        """Retorna las instrucciones específicas del agente."""
        pass

    @abstractmethod
    def get_response_model(self) -> Any:
        """Retorna el modelo de respuesta estructurada."""
        pass

    def build_context(self, context: Optional[str] = None, **kwargs) -> str:
        """Construye el contexto para el análisis de sentimientos."""
        if context:
            return context
        return ""

    def create_agent(self, context: str, response_model: Any) -> Agent:
        """Crea y configura un agente de análisis de sentimientos."""
        return Agent(
            model=self.model,
            description=self.get_agent_description(),
            instructions=self.get_agent_instructions(),
            context=context,
            response_model=response_model,
        )

    def analyze_sentiment(self, text: str, context: str) -> Any:
        """Ejecuta el análisis de sentimiento."""
        response_model = self.get_response_model()
        agent = self.create_agent(context, response_model)

        response = agent.run(text)
        return response.content
```

#### Métodos Abstractos Requeridos

1. **`get_agent_description()`**: Descripción del agente de IA
2. **`get_agent_instructions()`**: Instrucciones específicas de análisis
3. **`get_response_model()`**: Modelo de respuesta estructurada

#### Métodos Heredados

- **`build_context()`**: Construcción de contexto (puede ser sobrescrito)
- **`create_agent()`**: Creación y configuración del agente
- **`analyze_sentiment()`**: Ejecución del análisis

## Servicios Implementados

### SentimentMessageService

Servicio especializado para análisis de mensajes individuales.

```python
class SentimentMessageService(BaseSentimentService):
    """
    Servicio para análisis de sentimientos de mensajes individuales.

    Utiliza un agente de IA para analizar el sentimiento de mensajes cortos
    basándose en el contexto proporcionado.
    """

    def get_agent_description(self) -> str:
        return "Eres un analista de los sentimientos de las frases enviadas por el usuario"

    def get_agent_instructions(self) -> str:
        return (
            "Analiza el sentimiento del mensaje del usuario y clasificalo como POSITIVO, NEGATIVO o NEUTRO. "
            "Proporciona una justificación para la clasificación."
        )

    def get_response_model(self) -> type:
        return SentimientScript

    @staticmethod
    def run(text: str, context: str) -> SentimientScript:
        """
        Ejecuta el análisis de sentimiento para un mensaje.

        Args:
            text: Texto del mensaje a analizar
            context: Contexto adicional para el análisis

        Returns:
            SentimientScript: Resultado del análisis con sentimiento, causa y log
        """
        service = SentimentMessageService()
        return service.analyze_sentiment(text, context)
```

**Características:**
- **Propósito**: Análisis de mensajes individuales
- **Contexto**: Simple, basado en parámetro proporcionado
- **Modelo de respuesta**: `SentimientScript`
- **Uso**: Análisis rápido de mensajes cortos

### SentimentChatService

Servicio especializado para análisis de chats completos con contexto enriquecido.

```python
class SentimentChatService(BaseSentimentService):
    """
    Servicio para análisis de sentimientos de chats completos.

    Utiliza un agente de IA configurado con tokens específicos del tenant
    para analizar el sentimiento de conversaciones completas.
    """

    def get_agent_description(self) -> str:
        return "Eres un analista de los sentimientos del chat enviado por el usuario"

    def get_agent_instructions(self) -> str:
        return (
            "Analiza el sentimiento del chat del usuario y clasificalo como POSITIVO, NEGATIVO o NEUTRO. "
            "Proporciona una justificación para la clasificación."
        )

    def get_response_model(self) -> type:
        return SentimentChatScript

    def build_context(self, context: str = None, sentiment_model: SentimentAgentModel = None) -> str:
        """
        Construye el contexto específico para análisis de chats con tokens del modelo.

        Args:
            context: Contexto base (no utilizado en esta implementación)
            sentiment_model: Modelo de sentimiento con tokens específicos

        Returns:
            str: Contexto formateado con ejemplos de tokens
        """
        if sentiment_model:
            return f"""
            ##Palabras de Ejemplo:
            Frases de sentimientos NEGATIVAS: {sentiment_model.negative_tokens}
            Frases de sentimientos POSITIVAS: {sentiment_model.positive_tokens}
            Frases de sentimientos NEUTRAS: {sentiment_model.neutral_tokens}
        """
        return ""

    @staticmethod
    def run(text: str, analyzer_name: str) -> SentimentChatScript:
        """
        Ejecuta el análisis de sentimiento para un chat completo.

        Args:
            text: Texto del chat a analizar
            analyzer_name: Nombre del agente de sentimiento a utilizar

        Returns:
            SentimentChatScript: Resultado del análisis con sentimiento, causa y log

        Raises:
            SentimentAgentModel.DoesNotExist: Si el analizador no existe
        """
        sentiment_model = SentimentAgentModel.objects.get(name=analyzer_name)

        service = SentimentChatService()
        context = service.build_context(sentiment_model=sentiment_model)

        return service.analyze_sentiment(text, context)
```

**Características:**
- **Propósito**: Análisis de chats completos
- **Contexto**: Enriquecido con tokens específicos del tenant
- **Modelo de respuesta**: `SentimentChatScript`
- **Integración**: Utiliza `SentimentAgentModel` para contexto personalizado

## Modelos de Respuesta (Scripts)

### SentimientScript

Modelo base para respuestas de análisis de sentimientos.

```python
from typing import Literal
from pydantic import BaseModel, Field

class SentimientScript(BaseModel):
    """
    Script base para análisis de sentimientos.

    Define la estructura común para respuestas de análisis de sentimientos.
    """
    sentimient: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"] = Field(
        ...,
        description="Clasifica el mensaje del usuario segun su sentimiento, en: POSITIVE, NEGATIVE o NEUTRAL",
        examples=["POSITIVE", "NEGATIVE", "NEUTRAL"],
    )
    cause: str = Field(
        ...,
        description="justifica la clasificacion del sentimiento",
        max_length=500
    )
    log: str = Field(
        ...,
        description="Log del analisis realizado, incluyendo el texto analizado y el sentimiento detectado",
        examples=["Analizado 55 caracteres de texto, sentimiento detectado: NEUTRO"],
        max_length=500,
    )
```

### SentimentChatScript

Modelo específico para análisis de chats que extiende el modelo base.

```python
from typing import Literal
from pydantic import Field

class SentimentChatScript(SentimientScript):
    """
    Script específico para análisis de sentimientos de chats completos.

    Extiende SentimientScript con configuraciones específicas para análisis de chat.
    """
    sentimient: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"] = Field(
        ...,
        description="Analiza totalmente el chat en: POSITIVE, NEGATIVE o NEUTRAL",
        examples=["POSITIVE", "NEGATIVE", "NEUTRAL"],
    )
```

## Integración con Modelos

### SentimentAgentModel

Los servicios integran con el modelo `SentimentAgentModel` que proporciona configuración específica por tenant:

```python
class SentimentAgentModel(AppModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    negative_tokens = models.TextField(
        help_text="Lista de tokens negativos, separados por comas."
    )
    positive_tokens = models.TextField(
        help_text="Lista de tokens positivos, separados por comas."
    )
    neutral_tokens = models.TextField(
        help_text="Lista de tokens neutrales, separados por comas."
    )
    tenant = models.ForeignKey(
        "tenants.TenantModel", on_delete=models.CASCADE, related_name="sentiment_agents"
    )
```

**Métodos útiles:**
- `get_positive_tokens_list()`: Lista de tokens positivos
- `get_negative_tokens_list()`: Lista de tokens negativos
- `get_neutral_tokens_list()`: Lista de tokens neutrales

## Ejemplos de Uso

### Análisis de Mensaje Individual

```python
from analysis.services import SentimentMessageService

# Análisis básico
result = SentimentMessageService.run(
    text="Estoy muy feliz con el servicio",
    context="Análisis de feedback de cliente"
)

print(f"Sentimiento: {result.sentimient}")
print(f"Justificación: {result.cause}")
print(f"Log: {result.log}")
```

### Análisis de Chat Completo

```python
from analysis.services import SentimentChatService

# Análisis con contexto específico del tenant
result = SentimentChatService.run(
    text="[Usuario]: Hola, tengo un problema\n[Agente]: ¿En qué puedo ayudarte?\n[Usuario]: Gracias por la ayuda",
    analyzer_name="mi_agente_sentimiento"
)

print(f"Sentimiento del chat: {result.sentimient}")
print(f"Análisis: {result.cause}")
```

### Uso en Views de Django

```python
from django.http import JsonResponse
from analysis.services import SentimentMessageService, SentimentChatService

def analyze_message_view(request):
    text = request.POST.get('text')
    context = request.POST.get('context', 'Análisis general')

    try:
        result = SentimentMessageService.run(text, context)
        return JsonResponse({
            'sentiment': result.sentimient,
            'cause': result.cause,
            'log': result.log
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def analyze_chat_view(request):
    text = request.POST.get('text')
    analyzer_name = request.POST.get('analyzer_name')

    try:
        result = SentimentChatService.run(text, analyzer_name)
        return JsonResponse({
            'sentiment': result.sentimient,
            'cause': result.cause,
            'log': result.log
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

## Configuración

### Settings Requeridos

```python
# main/settings.py
IA_MODEL = "llama3.1:8b"  # Modelo Ollama a utilizar
```

### Instalación de Dependencias

```bash
pip install agno
pip install ollama
```

## Beneficios de la Arquitectura

### 1. **Reutilización de Código**
- Lógica común centralizada en `BaseSentimentService`
- Evita duplicación de código entre servicios

### 2. **Consistencia**
- Interfaz uniforme para todos los servicios de sentimientos
- Patrones de respuesta estandarizados

### 3. **Mantenibilidad**
- Cambios centralizados en la clase base
- Fácil actualización de funcionalidad común

### 4. **Extensibilidad**
- Fácil adición de nuevos servicios de sentimientos
- Sobrescritura selectiva de métodos según necesidades

### 5. **Testing**
- Tests comunes para funcionalidad base
- Tests específicos para cada implementación

## Mejores Prácticas

### 1. **Manejo de Errores**
```python
try:
    result = SentimentMessageService.run(text, context)
except Exception as e:
    logger.error(f"Error en análisis de sentimiento: {e}")
    # Manejar error apropiadamente
```

### 2. **Logging**
```python
import logging

logger = logging.getLogger(__name__)

# En los servicios
logger.info(f"Iniciando análisis de sentimiento para texto de {len(text)} caracteres")
logger.debug(f"Contexto utilizado: {context}")
```

### 3. **Validación de Entrada**
```python
def validate_text_input(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("El texto no puede estar vacío")

    if len(text) > 10000:
        raise ValueError("El texto es demasiado largo para análisis")

    return text.strip()
```

### 4. **Caching** (Recomendado)
```python
from django.core.cache import cache
import hashlib

def get_sentiment_cache_key(text: str, context: str) -> str:
    """Genera clave única para cache de análisis."""
    content = f"{text}:{context}"
    return f"sentiment:{hashlib.md5(content.encode()).hexdigest()}"

# En el servicio
cache_key = get_sentiment_cache_key(text, context)
cached_result = cache.get(cache_key)

if cached_result:
    return cached_result

result = self.analyze_sentiment(text, context)
cache.set(cache_key, result, timeout=3600)  # 1 hora
```

## Extensión del Sistema

### Crear Nuevo Servicio de Sentimientos

```python
class CustomSentimentService(BaseSentimentService):
    """Servicio personalizado para análisis específico."""

    def get_agent_description(self) -> str:
        return "Descripción específica del agente personalizado"

    def get_agent_instructions(self) -> str:
        return "Instrucciones específicas para el análisis personalizado"

    def get_response_model(self) -> type:
        return CustomSentimentScript

    def build_context(self, context: str = None, **kwargs) -> str:
        # Lógica personalizada para construir contexto
        return super().build_context(context, **kwargs)

    @staticmethod
    def run(text: str, custom_param: str) -> CustomSentimentScript:
        service = CustomSentimentService()
        context = service.build_context(custom_param=custom_param)
        return service.analyze_sentiment(text, context)
```

### Crear Nuevo Modelo de Respuesta

```python
class CustomSentimentScript(SentimientScript):
    """Modelo personalizado con campos adicionales."""

    confidence_score: float = Field(
        ...,
        description="Puntuación de confianza del análisis (0-1)",
        ge=0.0,
        le=1.0
    )

    keywords: List[str] = Field(
        default_factory=list,
        description="Palabras clave identificadas en el análisis"
    )
```

## Monitoreo y Métricas

### Métricas Recomendadas

1. **Tiempo de procesamiento** por análisis
2. **Tasa de errores** en análisis
3. **Distribución de sentimientos** detectados
4. **Uso de cache** (hit rate)
5. **Volumen de análisis** por período

### Implementación de Métricas

```python
import time
from django.core.cache import cache

class SentimentMetrics:
    @staticmethod
    def track_analysis(service_name: str, duration: float, success: bool):
        """Registra métricas de análisis."""
        timestamp = int(time.time())
        metric_key = f"sentiment_metrics:{service_name}:{timestamp}"

        cache.set(metric_key, {
            'duration': duration,
            'success': success,
            'timestamp': timestamp
        }, timeout=86400)  # 24 horas

    @staticmethod
    def get_metrics_summary(service_name: str, hours: int = 24) -> dict:
        """Obtiene resumen de métricas."""
        # Implementar lógica de agregación de métricas
        pass
```

## Troubleshooting

### Errores Comunes

1. **"SentimentAgentModel.DoesNotExist"**
   - Verificar que el agente existe en la base de datos
   - Confirmar que el nombre del agente es correcto

2. **"Connection refused to Ollama"**
   - Verificar que Ollama está ejecutándose
   - Confirmar la configuración del modelo en settings

3. **"Response model validation error"**
   - Verificar que el modelo de respuesta coincide con la salida del agente
   - Revisar la configuración del agente

### Debugging

```python
import logging

# Habilitar logging detallado
logging.basicConfig(level=logging.DEBUG)

# En desarrollo
DEBUG_SENTIMENT = True

if DEBUG_SENTIMENT:
    print(f"Contexto generado: {context}")
    print(f"Texto a analizar: {text[:100]}...")
```
