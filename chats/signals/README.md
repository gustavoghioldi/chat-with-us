# Señales de Chats

## Descripción General
Este directorio contiene las señales (signals) del módulo de chats. Las señales permiten ejecutar código automáticamente cuando ocurren ciertos eventos en el sistema, como la creación de nuevos mensajes o cambios en los chats.

## Estructura de Archivos

### `chat_post_save_receiver.py`
Receptor de señales que se ejecuta después de guardar un chat.

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from chats.models import Chat
from analysis.tasks import analyze_chat_sentiment
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Chat)
def chat_post_save_receiver(sender, instance, created, **kwargs):
    """
    Receptor que se ejecuta después de guardar un chat.

    Args:
        sender: El modelo que envió la señal (Chat)
        instance: La instancia del chat que fue guardado
        created: Boolean indicando si el chat fue creado o actualizado
        **kwargs: Argumentos adicionales
    """

    if created:
        logger.info(f"New chat created: {instance.id}")

        # Inicializar configuración del chat
        initialize_chat_settings(instance)

        # Notificar a otros sistemas
        notify_chat_created(instance)

        # Registrar métricas
        record_chat_metrics(instance)

    else:
        logger.info(f"Chat updated: {instance.id}")

        # Procesar actualizaciones
        process_chat_update(instance)

def initialize_chat_settings(chat):
    """
    Inicializa configuraciones por defecto para un nuevo chat.
    """
    try:
        # Configurar agente por defecto si no está asignado
        if not chat.agent:
            from agents.models import AgentModel
            default_agent = AgentModel.objects.filter(
                tenant=chat.tenant,
                is_default=True
            ).first()

            if default_agent:
                chat.agent = default_agent
                chat.save(update_fields=['agent'])

        # Configurar configuraciones iniciales
        chat.settings = {
            'auto_save': True,
            'sentiment_analysis': True,
            'notifications': True
        }
        chat.save(update_fields=['settings'])

        logger.info(f"Chat settings initialized for chat {chat.id}")

    except Exception as e:
        logger.error(f"Error initializing chat settings: {e}")

def notify_chat_created(chat):
    """
    Notifica a otros sistemas sobre la creación de un nuevo chat.
    """
    try:
        # Enviar notificación al administrador del tenant
        from notifications.services import NotificationService
        notification_service = NotificationService()

        notification_service.send_notification(
            recipient=chat.tenant.admin,
            message=f"New chat created by {chat.user.username}",
            notification_type='chat_created'
        )

        # Registrar evento en el sistema de auditoría
        from audit.services import AuditService
        audit_service = AuditService()

        audit_service.log_event(
            action='chat_created',
            user=chat.user,
            tenant=chat.tenant,
            object_type='chat',
            object_id=chat.id
        )

    except Exception as e:
        logger.error(f"Error notifying chat creation: {e}")

def record_chat_metrics(chat):
    """
    Registra métricas del nuevo chat.
    """
    try:
        from metrics.services import MetricsService
        metrics_service = MetricsService()

        metrics_service.increment_counter(
            metric_name='chats_created',
            labels={
                'tenant_id': str(chat.tenant.id),
                'agent_id': str(chat.agent.id) if chat.agent else 'none'
            }
        )

        metrics_service.set_gauge(
            metric_name='active_chats',
            value=Chat.objects.filter(tenant=chat.tenant, is_active=True).count(),
            labels={'tenant_id': str(chat.tenant.id)}
        )

    except Exception as e:
        logger.error(f"Error recording chat metrics: {e}")

def process_chat_update(chat):
    """
    Procesa actualizaciones del chat.
    """
    try:
        # Verificar cambios importantes
        if chat.tracker.has_changed('is_active'):
            if chat.is_active:
                logger.info(f"Chat {chat.id} activated")
                # Lógica para activación
            else:
                logger.info(f"Chat {chat.id} deactivated")
                # Lógica para desactivación

        if chat.tracker.has_changed('agent'):
            logger.info(f"Chat {chat.id} agent changed to {chat.agent}")
            # Actualizar configuraciones del agente
            update_agent_settings(chat)

    except Exception as e:
        logger.error(f"Error processing chat update: {e}")

def update_agent_settings(chat):
    """
    Actualiza configuraciones cuando cambia el agente.
    """
    if chat.agent:
        # Aplicar configuraciones del nuevo agente
        chat.settings.update({
            'temperature': chat.agent.temperature,
            'max_tokens': chat.agent.max_tokens,
            'model_provider': chat.agent.model_provider
        })
        chat.save(update_fields=['settings'])
```

### `content_chat_emit.py`
Emisor de señales para contenido de chat.

```python
from django.dispatch import Signal
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from chats.models import Message
import logging

logger = logging.getLogger(__name__)

# Señales personalizadas
message_analyzed = Signal()
conversation_completed = Signal()
chat_archived = Signal()

@receiver(post_save, sender=Message)
def message_post_save_receiver(sender, instance, created, **kwargs):
    """
    Receptor que se ejecuta después de guardar un mensaje.
    """
    if created:
        logger.info(f"New message created: {instance.id}")

        # Procesar mensaje asíncronamente
        process_new_message.delay(instance.id)

        # Emitir señal personalizada
        emit_message_signals(instance)

        # Actualizar estado del chat
        update_chat_activity(instance.chat)

def process_new_message(message_id):
    """
    Procesa un nuevo mensaje de forma asíncrona.
    """
    try:
        from celery import shared_task

        @shared_task
        def process_message_task(msg_id):
            message = Message.objects.get(id=msg_id)

            # Análisis de sentimientos
            if message.sender == 'user':
                from analysis.tasks import analyze_message_sentiment
                analyze_message_sentiment.delay(message.id)

            # Generar respuesta automática si es necesario
            if should_generate_auto_response(message):
                generate_auto_response.delay(message.id)

            # Actualizar métricas
            update_message_metrics(message)

        process_message_task.delay(message_id)

    except Exception as e:
        logger.error(f"Error processing new message: {e}")

def emit_message_signals(message):
    """
    Emite señales personalizadas para el mensaje.
    """
    try:
        # Emitir señal de análisis completado
        message_analyzed.send(
            sender=Message,
            message=message,
            timestamp=timezone.now()
        )

        # Verificar si la conversación está completa
        if is_conversation_complete(message.chat):
            conversation_completed.send(
                sender=Message,
                chat=message.chat,
                final_message=message
            )

    except Exception as e:
        logger.error(f"Error emitting message signals: {e}")

def update_chat_activity(chat):
    """
    Actualiza la actividad del chat.
    """
    try:
        from django.utils import timezone

        chat.last_activity = timezone.now()
        chat.message_count = chat.messages.count()
        chat.save(update_fields=['last_activity', 'message_count'])

        # Marcar chat como activo si no lo está
        if not chat.is_active:
            chat.is_active = True
            chat.save(update_fields=['is_active'])

    except Exception as e:
        logger.error(f"Error updating chat activity: {e}")

def should_generate_auto_response(message):
    """
    Determina si se debe generar una respuesta automática.
    """
    # Verificar si el mensaje es del usuario
    if message.sender != 'user':
        return False

    # Verificar si el chat tiene auto-respuesta habilitada
    if not message.chat.settings.get('auto_response', True):
        return False

    # Verificar si el agente está disponible
    if not message.chat.agent or not message.chat.agent.is_active:
        return False

    return True

def generate_auto_response(message_id):
    """
    Genera una respuesta automática para el mensaje.
    """
    try:
        from celery import shared_task
        from agents.services.agent_service import AgentService

        @shared_task
        def generate_response_task(msg_id):
            message = Message.objects.get(id=msg_id)
            agent_service = AgentService()

            response = agent_service.generate_response(
                agent_id=message.chat.agent.id,
                message=message.content,
                context={
                    'chat_id': message.chat.id,
                    'user_id': message.chat.user.id
                }
            )

            # Crear mensaje de respuesta
            Message.objects.create(
                chat=message.chat,
                content=response,
                sender='agent',
                in_response_to=message
            )

        generate_response_task.delay(message_id)

    except Exception as e:
        logger.error(f"Error generating auto response: {e}")

def is_conversation_complete(chat):
    """
    Determina si una conversación está completa.
    """
    # Verificar si el chat ha sido marcado como completo
    if chat.status == 'completed':
        return True

    # Verificar inactividad
    from django.utils import timezone
    from datetime import timedelta

    if chat.last_activity:
        inactive_time = timezone.now() - chat.last_activity
        if inactive_time > timedelta(hours=24):
            return True

    return False

def update_message_metrics(message):
    """
    Actualiza métricas del mensaje.
    """
    try:
        from metrics.services import MetricsService
        metrics_service = MetricsService()

        metrics_service.increment_counter(
            metric_name='messages_created',
            labels={
                'sender': message.sender,
                'chat_id': str(message.chat.id),
                'tenant_id': str(message.chat.tenant.id)
            }
        )

        # Métricas de longitud del mensaje
        metrics_service.observe_histogram(
            metric_name='message_length',
            value=len(message.content),
            labels={
                'sender': message.sender,
                'tenant_id': str(message.chat.tenant.id)
            }
        )

    except Exception as e:
        logger.error(f"Error updating message metrics: {e}")

# Receptores para señales personalizadas
@receiver(message_analyzed)
def handle_message_analyzed(sender, message, **kwargs):
    """
    Maneja la señal de mensaje analizado.
    """
    logger.info(f"Message {message.id} analysis completed")

    # Procesar resultados del análisis
    process_analysis_results(message)

@receiver(conversation_completed)
def handle_conversation_completed(sender, chat, final_message, **kwargs):
    """
    Maneja la señal de conversación completada.
    """
    logger.info(f"Conversation completed for chat {chat.id}")

    # Archivar conversación
    archive_conversation(chat)

    # Generar resumen
    generate_conversation_summary(chat)

def process_analysis_results(message):
    """
    Procesa los resultados del análisis de mensaje.
    """
    try:
        # Obtener resultados del análisis
        from analysis.models import SentimentChatModel

        sentiment = SentimentChatModel.objects.filter(
            message=message
        ).first()

        if sentiment:
            # Actualizar configuraciones basadas en el sentimiento
            if sentiment.sentiment == 'negative':
                # Activar escalado si es necesario
                trigger_escalation(message)

            # Ajustar respuestas futuras del agente
            adjust_agent_behavior(message.chat, sentiment)

    except Exception as e:
        logger.error(f"Error processing analysis results: {e}")

def trigger_escalation(message):
    """
    Activa escalado para mensajes negativos.
    """
    try:
        from notifications.services import NotificationService
        notification_service = NotificationService()

        notification_service.send_escalation_alert(
            chat=message.chat,
            message=message,
            reason='negative_sentiment'
        )

    except Exception as e:
        logger.error(f"Error triggering escalation: {e}")

def adjust_agent_behavior(chat, sentiment):
    """
    Ajusta el comportamiento del agente basado en el sentimiento.
    """
    try:
        if sentiment.sentiment == 'negative':
            # Usar tono más empático
            chat.agent_settings = {
                'tone': 'empathetic',
                'response_style': 'supportive'
            }
        elif sentiment.sentiment == 'positive':
            # Mantener tono positivo
            chat.agent_settings = {
                'tone': 'friendly',
                'response_style': 'enthusiastic'
            }

        chat.save(update_fields=['agent_settings'])

    except Exception as e:
        logger.error(f"Error adjusting agent behavior: {e}")

def archive_conversation(chat):
    """
    Archiva una conversación completada.
    """
    try:
        chat.status = 'archived'
        chat.archived_at = timezone.now()
        chat.save(update_fields=['status', 'archived_at'])

        # Emitir señal de archivado
        chat_archived.send(
            sender=Chat,
            chat=chat,
            archived_at=chat.archived_at
        )

    except Exception as e:
        logger.error(f"Error archiving conversation: {e}")

def generate_conversation_summary(chat):
    """
    Genera un resumen de la conversación.
    """
    try:
        from analysis.services import ConversationSummaryService
        summary_service = ConversationSummaryService()

        summary_service.generate_summary(chat.id)

    except Exception as e:
        logger.error(f"Error generating conversation summary: {e}")
```

## Configuración de Señales

### Registro de Señales
```python
# apps.py
from django.apps import AppConfig

class ChatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chats'

    def ready(self):
        import chats.signals.chat_post_save_receiver
        import chats.signals.content_chat_emit
```

### Señales Personalizadas
```python
from django.dispatch import Signal

# Definir señales personalizadas
message_analyzed = Signal()
conversation_completed = Signal()
chat_archived = Signal()
escalation_triggered = Signal()

# Usar señales personalizadas
def send_custom_signal():
    message_analyzed.send(
        sender=Message,
        message=message_instance,
        analysis_results=results
    )
```

## Casos de Uso

### 1. Análisis Automático de Sentimientos
```python
@receiver(post_save, sender=Message)
def trigger_sentiment_analysis(sender, instance, created, **kwargs):
    if created and instance.sender == 'user':
        # Analizar sentimiento del mensaje
        analyze_message_sentiment.delay(instance.id)
```

### 2. Notificaciones en Tiempo Real
```python
@receiver(post_save, sender=Message)
def send_realtime_notification(sender, instance, created, **kwargs):
    if created:
        # Enviar notificación WebSocket
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"chat_{instance.chat.id}",
            {
                'type': 'chat_message',
                'message': MessageSerializer(instance).data
            }
        )
```

### 3. Métricas y Auditoría
```python
@receiver(post_save, sender=Chat)
def log_chat_audit(sender, instance, created, **kwargs):
    if created:
        # Registrar evento de auditoría
        from audit.models import AuditLog
        AuditLog.objects.create(
            action='chat_created',
            user=instance.user,
            object_type='chat',
            object_id=instance.id,
            details={'agent': instance.agent.name if instance.agent else None}
        )
```

## Manejo de Errores

### Manejo Robusto de Excepciones
```python
@receiver(post_save, sender=Message)
def safe_signal_handler(sender, instance, created, **kwargs):
    try:
        # Lógica principal
        process_message(instance)
    except Exception as e:
        logger.error(f"Error in signal handler: {e}")

        # Opcional: reintentarlo más tarde
        retry_signal_processing.delay(instance.id)
```

### Logging Detallado
```python
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Chat)
def logged_signal_handler(sender, instance, created, **kwargs):
    logger.info(f"Processing chat signal: {instance.id}, created: {created}")

    try:
        # Lógica del handler
        pass
    except Exception as e:
        logger.error(f"Signal handler failed: {e}", exc_info=True)
```

## Testing

### Test de Señales
```python
from django.test import TestCase
from django.test.utils import override_settings
from unittest.mock import patch

class ChatSignalsTestCase(TestCase):
    @patch('chats.signals.chat_post_save_receiver.initialize_chat_settings')
    def test_chat_creation_signal(self, mock_initialize):
        # Crear chat
        chat = Chat.objects.create(
            title="Test Chat",
            user=self.user
        )

        # Verificar que la señal fue procesada
        mock_initialize.assert_called_once_with(chat)

    def test_message_creation_signal(self):
        with patch('chats.signals.content_chat_emit.process_new_message') as mock_process:
            message = Message.objects.create(
                chat=self.chat,
                content="Test message",
                sender='user'
            )

            mock_process.delay.assert_called_once_with(message.id)
```

## Mejores Prácticas

1. **Manejo de Errores**: Siempre manejar excepciones en los receptores
2. **Logging**: Registrar eventos importantes para debugging
3. **Asíncrono**: Usar Celery para procesamiento pesado
4. **Idempotencia**: Asegurar que las señales puedan ejecutarse múltiples veces
5. **Testing**: Escribir tests para verificar comportamiento de señales
6. **Documentación**: Documentar qué hace cada señal

## Monitoreo

### Métricas de Señales
```python
from functools import wraps
import time

def monitor_signal(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            # Registrar éxito
            return result
        except Exception as e:
            # Registrar error
            raise
        finally:
            duration = time.time() - start_time
            # Registrar duración
    return wrapper

@monitor_signal
@receiver(post_save, sender=Message)
def monitored_signal_handler(sender, instance, created, **kwargs):
    # Lógica del handler
    pass
```

## Configuración Avanzada

### Señales Condicionales
```python
@receiver(post_save, sender=Chat)
def conditional_signal_handler(sender, instance, created, **kwargs):
    # Solo procesar en ciertos ambientes
    if settings.ENVIRONMENT == 'production':
        process_production_logic(instance)
    elif settings.ENVIRONMENT == 'development':
        process_development_logic(instance)
```

### Desconexión Temporal
```python
from django.db.models.signals import post_save

def temporarily_disconnect_signals():
    """
    Desconecta temporalmente las señales para operaciones masivas.
    """
    post_save.disconnect(chat_post_save_receiver, sender=Chat)
    try:
        # Operaciones masivas
        yield
    finally:
        post_save.connect(chat_post_save_receiver, sender=Chat)
```
