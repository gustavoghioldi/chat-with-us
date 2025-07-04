# Knowledge Signals - Señales del Módulo de Conocimiento

## Descripción General
Este módulo contiene las señales de Django que se ejecutan automáticamente en respuesta a eventos relacionados con el sistema de conocimiento. Las señales permiten implementar lógica de negocio que se ejecuta cuando ocurren cambios en documentos, bases de conocimiento y otros elementos del sistema.

## Estructura del Módulo

### Archivos Principales
- **handle_document_changes.py**: Señales para manejar cambios en documentos

## Señales Implementadas

### 1. Señales de Documentos (handle_document_changes.py)

#### post_save_document
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from documents.models import Document
from knowledge.services import KnowledgeIndexService, DocumentProcessor

@receiver(post_save, sender=Document)
def handle_document_save(sender, instance, created, **kwargs):
    """
    Maneja el evento de guardado de un documento.

    Args:
        sender: El modelo que envió la señal
        instance: La instancia del documento
        created: True si el documento fue creado, False si fue actualizado
        **kwargs: Argumentos adicionales
    """
    if created:
        # Documento nuevo - procesar para indexación
        process_new_document.delay(instance.id)

        # Notificar a los usuarios con permisos
        notify_document_created.delay(instance.id)

        # Generar embeddings si es necesario
        generate_document_embeddings.delay(instance.id)

    else:
        # Documento actualizado - re-indexar si es necesario
        if instance.content_has_changed():
            reindex_document.delay(instance.id)

        # Actualizar estadísticas
        update_knowledge_base_stats.delay(instance.knowledge_base.id)
```

#### post_delete_document
```python
@receiver(post_delete, sender=Document)
def handle_document_delete(sender, instance, **kwargs):
    """
    Maneja el evento de eliminación de un documento.

    Args:
        sender: El modelo que envió la señal
        instance: La instancia del documento eliminado
        **kwargs: Argumentos adicionales
    """
    # Limpiar índices de búsqueda
    cleanup_document_indexes.delay(instance.id)

    # Actualizar estadísticas de la base de conocimiento
    update_knowledge_base_stats.delay(instance.knowledge_base.id)

    # Notificar eliminación
    notify_document_deleted.delay(instance.id, instance.tenant.id)

    # Limpiar archivos físicos si es necesario
    cleanup_document_files.delay(instance.file_path)
```

#### pre_save_document
```python
@receiver(pre_save, sender=Document)
def handle_document_pre_save(sender, instance, **kwargs):
    """
    Maneja el evento antes de guardar un documento.

    Args:
        sender: El modelo que envió la señal
        instance: La instancia del documento
        **kwargs: Argumentos adicionales
    """
    # Validar contenido del documento
    if instance.content:
        validate_document_content(instance)

    # Generar hash del contenido para detectar cambios
    instance.content_hash = generate_content_hash(instance.content)

    # Extraer metadatos si es un archivo
    if instance.file and not instance.metadata:
        instance.metadata = extract_document_metadata(instance.file)

    # Establecer fecha de última modificación
    if instance.pk:  # Solo para documentos existentes
        instance.last_modified = timezone.now()
```

### 2. Señales de Base de Conocimiento

#### post_save_knowledge_base
```python
from knowledge.models import KnowledgeBase

@receiver(post_save, sender=KnowledgeBase)
def handle_knowledge_base_save(sender, instance, created, **kwargs):
    """
    Maneja el evento de guardado de una base de conocimiento.

    Args:
        sender: El modelo que envió la señal
        instance: La instancia de la base de conocimiento
        created: True si fue creada, False si fue actualizada
        **kwargs: Argumentos adicionales
    """
    if created:
        # Nueva base de conocimiento
        initialize_knowledge_base.delay(instance.id)

        # Crear configuración por defecto
        create_default_kb_config.delay(instance.id)

        # Notificar a administradores
        notify_kb_created.delay(instance.id)

    else:
        # Base de conocimiento actualizada
        if instance.settings_changed():
            update_kb_processing_settings.delay(instance.id)

        # Actualizar índices si cambió la configuración
        if instance.index_config_changed():
            reindex_knowledge_base.delay(instance.id)
```

#### post_delete_knowledge_base
```python
@receiver(post_delete, sender=KnowledgeBase)
def handle_knowledge_base_delete(sender, instance, **kwargs):
    """
    Maneja el evento de eliminación de una base de conocimiento.

    Args:
        sender: El modelo que envió la señal
        instance: La instancia de la base de conocimiento eliminada
        **kwargs: Argumentos adicionales
    """
    # Limpiar todos los índices relacionados
    cleanup_knowledge_base_indexes.delay(instance.id)

    # Limpiar archivos de embeddings
    cleanup_knowledge_base_embeddings.delay(instance.id)

    # Notificar eliminación
    notify_kb_deleted.delay(instance.id, instance.tenant.id)

    # Actualizar estadísticas del tenant
    update_tenant_knowledge_stats.delay(instance.tenant.id)
```

### 3. Señales de Consultas de Conocimiento

#### post_save_knowledge_query
```python
from knowledge.models import KnowledgeQuery

@receiver(post_save, sender=KnowledgeQuery)
def handle_knowledge_query_save(sender, instance, created, **kwargs):
    """
    Maneja el evento de guardado de una consulta de conocimiento.

    Args:
        sender: El modelo que envió la señal
        instance: La instancia de la consulta
        created: True si fue creada, False si fue actualizada
        **kwargs: Argumentos adicionales
    """
    if created:
        # Nueva consulta - actualizar métricas
        update_knowledge_usage_metrics.delay(instance.knowledge_base.id)

        # Analizar consulta para mejorar el sistema
        analyze_knowledge_query.delay(instance.id)

        # Generar sugerencias si es necesario
        if instance.results_count == 0:
            generate_query_suggestions.delay(instance.id)
```

## Tareas Asíncronas (Celery)

### Procesamiento de Documentos
```python
from celery import shared_task
from knowledge.services import DocumentProcessor, EmbeddingService

@shared_task
def process_new_document(document_id):
    """
    Procesa un nuevo documento para indexación.

    Args:
        document_id: ID del documento a procesar
    """
    try:
        document = Document.objects.get(id=document_id)
        processor = DocumentProcessor(document)

        # Extraer texto del documento
        extracted_text = processor.extract_text()

        # Limpiar y procesar texto
        processed_text = processor.clean_text(extracted_text)

        # Generar chunks para indexación
        chunks = processor.create_chunks(processed_text)

        # Indexar cada chunk
        for chunk in chunks:
            index_document_chunk.delay(document_id, chunk)

        # Marcar como procesado
        document.processing_status = 'completed'
        document.save()

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found for processing")
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        # Marcar como fallido
        document.processing_status = 'failed'
        document.save()
```

### Generación de Embeddings
```python
@shared_task
def generate_document_embeddings(document_id):
    """
    Genera embeddings para un documento.

    Args:
        document_id: ID del documento
    """
    try:
        document = Document.objects.get(id=document_id)
        embedding_service = EmbeddingService()

        # Generar embeddings para el documento completo
        document_embedding = embedding_service.generate_embedding(
            document.content
        )

        # Guardar embedding
        document.embedding = document_embedding
        document.save()

        # Generar embeddings para chunks si existen
        for chunk in document.chunks.all():
            chunk_embedding = embedding_service.generate_embedding(
                chunk.content
            )
            chunk.embedding = chunk_embedding
            chunk.save()

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found for embedding generation")
    except Exception as e:
        logger.error(f"Error generating embeddings for document {document_id}: {str(e)}")
```

### Indexación de Documentos
```python
@shared_task
def reindex_document(document_id):
    """
    Re-indexa un documento actualizado.

    Args:
        document_id: ID del documento a re-indexar
    """
    try:
        document = Document.objects.get(id=document_id)
        search_service = KnowledgeSearchService()

        # Eliminar índices existentes
        search_service.remove_document_from_index(document_id)

        # Crear nuevos índices
        search_service.index_document(document)

        # Actualizar timestamp de indexación
        document.last_indexed = timezone.now()
        document.save()

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found for reindexing")
    except Exception as e:
        logger.error(f"Error reindexing document {document_id}: {str(e)}")
```

## Utilidades de Señales

### Funciones de Validación
```python
def validate_document_content(document):
    """
    Valida el contenido de un documento antes de guardarlo.

    Args:
        document: Instancia del documento a validar

    Raises:
        ValidationError: Si el contenido no es válido
    """
    if not document.content and not document.file:
        raise ValidationError("El documento debe tener contenido o archivo")

    if document.content and len(document.content) > 10000000:  # 10MB
        raise ValidationError("El contenido del documento es demasiado grande")

    # Validar formato de contenido
    if document.content_type == 'text/plain':
        validate_plain_text(document.content)
    elif document.content_type == 'text/html':
        validate_html_content(document.content)
```

### Generación de Hash
```python
import hashlib

def generate_content_hash(content):
    """
    Genera un hash del contenido del documento.

    Args:
        content: Contenido del documento

    Returns:
        str: Hash MD5 del contenido
    """
    if not content:
        return None

    return hashlib.md5(content.encode('utf-8')).hexdigest()
```

### Extracción de Metadatos
```python
def extract_document_metadata(file):
    """
    Extrae metadatos de un archivo.

    Args:
        file: Archivo del documento

    Returns:
        dict: Metadatos extraídos
    """
    metadata = {
        'filename': file.name,
        'size': file.size,
        'content_type': file.content_type,
        'extracted_at': timezone.now().isoformat()
    }

    # Extraer metadatos específicos según el tipo
    if file.content_type == 'application/pdf':
        metadata.update(extract_pdf_metadata(file))
    elif file.content_type.startswith('image/'):
        metadata.update(extract_image_metadata(file))
    elif file.content_type.startswith('text/'):
        metadata.update(extract_text_metadata(file))

    return metadata
```

## Notificaciones

### Sistema de Notificaciones
```python
@shared_task
def notify_document_created(document_id):
    """
    Notifica la creación de un nuevo documento.

    Args:
        document_id: ID del documento creado
    """
    try:
        document = Document.objects.get(id=document_id)

        # Obtener usuarios que deben ser notificados
        users_to_notify = get_users_to_notify(document)

        for user in users_to_notify:
            send_notification(
                user=user,
                title="Nuevo documento agregado",
                message=f"Se ha agregado un nuevo documento: {document.title}",
                type="document_created",
                related_object=document
            )

    except Document.DoesNotExist:
        logger.error(f"Document {document_id} not found for notification")
```

### Notificaciones por Email
```python
@shared_task
def send_knowledge_digest(tenant_id, period='daily'):
    """
    Envía un resumen de actividad de conocimiento.

    Args:
        tenant_id: ID del tenant
        period: Período del resumen ('daily', 'weekly', 'monthly')
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id)

        # Obtener estadísticas del período
        stats = get_knowledge_stats(tenant, period)

        # Obtener usuarios suscritos
        subscribers = get_digest_subscribers(tenant)

        # Generar y enviar emails
        for user in subscribers:
            send_digest_email(user, stats, period)

    except Tenant.DoesNotExist:
        logger.error(f"Tenant {tenant_id} not found for digest")
```

## Métricas y Analíticas

### Actualización de Métricas
```python
@shared_task
def update_knowledge_usage_metrics(knowledge_base_id):
    """
    Actualiza las métricas de uso de una base de conocimiento.

    Args:
        knowledge_base_id: ID de la base de conocimiento
    """
    try:
        kb = KnowledgeBase.objects.get(id=knowledge_base_id)

        # Calcular métricas
        metrics = {
            'total_queries': KnowledgeQuery.objects.filter(
                knowledge_base=kb
            ).count(),
            'queries_today': KnowledgeQuery.objects.filter(
                knowledge_base=kb,
                created_at__date=timezone.now().date()
            ).count(),
            'avg_results_per_query': KnowledgeQuery.objects.filter(
                knowledge_base=kb
            ).aggregate(
                avg_results=Avg('results_count')
            )['avg_results'] or 0,
            'last_query_at': KnowledgeQuery.objects.filter(
                knowledge_base=kb
            ).aggregate(
                last_query=Max('created_at')
            )['last_query']
        }

        # Actualizar métricas en la base de conocimiento
        kb.metrics = metrics
        kb.save()

    except KnowledgeBase.DoesNotExist:
        logger.error(f"KnowledgeBase {knowledge_base_id} not found for metrics update")
```

## Limpieza y Mantenimiento

### Limpieza de Índices
```python
@shared_task
def cleanup_document_indexes(document_id):
    """
    Limpia los índices de un documento eliminado.

    Args:
        document_id: ID del documento eliminado
    """
    try:
        search_service = KnowledgeSearchService()

        # Eliminar de índices de búsqueda
        search_service.remove_document_from_index(document_id)

        # Eliminar embeddings
        EmbeddingService().remove_document_embeddings(document_id)

        # Limpiar caché relacionado
        cache_keys = [
            f"document_{document_id}",
            f"document_chunks_{document_id}",
            f"document_embeddings_{document_id}"
        ]

        for key in cache_keys:
            cache.delete(key)

    except Exception as e:
        logger.error(f"Error cleaning up indexes for document {document_id}: {str(e)}")
```

### Limpieza de Archivos
```python
@shared_task
def cleanup_document_files(file_path):
    """
    Limpia archivos físicos de un documento eliminado.

    Args:
        file_path: Ruta del archivo a eliminar
    """
    try:
        import os

        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Removed file: {file_path}")

        # Limpiar thumbnails o archivos derivados
        cleanup_derived_files(file_path)

    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {str(e)}")
```

## Configuración

### Registro de Señales
```python
# knowledge/apps.py
from django.apps import AppConfig

class KnowledgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'knowledge'

    def ready(self):
        # Importar señales para registrarlas
        import knowledge.signals.handle_document_changes
```

### Variables de Configuración
```python
# settings.py
KNOWLEDGE_SIGNALS_CONFIG = {
    'ENABLE_ASYNC_PROCESSING': True,
    'ENABLE_DOCUMENT_NOTIFICATIONS': True,
    'ENABLE_USAGE_METRICS': True,
    'CLEANUP_DELAY_MINUTES': 30,
    'NOTIFICATION_BATCH_SIZE': 100,
}
```

## Testing

### Tests de Señales
```python
from django.test import TestCase
from django.test.utils import override_settings
from unittest.mock import patch

class KnowledgeSignalsTestCase(TestCase):

    def setUp(self):
        self.tenant = TenantFactory()
        self.user = UserFactory()
        self.knowledge_base = KnowledgeBaseFactory(tenant=self.tenant)

    @patch('knowledge.signals.handle_document_changes.process_new_document.delay')
    def test_document_created_signal(self, mock_process):
        """Test que se ejecuta el procesamiento cuando se crea un documento."""
        document = DocumentFactory(
            knowledge_base=self.knowledge_base,
            tenant=self.tenant
        )

        mock_process.assert_called_once_with(document.id)

    @patch('knowledge.signals.handle_document_changes.cleanup_document_indexes.delay')
    def test_document_deleted_signal(self, mock_cleanup):
        """Test que se ejecuta la limpieza cuando se elimina un documento."""
        document = DocumentFactory(
            knowledge_base=self.knowledge_base,
            tenant=self.tenant
        )
        document_id = document.id
        document.delete()

        mock_cleanup.assert_called_once_with(document_id)
```

## Monitoreo

### Logging de Señales
```python
import logging

logger = logging.getLogger(__name__)

def log_signal_execution(signal_name, instance, **kwargs):
    """
    Registra la ejecución de una señal.

    Args:
        signal_name: Nombre de la señal
        instance: Instancia del modelo
        **kwargs: Argumentos adicionales
    """
    logger.info(
        f"Signal {signal_name} executed for {instance.__class__.__name__} "
        f"with id {instance.id}"
    )
```

### Métricas de Rendimiento
```python
from django.core.cache import cache
from django.utils import timezone

def track_signal_performance(signal_name):
    """
    Decorador para medir el rendimiento de señales.

    Args:
        signal_name: Nombre de la señal
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = timezone.now()
            result = func(*args, **kwargs)
            end_time = timezone.now()

            duration = (end_time - start_time).total_seconds()

            # Guardar métricas en caché
            cache_key = f"signal_performance_{signal_name}"
            performance_data = cache.get(cache_key, [])
            performance_data.append({
                'timestamp': start_time.isoformat(),
                'duration': duration
            })

            # Mantener solo últimas 100 ejecuciones
            if len(performance_data) > 100:
                performance_data = performance_data[-100:]

            cache.set(cache_key, performance_data, 3600)  # 1 hora

            return result
        return wrapper
    return decorator
```

## Mejores Prácticas

### 1. Manejo de Errores
- Siempre usar try/except en señales
- Registrar errores detallados
- No lanzar excepciones que puedan interrumpir el flujo principal

### 2. Procesamiento Asíncrono
- Usar Celery para operaciones pesadas
- Evitar operaciones síncronas en señales
- Implementar reintentos para tareas fallidas

### 3. Eficiencia
- Minimizar consultas a la base de datos
- Usar select_related/prefetch_related
- Implementar caching cuando sea apropiado

### 4. Configurabilidad
- Hacer las señales configurables
- Permitir deshabilitarlas en entornos de testing
- Usar feature flags para funcionalidades opcionales

Este sistema de señales proporciona una base sólida para el manejo automático de eventos en el módulo de conocimiento, garantizando la integridad de los datos y la eficiencia del sistema.
