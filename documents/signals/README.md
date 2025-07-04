# Señales de Documentos

## Descripción General
Este directorio contiene las señales (signals) del módulo de documentos. Las señales se ejecutan automáticamente cuando ocurren eventos relacionados con documentos, como creación, actualización, eliminación o cambios en la base de conocimiento.

## Estructura de Archivos

### `handle_knowledge_changes.py`
Maneja los cambios en la base de conocimiento cuando se modifican documentos.

```python
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from documents.models import Document
from knowledge.models import KnowledgeBase
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Document)
def document_post_save_handler(sender, instance, created, **kwargs):
    """
    Maneja eventos después de guardar un documento.

    Args:
        sender: El modelo que envió la señal (Document)
        instance: La instancia del documento
        created: Boolean indicando si fue creado o actualizado
        **kwargs: Argumentos adicionales
    """

    if created:
        logger.info(f"New document created: {instance.title} ({instance.id})")

        # Procesar nuevo documento
        process_new_document(instance)

        # Actualizar índices de búsqueda
        update_search_indexes(instance)

        # Notificar a sistemas relacionados
        notify_document_created(instance)

        # Registrar métricas
        record_document_metrics(instance, 'created')

    else:
        logger.info(f"Document updated: {instance.title} ({instance.id})")

        # Procesar actualización
        process_document_update(instance)

        # Verificar cambios importantes
        handle_significant_changes(instance)

def process_new_document(document):
    """
    Procesa un nuevo documento.
    """
    try:
        # Extraer y procesar contenido
        from documents.services import DocumentProcessingService
        processing_service = DocumentProcessingService()

        # Procesar contenido asíncronamente
        processing_service.process_document_content.delay(document.id)

        # Generar embeddings si es necesario
        if document.generate_embeddings:
            processing_service.generate_embeddings.delay(document.id)

        # Agregar a knowledge base automáticamente
        add_to_knowledge_base(document)

        # Actualizar contadores
        update_document_counters(document.tenant, 'increment')

    except Exception as e:
        logger.error(f"Error processing new document {document.id}: {e}")

def process_document_update(document):
    """
    Procesa actualización de documento.
    """
    try:
        # Verificar si el contenido cambió
        if document.tracker.has_changed('content'):
            logger.info(f"Document content changed: {document.id}")

            # Reprocesar contenido
            from documents.services import DocumentProcessingService
            processing_service = DocumentProcessingService()
            processing_service.reprocess_document.delay(document.id)

            # Actualizar embeddings
            if document.generate_embeddings:
                processing_service.update_embeddings.delay(document.id)

        # Verificar cambios en metadatos
        if document.tracker.has_changed('metadata'):
            update_knowledge_base_metadata(document)

        # Verificar cambios en estado
        if document.tracker.has_changed('is_active'):
            handle_active_state_change(document)

    except Exception as e:
        logger.error(f"Error processing document update {document.id}: {e}")

def add_to_knowledge_base(document):
    """
    Agrega documento a la base de conocimiento apropiada.
    """
    try:
        # Buscar knowledge base por defecto para el tenant
        default_kb = KnowledgeBase.objects.filter(
            tenant=document.tenant,
            is_default=True
        ).first()

        if default_kb:
            # Agregar documento a la knowledge base
            default_kb.documents.add(document)
            logger.info(f"Document {document.id} added to knowledge base {default_kb.id}")
        else:
            # Crear knowledge base si no existe
            kb = KnowledgeBase.objects.create(
                name=f"Knowledge Base - {document.tenant.name}",
                tenant=document.tenant,
                is_default=True
            )
            kb.documents.add(document)
            logger.info(f"Created new knowledge base {kb.id} for document {document.id}")

        # Actualizar índices de la knowledge base
        update_knowledge_base_index(document.tenant)

    except Exception as e:
        logger.error(f"Error adding document to knowledge base: {e}")

def update_search_indexes(document):
    """
    Actualiza los índices de búsqueda para el documento.
    """
    try:
        from documents.services import SearchIndexService
        search_service = SearchIndexService()

        # Indexar documento para búsqueda
        search_service.index_document.delay(document.id)

        # Actualizar índices relacionados
        search_service.update_related_indexes.delay(document.tenant.id)

    except Exception as e:
        logger.error(f"Error updating search indexes: {e}")

def notify_document_created(document):
    """
    Notifica sobre la creación de un nuevo documento.
    """
    try:
        # Notificar a usuarios interesados
        from notifications.services import NotificationService
        notification_service = NotificationService()

        # Notificar al propietario del documento
        if document.owner:
            notification_service.send_notification(
                recipient=document.owner,
                title="Documento creado",
                message=f"Su documento '{document.title}' ha sido procesado exitosamente",
                notification_type='document_created'
            )

        # Notificar a administradores del tenant
        tenant_admins = document.tenant.get_admin_users()
        for admin in tenant_admins:
            notification_service.send_notification(
                recipient=admin,
                title="Nuevo documento",
                message=f"Nuevo documento agregado: {document.title}",
                notification_type='document_added'
            )

        # Emitir evento para webhooks
        emit_webhook_event(document, 'document.created')

    except Exception as e:
        logger.error(f"Error sending document notifications: {e}")

def record_document_metrics(document, action):
    """
    Registra métricas del documento.
    """
    try:
        from metrics.services import MetricsService
        metrics_service = MetricsService()

        # Contador de documentos por acción
        metrics_service.increment_counter(
            f'documents_{action}_total',
            labels={
                'tenant_id': str(document.tenant.id),
                'document_type': document.document_type,
                'source': document.source or 'unknown'
            }
        )

        # Tamaño de documentos
        if document.file_size:
            metrics_service.observe_histogram(
                'document_size_bytes',
                value=document.file_size,
                labels={
                    'tenant_id': str(document.tenant.id),
                    'document_type': document.document_type
                }
            )

        # Actualizar gauge de documentos activos
        active_count = Document.objects.filter(
            tenant=document.tenant,
            is_active=True
        ).count()

        metrics_service.set_gauge(
            'documents_active_total',
            value=active_count,
            labels={'tenant_id': str(document.tenant.id)}
        )

    except Exception as e:
        logger.error(f"Error recording document metrics: {e}")

def handle_significant_changes(document):
    """
    Maneja cambios significativos en el documento.
    """
    try:
        # Verificar cambios en título
        if document.tracker.has_changed('title'):
            logger.info(f"Document title changed: {document.id}")
            update_references_to_document(document)

        # Verificar cambios en tipo
        if document.tracker.has_changed('document_type'):
            logger.info(f"Document type changed: {document.id}")
            reprocess_document_type(document)

        # Verificar cambios en configuración
        if document.tracker.has_changed('processing_config'):
            logger.info(f"Document processing config changed: {document.id}")
            reprocess_with_new_config(document)

    except Exception as e:
        logger.error(f"Error handling significant changes: {e}")

def update_document_counters(tenant, operation):
    """
    Actualiza contadores de documentos del tenant.
    """
    try:
        if operation == 'increment':
            tenant.document_count += 1
        elif operation == 'decrement':
            tenant.document_count = max(0, tenant.document_count - 1)

        tenant.save(update_fields=['document_count'])

    except Exception as e:
        logger.error(f"Error updating document counters: {e}")

def handle_active_state_change(document):
    """
    Maneja cambios en el estado activo del documento.
    """
    try:
        if document.is_active:
            logger.info(f"Document activated: {document.id}")

            # Reactivar en índices
            from documents.services import SearchIndexService
            search_service = SearchIndexService()
            search_service.reindex_document.delay(document.id)

            # Reactivar en knowledge base
            reactivate_in_knowledge_base(document)

        else:
            logger.info(f"Document deactivated: {document.id}")

            # Remover de índices
            remove_from_search_indexes(document)

            # Desactivar en knowledge base
            deactivate_in_knowledge_base(document)

    except Exception as e:
        logger.error(f"Error handling active state change: {e}")

@receiver(pre_delete, sender=Document)
def document_pre_delete_handler(sender, instance, **kwargs):
    """
    Maneja eventos antes de eliminar un documento.
    """
    logger.info(f"Document being deleted: {instance.title} ({instance.id})")

    try:
        # Respaldar información importante
        backup_document_info(instance)

        # Notificar antes de eliminar
        notify_document_deletion(instance)

        # Limpiar referencias
        cleanup_document_references(instance)

    except Exception as e:
        logger.error(f"Error in pre-delete handler: {e}")

@receiver(post_delete, sender=Document)
def document_post_delete_handler(sender, instance, **kwargs):
    """
    Maneja eventos después de eliminar un documento.
    """
    logger.info(f"Document deleted: {instance.title} ({instance.id})")

    try:
        # Eliminar archivo físico
        cleanup_document_file(instance)

        # Limpiar índices
        cleanup_search_indexes(instance)

        # Actualizar contadores
        update_document_counters(instance.tenant, 'decrement')

        # Registrar métricas
        record_document_metrics(instance, 'deleted')

        # Actualizar knowledge base
        update_knowledge_base_after_deletion(instance)

    except Exception as e:
        logger.error(f"Error in post-delete handler: {e}")

def backup_document_info(document):
    """
    Respalda información del documento antes de eliminar.
    """
    try:
        from documents.models import DocumentDeletionLog

        DocumentDeletionLog.objects.create(
            document_id=document.id,
            title=document.title,
            document_type=document.document_type,
            file_size=document.file_size,
            tenant=document.tenant,
            deleted_by=getattr(document, '_deleted_by', None),
            metadata=document.metadata
        )

    except Exception as e:
        logger.error(f"Error backing up document info: {e}")

def notify_document_deletion(document):
    """
    Notifica sobre la eliminación del documento.
    """
    try:
        from notifications.services import NotificationService
        notification_service = NotificationService()

        # Notificar a usuarios que tienen el documento en favoritos
        favorite_users = document.favorited_by.all()
        for user in favorite_users:
            notification_service.send_notification(
                recipient=user,
                title="Documento eliminado",
                message=f"El documento '{document.title}' ha sido eliminado",
                notification_type='document_deleted'
            )

        # Emitir evento para webhooks
        emit_webhook_event(document, 'document.deleted')

    except Exception as e:
        logger.error(f"Error notifying document deletion: {e}")

def cleanup_document_file(document):
    """
    Limpia el archivo físico del documento.
    """
    try:
        if document.file_path:
            import os
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
                logger.info(f"Document file deleted: {document.file_path}")

    except Exception as e:
        logger.error(f"Error cleaning up document file: {e}")

def cleanup_search_indexes(document):
    """
    Limpia los índices de búsqueda del documento.
    """
    try:
        from documents.services import SearchIndexService
        search_service = SearchIndexService()

        # Remover de índices
        search_service.remove_from_index.delay(document.id)

    except Exception as e:
        logger.error(f"Error cleaning up search indexes: {e}")

def update_knowledge_base_after_deletion(document):
    """
    Actualiza knowledge base después de eliminar documento.
    """
    try:
        # Remover de todas las knowledge bases
        knowledge_bases = document.knowledge_bases.all()
        for kb in knowledge_bases:
            kb.documents.remove(document)

            # Actualizar índices de la knowledge base
            update_knowledge_base_index(kb.tenant)

    except Exception as e:
        logger.error(f"Error updating knowledge base after deletion: {e}")

def emit_webhook_event(document, event_type):
    """
    Emite evento para webhooks.
    """
    try:
        from webhooks.services import WebhookService
        webhook_service = WebhookService()

        webhook_service.emit_event(
            event_type=event_type,
            tenant=document.tenant,
            data={
                'document_id': document.id,
                'title': document.title,
                'document_type': document.document_type,
                'timestamp': timezone.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error emitting webhook event: {e}")

# Funciones auxiliares
def update_knowledge_base_index(tenant):
    """
    Actualiza índices de knowledge base para un tenant.
    """
    try:
        from knowledge.services import KnowledgeBaseService
        kb_service = KnowledgeBaseService()

        kb_service.update_indexes.delay(tenant.id)

    except Exception as e:
        logger.error(f"Error updating knowledge base index: {e}")

def update_references_to_document(document):
    """
    Actualiza referencias al documento en otros sistemas.
    """
    try:
        # Actualizar referencias en chats
        from chats.models import Message
        Message.objects.filter(
            referenced_documents=document
        ).update(updated_at=timezone.now())

        # Actualizar referencias en agentes
        from agents.models import AgentModel
        agents = AgentModel.objects.filter(knowledge_documents=document)
        for agent in agents:
            agent.knowledge_updated_at = timezone.now()
            agent.save(update_fields=['knowledge_updated_at'])

    except Exception as e:
        logger.error(f"Error updating references to document: {e}")

def reprocess_document_type(document):
    """
    Reprocesa documento con nuevo tipo.
    """
    try:
        from documents.services import DocumentProcessingService
        processing_service = DocumentProcessingService()

        # Reprocesar con configuración del nuevo tipo
        processing_service.reprocess_with_type.delay(
            document.id,
            document.document_type
        )

    except Exception as e:
        logger.error(f"Error reprocessing document type: {e}")

def reprocess_with_new_config(document):
    """
    Reprocesa documento con nueva configuración.
    """
    try:
        from documents.services import DocumentProcessingService
        processing_service = DocumentProcessingService()

        # Reprocesar con nueva configuración
        processing_service.reprocess_with_config.delay(
            document.id,
            document.processing_config
        )

    except Exception as e:
        logger.error(f"Error reprocessing with new config: {e}")

def cleanup_document_references(document):
    """
    Limpia referencias al documento antes de eliminar.
    """
    try:
        # Remover de favoritos
        document.favorited_by.clear()

        # Remover de knowledge bases
        document.knowledge_bases.clear()

        # Limpiar referencias en otros modelos
        from chats.models import Message
        Message.objects.filter(
            referenced_documents=document
        ).update(referenced_documents=None)

    except Exception as e:
        logger.error(f"Error cleaning up document references: {e}")

def reactivate_in_knowledge_base(document):
    """
    Reactiva documento en knowledge base.
    """
    try:
        knowledge_bases = document.knowledge_bases.all()
        for kb in knowledge_bases:
            # Reactivar en índices
            kb.reindex_document(document)

    except Exception as e:
        logger.error(f"Error reactivating in knowledge base: {e}")

def deactivate_in_knowledge_base(document):
    """
    Desactiva documento en knowledge base.
    """
    try:
        knowledge_bases = document.knowledge_bases.all()
        for kb in knowledge_bases:
            # Desactivar en índices
            kb.deactivate_document(document)

    except Exception as e:
        logger.error(f"Error deactivating in knowledge base: {e}")

def remove_from_search_indexes(document):
    """
    Remover documento de índices de búsqueda.
    """
    try:
        from documents.services import SearchIndexService
        search_service = SearchIndexService()

        search_service.remove_from_index.delay(document.id)

    except Exception as e:
        logger.error(f"Error removing from search indexes: {e}")

def update_knowledge_base_metadata(document):
    """
    Actualiza metadatos en knowledge base.
    """
    try:
        knowledge_bases = document.knowledge_bases.all()
        for kb in knowledge_bases:
            kb.update_document_metadata(document)

    except Exception as e:
        logger.error(f"Error updating knowledge base metadata: {e}")
```

## Configuración de Señales

### Registro en apps.py
```python
# apps.py
from django.apps import AppConfig

class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'documents'

    def ready(self):
        import documents.signals.handle_knowledge_changes
```

### Señales Personalizadas
```python
from django.dispatch import Signal

# Definir señales personalizadas
document_processed = Signal()
embeddings_generated = Signal()
knowledge_base_updated = Signal()

# Uso de señales personalizadas
document_processed.send(
    sender=Document,
    document=document_instance,
    processing_results=results
)
```

## Casos de Uso Avanzados

### Procesamiento Asíncrono
```python
@receiver(post_save, sender=Document)
def async_document_processing(sender, instance, created, **kwargs):
    if created:
        # Procesar de forma asíncrona
        from documents.tasks import process_document_async
        process_document_async.delay(instance.id)
```

### Versionado de Documentos
```python
@receiver(post_save, sender=Document)
def handle_document_versioning(sender, instance, created, **kwargs):
    if not created and instance.tracker.has_changed('content'):
        # Crear nueva versión
        create_document_version(instance)
```

### Sincronización con Servicios Externos
```python
@receiver(post_save, sender=Document)
def sync_with_external_services(sender, instance, created, **kwargs):
    if created:
        # Sincronizar con servicios externos
        sync_to_external_storage.delay(instance.id)
        sync_to_search_engine.delay(instance.id)
```

## Testing

### Test de Señales
```python
from django.test import TestCase
from unittest.mock import patch

class DocumentSignalsTestCase(TestCase):
    @patch('documents.signals.handle_knowledge_changes.process_new_document')
    def test_document_creation_signal(self, mock_process):
        # Crear documento
        document = Document.objects.create(
            title="Test Document",
            tenant=self.tenant
        )

        # Verificar que la señal fue procesada
        mock_process.assert_called_once_with(document)

    @patch('documents.signals.handle_knowledge_changes.cleanup_document_file')
    def test_document_deletion_signal(self, mock_cleanup):
        # Crear y eliminar documento
        document = Document.objects.create(
            title="Test Document",
            tenant=self.tenant
        )
        document.delete()

        # Verificar que la limpieza fue ejecutada
        mock_cleanup.assert_called_once()
```

## Mejores Prácticas

1. **Manejo de Errores**: Capturar y registrar todas las excepciones
2. **Procesamiento Asíncrono**: Usar Celery para operaciones pesadas
3. **Logging Detallado**: Registrar eventos importantes para debugging
4. **Idempotencia**: Asegurar que las señales puedan ejecutarse múltiples veces
5. **Testing**: Escribir tests para verificar comportamiento de señales
6. **Monitoring**: Registrar métricas y monitorear rendimiento

## Monitoreo y Debugging

### Métricas de Señales
```python
from functools import wraps
import time

def monitor_signal_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            # Registrar éxito
            return result
        except Exception as e:
            # Registrar error
            logger.error(f"Signal error: {e}")
            raise
        finally:
            duration = time.time() - start_time
            # Registrar duración
            logger.info(f"Signal {func.__name__} took {duration:.2f}s")
    return wrapper
```

### Debugging de Señales
```python
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Document)
def debug_document_signal(sender, instance, created, **kwargs):
    logger.debug(f"Document signal: {instance.id}, created: {created}")
    logger.debug(f"Document data: {instance.__dict__}")
```
