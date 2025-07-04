# Comandos de Management de Documentos

## Descripción General
Este directorio contiene comandos personalizados de Django para la gestión de documentos. Estos comandos se pueden ejecutar desde la línea de comandos usando `python manage.py <comando>`.

## Estructura de Archivos

### `cleanup_documents.py`
Comando para limpieza automática de documentos.

```python
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from documents.models import Document
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Limpia documentos antiguos y archivos huérfanos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Número de días para considerar documentos como antiguos'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin realizar cambios reales'
        )

        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar limpieza sin confirmación'
        )

        parser.add_argument(
            '--type',
            choices=['all', 'unused', 'expired', 'orphaned'],
            default='all',
            help='Tipo de limpieza a realizar'
        )

        parser.add_argument(
            '--tenant',
            type=str,
            help='ID del tenant específico para limpiar'
        )

    def handle(self, *args, **options):
        """
        Ejecuta el comando de limpieza.
        """
        self.stdout.write(
            self.style.SUCCESS('Iniciando limpieza de documentos...')
        )

        days = options['days']
        dry_run = options['dry_run']
        force = options['force']
        cleanup_type = options['type']
        tenant_id = options['tenant']

        if dry_run:
            self.stdout.write(
                self.style.WARNING('Modo DRY-RUN activado - No se realizarán cambios')
            )

        # Realizar limpieza según el tipo
        if cleanup_type == 'all':
            self.cleanup_all(days, dry_run, force, tenant_id)
        elif cleanup_type == 'unused':
            self.cleanup_unused_documents(days, dry_run, tenant_id)
        elif cleanup_type == 'expired':
            self.cleanup_expired_documents(dry_run, tenant_id)
        elif cleanup_type == 'orphaned':
            self.cleanup_orphaned_files(dry_run, tenant_id)

        self.stdout.write(
            self.style.SUCCESS('Limpieza completada')
        )

    def cleanup_all(self, days, dry_run, force, tenant_id):
        """
        Realiza limpieza completa.
        """
        if not force:
            confirm = input(
                f'¿Está seguro de que desea limpiar documentos de más de {days} días? (y/N): '
            )
            if confirm.lower() != 'y':
                self.stdout.write('Operación cancelada')
                return

        self.cleanup_unused_documents(days, dry_run, tenant_id)
        self.cleanup_expired_documents(dry_run, tenant_id)
        self.cleanup_orphaned_files(dry_run, tenant_id)

    def cleanup_unused_documents(self, days, dry_run, tenant_id):
        """
        Limpia documentos no utilizados.
        """
        cutoff_date = timezone.now() - timedelta(days=days)

        queryset = Document.objects.filter(
            last_accessed__lt=cutoff_date,
            is_active=True
        )

        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)

        # Filtrar documentos que no están siendo utilizados
        unused_docs = []
        for doc in queryset:
            if not self.is_document_referenced(doc):
                unused_docs.append(doc)

        self.stdout.write(
            f'Encontrados {len(unused_docs)} documentos no utilizados'
        )

        if not dry_run:
            deleted_count = 0
            for doc in unused_docs:
                try:
                    self.delete_document(doc)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f'Error eliminando documento {doc.id}: {e}')

            self.stdout.write(
                self.style.SUCCESS(f'Eliminados {deleted_count} documentos')
            )
        else:
            for doc in unused_docs:
                self.stdout.write(f'  - {doc.title} ({doc.id})')

    def cleanup_expired_documents(self, dry_run, tenant_id):
        """
        Limpia documentos con fecha de expiración.
        """
        queryset = Document.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )

        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)

        expired_docs = list(queryset)

        self.stdout.write(
            f'Encontrados {len(expired_docs)} documentos expirados'
        )

        if not dry_run:
            deleted_count = 0
            for doc in expired_docs:
                try:
                    self.delete_document(doc)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f'Error eliminando documento expirado {doc.id}: {e}')

            self.stdout.write(
                self.style.SUCCESS(f'Eliminados {deleted_count} documentos expirados')
            )
        else:
            for doc in expired_docs:
                self.stdout.write(f'  - {doc.title} (expirado: {doc.expires_at})')

    def cleanup_orphaned_files(self, dry_run, tenant_id):
        """
        Limpia archivos huérfanos en el sistema de archivos.
        """
        media_root = settings.MEDIA_ROOT
        documents_path = os.path.join(media_root, 'documents')

        if not os.path.exists(documents_path):
            self.stdout.write('Directorio de documentos no encontrado')
            return

        orphaned_files = []

        # Recorrer archivos en el directorio
        for root, dirs, files in os.walk(documents_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, media_root)

                # Verificar si el archivo está referenciado en la base de datos
                if not Document.objects.filter(file_path=relative_path).exists():
                    orphaned_files.append(file_path)

        self.stdout.write(
            f'Encontrados {len(orphaned_files)} archivos huérfanos'
        )

        if not dry_run:
            deleted_count = 0
            for file_path in orphaned_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f'Error eliminando archivo {file_path}: {e}')

            self.stdout.write(
                self.style.SUCCESS(f'Eliminados {deleted_count} archivos huérfanos')
            )
        else:
            for file_path in orphaned_files:
                self.stdout.write(f'  - {file_path}')

    def is_document_referenced(self, document):
        """
        Verifica si un documento está siendo referenciado.
        """
        # Verificar si está siendo usado por agentes
        if document.agents.exists():
            return True

        # Verificar si está en knowledge base activa
        if document.knowledge_bases.filter(is_active=True).exists():
            return True

        # Verificar si tiene referencias en chats recientes
        recent_date = timezone.now() - timedelta(days=7)
        if document.chat_references.filter(created_at__gte=recent_date).exists():
            return True

        return False

    def delete_document(self, document):
        """
        Elimina un documento y su archivo asociado.
        """
        # Eliminar archivo físico
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Eliminar entrada de base de datos
        document.delete()

        logger.info(f'Documento eliminado: {document.title} ({document.id})')

    def get_file_size_mb(self, file_path):
        """
        Obtiene el tamaño del archivo en MB.
        """
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0
```

## Comandos Adicionales

### Comando para Optimización de Documentos
```python
class OptimizeDocumentsCommand(BaseCommand):
    help = 'Optimiza documentos para mejorar rendimiento'

    def handle(self, *args, **options):
        # Reindexar documentos
        self.reindex_documents()

        # Optimizar tamaños de archivo
        self.optimize_file_sizes()

        # Limpiar metadatos
        self.clean_metadata()

    def reindex_documents(self):
        """Reindexa documentos para búsqueda."""
        from documents.services import DocumentIndexService

        service = DocumentIndexService()
        documents = Document.objects.filter(is_active=True)

        for doc in documents:
            service.index_document(doc)
            self.stdout.write(f'Reindexado: {doc.title}')
```

### Comando para Estadísticas
```python
class DocumentStatsCommand(BaseCommand):
    help = 'Muestra estadísticas de documentos'

    def handle(self, *args, **options):
        # Contar documentos por tipo
        stats = Document.objects.values('document_type').annotate(
            count=Count('id'),
            total_size=Sum('file_size')
        )

        self.stdout.write('Estadísticas por tipo de documento:')
        for stat in stats:
            self.stdout.write(
                f"  {stat['document_type']}: {stat['count']} documentos, "
                f"{stat['total_size']/(1024*1024):.2f} MB"
            )
```

### Comando para Migración de Documentos
```python
class MigrateDocumentsCommand(BaseCommand):
    help = 'Migra documentos a nueva estructura'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-version',
            type=str,
            required=True,
            help='Versión de origen'
        )

        parser.add_argument(
            '--to-version',
            type=str,
            required=True,
            help='Versión de destino'
        )

    def handle(self, *args, **options):
        from_version = options['from_version']
        to_version = options['to_version']

        self.stdout.write(
            f'Migrando de versión {from_version} a {to_version}'
        )

        # Implementar lógica de migración
        self.migrate_documents(from_version, to_version)
```

## Uso de los Comandos

### Comando de Limpieza
```bash
# Limpieza básica (documentos de más de 30 días)
python manage.py cleanup_documents

# Limpieza con parámetros específicos
python manage.py cleanup_documents --days 60 --type unused

# Modo dry-run para ver qué se eliminaría
python manage.py cleanup_documents --dry-run

# Limpieza forzada sin confirmación
python manage.py cleanup_documents --force

# Limpieza para un tenant específico
python manage.py cleanup_documents --tenant 123

# Solo limpiar archivos huérfanos
python manage.py cleanup_documents --type orphaned
```

### Comando de Optimización
```bash
# Optimizar todos los documentos
python manage.py optimize_documents

# Optimizar con verbose
python manage.py optimize_documents --verbosity 2
```

### Comando de Estadísticas
```bash
# Mostrar estadísticas generales
python manage.py document_stats

# Estadísticas detalladas
python manage.py document_stats --detailed
```

## Configuración en Cron

### Limpieza Automática
```bash
# Ejecutar limpieza diariamente a las 2 AM
0 2 * * * cd /path/to/project && python manage.py cleanup_documents --days 30 --force

# Optimización semanal
0 3 * * 0 cd /path/to/project && python manage.py optimize_documents
```

## Logging y Monitoreo

### Configuración de Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'document_cleanup': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/document_cleanup.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'documents.management.commands': {
            'handlers': ['document_cleanup'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Métricas de Limpieza
```python
def record_cleanup_metrics(self, deleted_count, total_size_mb):
    """
    Registra métricas de limpieza.
    """
    from metrics.services import MetricsService

    metrics_service = MetricsService()
    metrics_service.increment_counter(
        'documents_cleaned_total',
        value=deleted_count
    )
    metrics_service.observe_histogram(
        'documents_cleaned_size_mb',
        value=total_size_mb
    )
```

## Testing

### Test de Comandos
```python
from django.test import TestCase
from django.core.management import call_command
from io import StringIO

class CleanupDocumentsTestCase(TestCase):
    def test_cleanup_dry_run(self):
        # Crear documentos de prueba
        self.create_test_documents()

        # Ejecutar comando en modo dry-run
        out = StringIO()
        call_command('cleanup_documents', '--dry-run', stdout=out)

        # Verificar output
        self.assertIn('DRY-RUN', out.getvalue())

        # Verificar que no se eliminaron documentos
        self.assertEqual(Document.objects.count(), 3)

    def test_cleanup_unused_documents(self):
        # Crear documentos no utilizados
        old_date = timezone.now() - timedelta(days=60)
        Document.objects.create(
            title='Old Document',
            last_accessed=old_date
        )

        # Ejecutar comando
        call_command('cleanup_documents', '--type', 'unused', '--force')

        # Verificar que se eliminó
        self.assertFalse(
            Document.objects.filter(title='Old Document').exists()
        )
```

## Mejores Prácticas

1. **Backup**: Siempre hacer backup antes de ejecutar limpieza
2. **Dry Run**: Usar `--dry-run` para verificar antes de ejecutar
3. **Logging**: Registrar todas las operaciones importantes
4. **Confirmación**: Requerir confirmación para operaciones destructivas
5. **Métricas**: Registrar métricas de limpieza para monitoreo
6. **Testing**: Probar comandos en entorno de desarrollo
7. **Scheduling**: Usar cron para automatizar tareas regulares

## Extensibilidad

### Agregar Nuevos Tipos de Limpieza
```python
def cleanup_custom_type(self, dry_run, tenant_id):
    """
    Limpieza personalizada.
    """
    # Implementar lógica específica
    pass

# Registrar en el comando principal
def handle(self, *args, **options):
    cleanup_type = options['type']

    if cleanup_type == 'custom':
        self.cleanup_custom_type(options['dry_run'], options['tenant'])
```

### Hooks para Extensión
```python
def pre_cleanup_hook(self, document):
    """
    Hook ejecutado antes de eliminar documento.
    """
    # Permitir extensión por otras apps
    pass

def post_cleanup_hook(self, deleted_count):
    """
    Hook ejecutado después de limpieza.
    """
    # Permitir extensión por otras apps
    pass
```
