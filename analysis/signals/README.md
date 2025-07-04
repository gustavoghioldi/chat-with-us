# Signals - Analysis

## Descripción General
Este directorio contiene las señales (signals) que manejan eventos automáticos relacionados con el análisis de datos. Las señales permiten que el sistema reaccione automáticamente a cambios en otros módulos y ejecute análisis cuando sea necesario.

## Señales Principales

### new_chat_text_receiver.py
Receptor principal que se activa cuando se crean nuevos mensajes de chat para procesarlos automáticamente.

#### Funcionalidades:
- **Detección automática**: Se activa al crear/actualizar mensajes
- **Análisis asíncrono**: Programa análisis en background
- **Filtrado inteligente**: Solo procesa mensajes que requieren análisis
- **Gestión de errores**: Maneja errores sin interrumpir el flujo principal

#### Implementación:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from chats.models import MessageModel
from analysis.tasks import analyze_message_sentiment
import logging

logger = logging.getLogger('analysis.signals')

@receiver(post_save, sender=MessageModel)
def new_chat_text_receiver(sender, instance, created, **kwargs):
    """
    Receptor que se activa cuando se crea o actualiza un mensaje de chat
    para programar su análisis de sentimiento automáticamente.
    """
    # Solo procesar mensajes nuevos o actualizados con contenido
    if not created and not kwargs.get('update_fields'):
        return

    # Filtrar mensajes que necesitan análisis
    if not should_analyze_message(instance):
        return

    try:
        # Verificar si ya existe análisis para este mensaje
        from analysis.models import SentimentChatModel

        existing_analysis = SentimentChatModel.objects.filter(
            message=instance,
            tenant=instance.chat.tenant
        ).exists()

        # Solo analizar si no existe análisis previo o se fuerza re-análisis
        if not existing_analysis or kwargs.get('force_reanalysis', False):
            logger.info(
                f"Programando análisis de sentimiento para mensaje {instance.id}"
            )

            # Programar análisis asíncrono
            analyze_message_sentiment.delay(
                message_id=instance.id,
                tenant_id=instance.chat.tenant.id,
                priority='normal'
            )

            # Opcional: programar análisis de contexto completo del chat
            if should_analyze_full_conversation(instance):
                from analysis.tasks import analyze_chat_conversation
                analyze_chat_conversation.delay(
                    chat_id=instance.chat.id,
                    tenant_id=instance.chat.tenant.id
                )

    except Exception as e:
        logger.error(
            f"Error programando análisis para mensaje {instance.id}: {str(e)}",
            exc_info=True
        )

        # No propagar el error para no interrumpir el flujo principal
        pass

def should_analyze_message(message):
    """
    Determina si un mensaje debe ser analizado.
    """
    # No analizar mensajes vacíos
    if not message.content or not message.content.strip():
        return False

    # No analizar mensajes del sistema
    if message.sender_type == 'system':
        return False

    # No analizar mensajes muy cortos (menos de 3 palabras)
    if len(message.content.split()) < 3:
        return False

    # Verificar si el tenant tiene análisis habilitado
    if hasattr(message.chat, 'tenant') and message.chat.tenant:
        tenant_settings = getattr(message.chat.tenant, 'analysis_settings', {})
        if not tenant_settings.get('sentiment_analysis_enabled', True):
            return False

    return True

def should_analyze_full_conversation(message):
    """
    Determina si se debe analizar la conversación completa.
    """
    # Analizar conversación cada N mensajes
    message_count = message.chat.messages.count()
    analysis_interval = 10  # Cada 10 mensajes

    return message_count % analysis_interval == 0
```

### agent_interaction_receiver.py
Receptor para análisis de interacciones con agentes.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from chats.models import MessageModel
from agents.models import AgentModel
from analysis.tasks import analyze_agent_interaction

@receiver(post_save, sender=MessageModel)
def agent_interaction_receiver(sender, instance, created, **kwargs):
    """
    Analiza interacciones específicas entre usuarios y agentes.
    """
    if not created:
        return

    # Solo procesar mensajes de agentes
    if instance.sender_type != 'agent':
        return

    try:
        # Buscar el mensaje del usuario inmediatamente anterior
        user_message = MessageModel.objects.filter(
            chat=instance.chat,
            sender_type='user',
            created_at__lt=instance.created_at
        ).order_by('-created_at').first()

        if user_message:
            logger.info(
                f"Programando análisis de interacción agente-usuario: "
                f"user_msg={user_message.id}, agent_msg={instance.id}"
            )

            # Programar análisis de la interacción
            analyze_agent_interaction.delay(
                user_message_id=user_message.id,
                agent_message_id=instance.id,
                tenant_id=instance.chat.tenant.id
            )

    except Exception as e:
        logger.error(
            f"Error programando análisis de interacción: {str(e)}",
            exc_info=True
        )
```

### chat_completion_receiver.py
Receptor para análisis cuando se completa un chat.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from chats.models import ChatModel
from analysis.tasks import generate_chat_summary_report

@receiver(post_save, sender=ChatModel)
def chat_completion_receiver(sender, instance, created, **kwargs):
    """
    Se activa cuando un chat cambia de estado, especialmente al completarse.
    """
    if created:
        return

    # Verificar si el chat se marcó como completado
    if instance.status == 'completed' and 'status' in (kwargs.get('update_fields', [])):
        logger.info(f"Chat {instance.id} completado, generando análisis final")

        try:
            # Generar reporte final del chat
            generate_chat_summary_report.delay(
                chat_id=instance.id,
                tenant_id=instance.tenant.id
            )

            # Actualizar métricas del agente si aplicable
            if hasattr(instance, 'agent') and instance.agent:
                from analysis.tasks import update_agent_performance_metrics
                update_agent_performance_metrics.delay(
                    agent_id=instance.agent.id,
                    tenant_id=instance.tenant.id
                )

        except Exception as e:
            logger.error(
                f"Error generando análisis final de chat {instance.id}: {str(e)}",
                exc_info=True
            )
```

## Señales de Configuración

### analysis_config_receiver.py
Receptor para cambios en configuración de análisis.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from tenants.models import TenantModel
from analysis.services import AnalysisCacheService

@receiver(post_save, sender=TenantModel)
def analysis_config_receiver(sender, instance, created, **kwargs):
    """
    Se activa cuando cambia la configuración de análisis de un tenant.
    """
    if created:
        return

    # Verificar si cambió configuración de análisis
    if 'analysis_settings' in (kwargs.get('update_fields', [])):
        logger.info(f"Configuración de análisis actualizada para tenant {instance.id}")

        try:
            # Invalidar caché de análisis del tenant
            cache_service = AnalysisCacheService()
            cache_service.invalidate_tenant_cache(instance.id)

            # Si se deshabilitó el análisis, pausar tareas pendientes
            analysis_settings = getattr(instance, 'analysis_settings', {})
            if not analysis_settings.get('sentiment_analysis_enabled', True):
                from analysis.tasks import pause_tenant_analysis_tasks
                pause_tenant_analysis_tasks.delay(instance.id)

        except Exception as e:
            logger.error(
                f"Error actualizando configuración de análisis: {str(e)}",
                exc_info=True
            )
```

## Emisores de Señales Personalizadas

### custom_signals.py
Definición de señales personalizadas para el módulo de análisis.

```python
import django.dispatch

# Señal emitida cuando se completa un análisis de sentimiento
sentiment_analysis_completed = django.dispatch.Signal()

# Señal emitida cuando se detecta un sentimiento muy negativo
negative_sentiment_detected = django.dispatch.Signal()

# Señal emitida cuando se genera un reporte de análisis
analysis_report_generated = django.dispatch.Signal()

# Señal emitida cuando se detecta una anomalía en los datos
analysis_anomaly_detected = django.dispatch.Signal()
```

### custom_signal_receivers.py
Receptores para señales personalizadas.

```python
from django.dispatch import receiver
from .custom_signals import (
    sentiment_analysis_completed,
    negative_sentiment_detected,
    analysis_report_generated,
    analysis_anomaly_detected
)

@receiver(sentiment_analysis_completed)
def handle_sentiment_analysis_completed(sender, **kwargs):
    """
    Maneja la finalización de un análisis de sentimiento.
    """
    analysis_result = kwargs.get('analysis_result')
    message_id = kwargs.get('message_id')

    logger.info(f"Análisis completado para mensaje {message_id}")

    # Verificar si requiere alertas
    if analysis_result.get('sentiment_score', 0) < -0.7:
        negative_sentiment_detected.send(
            sender=sender,
            analysis_result=analysis_result,
            message_id=message_id
        )

@receiver(negative_sentiment_detected)
def handle_negative_sentiment_detected(sender, **kwargs):
    """
    Maneja detección de sentimiento muy negativo.
    """
    analysis_result = kwargs.get('analysis_result')
    message_id = kwargs.get('message_id')

    logger.warning(f"Sentimiento muy negativo detectado en mensaje {message_id}")

    try:
        # Notificar al equipo de soporte
        from analysis.tasks import send_negative_sentiment_alert
        send_negative_sentiment_alert.delay(
            message_id=message_id,
            sentiment_score=analysis_result.get('sentiment_score'),
            confidence=analysis_result.get('confidence')
        )

        # Marcar para posible escalamiento
        from chats.models import MessageModel
        message = MessageModel.objects.get(id=message_id)
        message.requires_attention = True
        message.save(update_fields=['requires_attention'])

    except Exception as e:
        logger.error(f"Error manejando sentimiento negativo: {str(e)}")

@receiver(analysis_report_generated)
def handle_analysis_report_generated(sender, **kwargs):
    """
    Maneja la generación de reportes de análisis.
    """
    report_id = kwargs.get('report_id')
    report_type = kwargs.get('report_type')
    tenant_id = kwargs.get('tenant_id')

    logger.info(f"Reporte {report_type} generado: {report_id}")

    try:
        # Notificar a usuarios relevantes
        from analysis.tasks import notify_report_completion
        notify_report_completion.delay(
            report_id=report_id,
            report_type=report_type,
            tenant_id=tenant_id
        )

    except Exception as e:
        logger.error(f"Error notificando reporte generado: {str(e)}")
```

## Configuración de Señales

### signal_configuration.py
Configuración y registro de señales.

```python
from django.apps import AppConfig

class AnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analysis'

    def ready(self):
        """
        Registra las señales cuando la app está lista.
        """
        # Importar receptores para registrarlos
        from . import signals

        # Configurar logging para señales
        import logging
        logger = logging.getLogger('analysis.signals')
        logger.info("Señales de análisis registradas")
```

## Gestión de Rendimiento

### signal_performance.py
Optimizaciones y gestión de rendimiento de señales.

```python
from django.db import transaction
from django.core.cache import cache
import time

def rate_limited_signal(cache_key, rate_limit_seconds=60):
    """
    Decorador para limitar la frecuencia de ejecución de señales.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Verificar rate limit
            last_execution = cache.get(cache_key)
            current_time = time.time()

            if last_execution and (current_time - last_execution) < rate_limit_seconds:
                logger.debug(f"Señal {func.__name__} limitada por rate limit")
                return

            # Ejecutar función
            result = func(*args, **kwargs)

            # Actualizar timestamp de última ejecución
            cache.set(cache_key, current_time, rate_limit_seconds * 2)

            return result

        return wrapper
    return decorator

@rate_limited_signal('analysis:bulk_sentiment_analysis', 300)  # 5 minutos
def bulk_sentiment_analysis_signal(sender, **kwargs):
    """
    Señal con rate limiting para análisis en lote.
    """
    # Implementación de análisis en lote
    pass
```

## Debugging y Monitoreo

### signal_monitoring.py
Herramientas para monitorear señales.

```python
import logging
from functools import wraps
from django.utils import timezone

logger = logging.getLogger('analysis.signals.monitoring')

def monitor_signal_execution(signal_name):
    """
    Decorador para monitorear ejecución de señales.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timezone.now()

            try:
                result = func(*args, **kwargs)

                execution_time = (timezone.now() - start_time).total_seconds()
                logger.info(
                    f"Señal {signal_name} ejecutada exitosamente en {execution_time:.3f}s"
                )

                # Registrar métricas
                from analysis.models import SignalExecutionMetric
                SignalExecutionMetric.objects.create(
                    signal_name=signal_name,
                    execution_time=execution_time,
                    success=True,
                    timestamp=start_time
                )

                return result

            except Exception as e:
                execution_time = (timezone.now() - start_time).total_seconds()
                logger.error(
                    f"Error en señal {signal_name} después de {execution_time:.3f}s: {str(e)}",
                    exc_info=True
                )

                # Registrar error
                SignalExecutionMetric.objects.create(
                    signal_name=signal_name,
                    execution_time=execution_time,
                    success=False,
                    error_message=str(e),
                    timestamp=start_time
                )

                raise

        return wrapper
    return decorator
```

## Mejores Prácticas

### Performance
1. **Ejecución Asíncrona**: Usar Celery para tareas pesadas
2. **Rate Limiting**: Limitar frecuencia de señales costosas
3. **Lazy Loading**: Evitar consultas innecesarias en señales
4. **Batch Processing**: Agrupar operaciones cuando sea posible

### Confiabilidad
1. **Error Handling**: Manejar errores sin interrumpir flujo principal
2. **Idempotencia**: Asegurar que señales sean idempotentes
3. **Logging**: Registrar todas las ejecuciones importantes
4. **Monitoring**: Monitorear rendimiento y errores

### Mantenimiento
1. **Documentación**: Documentar propósito de cada señal
2. **Testing**: Probar señales aisladamente
3. **Cleanup**: Limpiar señales obsoletas regularmente
4. **Versioning**: Versionar cambios en señales críticas
